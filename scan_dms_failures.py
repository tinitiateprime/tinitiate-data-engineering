import sys
import re
import time
import traceback
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2 import sql

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


# ============================================================
# ARGUMENT HANDLING
# ============================================================

REQUIRED_ARGS = [
    "JOB_NAME",

    "BRONZE_HOST",
    "BRONZE_PORT",
    "BRONZE_DB",
    "BRONZE_USERNAME",
    "BRONZE_PASSWORD",

    "SILVER_HOST",
    "SILVER_PORT",
    "SILVER_DB",
    "SILVER_USERNAME",
    "SILVER_PASSWORD",

    "SOURCE_SCHEMA",
    "TARGET_SCHEMA",

    "CONTROL_SCHEMA",
    "DEFAULT_LOAD_STRATEGY",

    "TIMESTAMP_COLUMN_CANDIDATES",
]


OPTIONAL_DEFAULTS = {
    "ROLLING_WINDOW_DAYS": "5",
    "ACTIVE_FLAG_COLUMN": "bronze_record_active_flg",
    "ACTIVE_FLAG_Y": "Y",
    "ACTIVE_FLAG_N": "N",
    "ROW_HASH_COLUMN": "bronze_row_hash",

    "UPDATE_EXISTING_ROWS": "false",
    "VALIDATE_KEY_OVERRIDE": "false",
    "ENABLE_EXACT_COUNTS": "false",
    "ANALYZE_TEMP_TABLE": "true",

    "BUCKET_COUNT": "1",
    "BUCKET_ROW_THRESHOLD": "20000000",

    "EXCLUDE_TABLE_PATTERN": "%_BKP",

    "CONFIG_TABLE": "etl_table_config",
    "CONTROL_TABLE": "etl_load_control",

    # Optional: process one table only.
    "SOURCE_TABLE": "",

    # Optional configuration-table filter.
    "CONFIG_ENABLED_COLUMN": "enabled_flag",
    "CONFIG_SKIP_COLUMN": "skip_flag",
}


def get_optional_argument(name, default):
    argument_name = f"--{name}"

    if argument_name in sys.argv:
        index = sys.argv.index(argument_name)

        if index + 1 < len(sys.argv):
            return sys.argv[index + 1]

    return default


args = getResolvedOptions(sys.argv, REQUIRED_ARGS)

for optional_name, optional_default in OPTIONAL_DEFAULTS.items():
    args[optional_name] = get_optional_argument(
        optional_name,
        optional_default
    )


# ============================================================
# GLUE INITIALIZATION
# ============================================================

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# ============================================================
# CONFIGURATION
# ============================================================

JOB_NAME = args["JOB_NAME"]

BRONZE_HOST = args["BRONZE_HOST"]
BRONZE_PORT = int(args["BRONZE_PORT"])
BRONZE_DB = args["BRONZE_DB"]
BRONZE_USERNAME = args["BRONZE_USERNAME"]
BRONZE_PASSWORD = args["BRONZE_PASSWORD"]

SILVER_HOST = args["SILVER_HOST"]
SILVER_PORT = int(args["SILVER_PORT"])
SILVER_DB = args["SILVER_DB"]
SILVER_USERNAME = args["SILVER_USERNAME"]
SILVER_PASSWORD = args["SILVER_PASSWORD"]

SOURCE_SCHEMA = args["SOURCE_SCHEMA"]
TARGET_SCHEMA = args["TARGET_SCHEMA"]

CONTROL_SCHEMA = args["CONTROL_SCHEMA"]
CONFIG_TABLE = args["CONFIG_TABLE"]
CONTROL_TABLE = args["CONTROL_TABLE"]

DEFAULT_LOAD_STRATEGY = args["DEFAULT_LOAD_STRATEGY"].strip().upper()

ROLLING_WINDOW_DAYS = int(args["ROLLING_WINDOW_DAYS"])

ACTIVE_FLAG_COLUMN = args["ACTIVE_FLAG_COLUMN"]
ACTIVE_FLAG_Y = args["ACTIVE_FLAG_Y"]
ACTIVE_FLAG_N = args["ACTIVE_FLAG_N"]

ROW_HASH_COLUMN = args["ROW_HASH_COLUMN"]

UPDATE_EXISTING_ROWS = (
    args["UPDATE_EXISTING_ROWS"].strip().lower() == "true"
)

VALIDATE_KEY_OVERRIDE = (
    args["VALIDATE_KEY_OVERRIDE"].strip().lower() == "true"
)

ENABLE_EXACT_COUNTS = (
    args["ENABLE_EXACT_COUNTS"].strip().lower() == "true"
)

ANALYZE_TEMP_TABLE = (
    args["ANALYZE_TEMP_TABLE"].strip().lower() == "true"
)

BUCKET_COUNT = max(int(args["BUCKET_COUNT"]), 1)
BUCKET_ROW_THRESHOLD = int(args["BUCKET_ROW_THRESHOLD"])

EXCLUDE_TABLE_PATTERN = args["EXCLUDE_TABLE_PATTERN"]
SOURCE_TABLE_FILTER = args["SOURCE_TABLE"].strip()

TIMESTAMP_COLUMN_CANDIDATES = [
    item.strip()
    for item in args["TIMESTAMP_COLUMN_CANDIDATES"].split(",")
    if item.strip()
]

SUPPORTED_STRATEGIES = {
    "AUTO",
    "ROLLING_WINDOW_REPLACE",
    "SNAPSHOT_REPLACE",
    "UPSERT",
    "SYNC_WITH_FLAG",
}


BRONZE_JDBC_URL = (
    f"jdbc:postgresql://{BRONZE_HOST}:{BRONZE_PORT}/{BRONZE_DB}"
)

SILVER_JDBC_URL = (
    f"jdbc:postgresql://{SILVER_HOST}:{SILVER_PORT}/{SILVER_DB}"
)


BRONZE_JDBC_PROPERTIES = {
    "user": BRONZE_USERNAME,
    "password": BRONZE_PASSWORD,
    "driver": "org.postgresql.Driver",
    "fetchsize": "10000",
}

SILVER_JDBC_PROPERTIES = {
    "user": SILVER_USERNAME,
    "password": SILVER_PASSWORD,
    "driver": "org.postgresql.Driver",
    "batchsize": "10000",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def log(message):
    print(message, flush=True)


def quote_identifier(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def qualified_name(schema_name, table_name):
    return (
        f"{quote_identifier(schema_name)}."
        f"{quote_identifier(table_name)}"
    )


def safe_stage_table_name(table_name):
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", table_name)

    timestamp_part = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    return f"_glue_stage_{cleaned}_{timestamp_part}".lower()


def get_bronze_connection():
    return psycopg2.connect(
        host=BRONZE_HOST,
        port=BRONZE_PORT,
        dbname=BRONZE_DB,
        user=BRONZE_USERNAME,
        password=BRONZE_PASSWORD,
        connect_timeout=30,
    )


def get_silver_connection():
    return psycopg2.connect(
        host=SILVER_HOST,
        port=SILVER_PORT,
        dbname=SILVER_DB,
        user=SILVER_USERNAME,
        password=SILVER_PASSWORD,
        connect_timeout=30,
    )


def execute_query(connection, statement, parameters=None):
    with connection.cursor() as cursor:
        cursor.execute(statement, parameters)

        if cursor.description:
            return cursor.fetchall()

        return []


def execute_scalar(connection, statement, parameters=None):
    rows = execute_query(connection, statement, parameters)

    if not rows:
        return None

    return rows[0][0]


# ============================================================
# METADATA FUNCTIONS
# ============================================================

def get_source_tables():
    """
    Retrieves source tables.

    If SOURCE_TABLE parameter is supplied, only that table is returned.
    Otherwise, configuration table is checked first.

    Tables with skip_flag=true/Y/1 are not returned.
    """

    if SOURCE_TABLE_FILTER:
        return [
            {
                "source_schema": SOURCE_SCHEMA,
                "source_table": SOURCE_TABLE_FILTER,
                "target_schema": TARGET_SCHEMA,
                "target_table": SOURCE_TABLE_FILTER,
                "load_strategy": DEFAULT_LOAD_STRATEGY,
                "primary_keys": [],
                "timestamp_column": None,
            }
        ]

    configured_tables = read_table_config()

    if configured_tables:
        return configured_tables

    log(
        "[FRAMEWORK] No enabled configuration rows found. "
        "Reading tables from information_schema."
    )

    connection = get_bronze_connection()

    try:
        query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE upper(table_schema) = upper(%s)
              AND table_type = 'BASE TABLE'
              AND table_name NOT LIKE %s
            ORDER BY table_name
        """

        rows = execute_query(
            connection,
            query,
            (SOURCE_SCHEMA, EXCLUDE_TABLE_PATTERN),
        )

        return [
            {
                "source_schema": row[0],
                "source_table": row[1],
                "target_schema": TARGET_SCHEMA,
                "target_table": row[1],
                "load_strategy": DEFAULT_LOAD_STRATEGY,
                "primary_keys": [],
                "timestamp_column": None,
            }
            for row in rows
        ]

    finally:
        connection.close()


def read_table_config():
    """
    Expected configuration-table columns:

        source_schema
        source_table
        target_schema
        target_table
        load_strategy
        primary_key_columns
        timestamp_column
        enabled_flag
        skip_flag

    primary_key_columns should contain comma-separated columns, for example:

        TASK_ID,EMPL_ID

    Modify the SQL below if your configuration table has different columns.
    """

    connection = get_silver_connection()

    try:
        config_qualified_name = qualified_name(
            CONTROL_SCHEMA,
            CONFIG_TABLE
        )

        query = f"""
            SELECT
                source_schema,
                source_table,
                COALESCE(target_schema, source_schema) AS target_schema,
                COALESCE(target_table, source_table) AS target_table,
                COALESCE(load_strategy, %s) AS load_strategy,
                COALESCE(primary_key_columns, '') AS primary_key_columns,
                NULLIF(TRIM(timestamp_column), '') AS timestamp_column
            FROM {config_qualified_name}
            WHERE upper(source_schema) = upper(%s)
              AND COALESCE(enabled_flag, 'Y') IN ('Y', 'y', 'TRUE', 'true', '1')
              AND COALESCE(skip_flag, 'N') NOT IN ('Y', 'y', 'TRUE', 'true', '1')
            ORDER BY source_table
        """

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    DEFAULT_LOAD_STRATEGY,
                    SOURCE_SCHEMA,
                ),
            )

            rows = cursor.fetchall()

        result = []

        for row in rows:
            primary_keys = [
                key.strip()
                for key in (row[5] or "").split(",")
                if key.strip()
            ]

            result.append(
                {
                    "source_schema": row[0],
                    "source_table": row[1],
                    "target_schema": row[2],
                    "target_table": row[3],
                    "load_strategy": (row[4] or DEFAULT_LOAD_STRATEGY).upper(),
                    "primary_keys": primary_keys,
                    "timestamp_column": row[6],
                }
            )

        return result

    except Exception as exc:
        log(
            "[FRAMEWORK] Configuration table could not be read. "
            f"Falling back to information_schema. Error={exc}"
        )

        connection.rollback()
        return []

    finally:
        connection.close()


def get_table_columns(
    connection,
    schema_name,
    table_name
):
    query = """
        SELECT
            column_name,
            data_type,
            ordinal_position
        FROM information_schema.columns
        WHERE upper(table_schema) = upper(%s)
          AND upper(table_name) = upper(%s)
        ORDER BY ordinal_position
    """

    rows = execute_query(
        connection,
        query,
        (schema_name, table_name),
    )

    return [
        {
            "column_name": row[0],
            "data_type": row[1],
            "ordinal_position": row[2],
        }
        for row in rows
    ]


def get_primary_keys(
    connection,
    schema_name,
    table_name
):
    query = """
        SELECT
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.constraint_schema = kcu.constraint_schema
         AND tc.table_schema = kcu.table_schema
         AND tc.table_name = kcu.table_name
        WHERE upper(tc.table_schema) = upper(%s)
          AND upper(tc.table_name) = upper(%s)
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
    """

    rows = execute_query(
        connection,
        query,
        (schema_name, table_name),
    )

    return [row[0] for row in rows]


def detect_timestamp_column(
    source_columns,
    configured_timestamp_column=None
):
    """
    Case-insensitive timestamp detection.

    This correctly matches:

        TIME_STAMP
        time_stamp
        Time_Stamp
    """

    actual_columns = {
        item["column_name"].strip().upper(): item["column_name"]
        for item in source_columns
    }

    candidates = []

    if configured_timestamp_column:
        candidates.append(configured_timestamp_column)

    candidates.extend(TIMESTAMP_COLUMN_CANDIDATES)

    # Additional safe defaults.
    candidates.extend(
        [
            "TIME_STAMP",
            "TIMESTAMP",
            "UPDATED_AT",
            "UPDATE_TIMESTAMP",
            "MODIFIED_AT",
            "MODIFIED_DATE",
            "LAST_UPDATED_AT",
            "LAST_UPDATE_DATE",
            "INGESTED_AT",
            "CREATED_AT",
        ]
    )

    deduplicated_candidates = []

    seen = set()

    for candidate in candidates:
        normalized = candidate.strip().upper()

        if normalized and normalized not in seen:
            seen.add(normalized)
            deduplicated_candidates.append(normalized)

    for candidate in deduplicated_candidates:
        if candidate in actual_columns:
            return actual_columns[candidate]

    return None


def table_exists(
    connection,
    schema_name,
    table_name
):
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE upper(table_schema) = upper(%s)
              AND upper(table_name) = upper(%s)
        )
    """

    return bool(
        execute_scalar(
            connection,
            query,
            (schema_name, table_name),
        )
    )


# ============================================================
# CONTROL TABLE LOGGING
# ============================================================

def insert_control_start(
    source_schema,
    source_table,
    target_schema,
    target_table,
    load_strategy
):
    connection = get_silver_connection()

    try:
        control_name = qualified_name(
            CONTROL_SCHEMA,
            CONTROL_TABLE
        )

        query = f"""
            INSERT INTO {control_name}
            (
                job_name,
                source_schema,
                source_table,
                target_schema,
                target_table,
                load_strategy,
                status,
                start_datetime,
                bronze_count,
                silver_count,
                rows_processed,
                error_count,
                message
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                'RUNNING',
                CURRENT_TIMESTAMP,
                NULL,
                NULL,
                0,
                0,
                %s
            )
            RETURNING id
        """

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    JOB_NAME,
                    source_schema,
                    source_table,
                    target_schema,
                    target_table,
                    load_strategy,
                    "Table processing started",
                ),
            )

            control_id = cursor.fetchone()[0]

        connection.commit()
        return control_id

    except Exception as exc:
        connection.rollback()

        log(
            f"[CONTROL] Unable to insert RUNNING record: {exc}"
        )

        return None

    finally:
        connection.close()


def update_control_end(
    control_id,
    status,
    bronze_count,
    silver_count,
    rows_processed,
    error_count,
    message
):
    if control_id is None:
        return

    connection = get_silver_connection()

    try:
        control_name = qualified_name(
            CONTROL_SCHEMA,
            CONTROL_TABLE
        )

        query = f"""
            UPDATE {control_name}
            SET
                status = %s,
                end_datetime = CURRENT_TIMESTAMP,
                bronze_count = %s,
                silver_count = %s,
                rows_processed = %s,
                error_count = %s,
                message = %s
            WHERE id = %s
        """

        execute_query(
            connection,
            query,
            (
                status,
                bronze_count,
                silver_count,
                rows_processed,
                error_count,
                message[:10000],
                control_id,
            ),
        )

        connection.commit()

    except Exception as exc:
        connection.rollback()

        log(
            f"[CONTROL] Unable to update control record "
            f"{control_id}: {exc}"
        )

    finally:
        connection.close()


# ============================================================
# SPARK JDBC READ/WRITE
# ============================================================

def build_source_query(
    source_schema,
    source_table,
    timestamp_column=None,
    window_start=None
):
    table_name = qualified_name(
        source_schema,
        source_table
    )

    if timestamp_column and window_start:
        timestamp_literal = window_start.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return f"""
            (
                SELECT *
                FROM {table_name}
                WHERE {quote_identifier(timestamp_column)}
                      >= TIMESTAMP '{timestamp_literal}'
            ) AS source_data
        """

    return f"""
        (
            SELECT *
            FROM {table_name}
        ) AS source_data
    """


def read_source_dataframe(
    source_schema,
    source_table,
    timestamp_column=None,
    window_start=None
):
    dbtable = build_source_query(
        source_schema=source_schema,
        source_table=source_table,
        timestamp_column=timestamp_column,
        window_start=window_start,
    )

    log(
        f"[{source_table}] Reading source through JDBC. "
        f"timestamp_column={timestamp_column}, "
        f"window_start={window_start}"
    )

    dataframe = (
        spark.read
        .format("jdbc")
        .option("url", BRONZE_JDBC_URL)
        .option("dbtable", dbtable)
        .option("user", BRONZE_USERNAME)
        .option("password", BRONZE_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .option("fetchsize", "10000")
        .load()
    )

    return dataframe


def write_stage_dataframe(
    dataframe,
    stage_schema,
    stage_table
):
    full_stage_name = (
        f"{quote_identifier(stage_schema)}."
        f"{quote_identifier(stage_table)}"
    )

    writer = (
        dataframe.write
        .format("jdbc")
        .option("url", SILVER_JDBC_URL)
        .option("dbtable", full_stage_name)
        .option("user", SILVER_USERNAME)
        .option("password", SILVER_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .option("batchsize", "10000")
        .mode("overwrite")
    )

    writer.save()


# ============================================================
# LOAD OPERATIONS
# ============================================================

def ensure_target_schema(connection, target_schema):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                sql.Identifier(target_schema)
            )
        )


def analyze_table(
    connection,
    schema_name,
    table_name
):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("ANALYZE {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )


def drop_table_if_exists(
    connection,
    schema_name,
    table_name
):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )


def get_common_columns(
    connection,
    source_schema,
    source_table,
    target_schema,
    target_table
):
    source_columns = get_table_columns(
        get_bronze_connection_for_metadata(),
        source_schema,
        source_table
    )

    target_columns = get_table_columns(
        connection,
        target_schema,
        target_table
    )

    source_map = {
        item["column_name"].upper(): item["column_name"]
        for item in source_columns
    }

    target_map = {
        item["column_name"].upper(): item["column_name"]
        for item in target_columns
    }

    common = []

    for normalized_name, source_name in source_map.items():
        if normalized_name in target_map:
            common.append(
                (
                    source_name,
                    target_map[normalized_name],
                )
            )

    return common


def get_bronze_connection_for_metadata():
    """
    Kept as a separate helper to make connection ownership obvious.
    Caller must close the returned connection.
    """
    return get_bronze_connection()


def snapshot_replace(
    dataframe,
    target_schema,
    target_table
):
    stage_table = safe_stage_table_name(target_table)

    write_stage_dataframe(
        dataframe,
        target_schema,
        stage_table
    )

    connection = get_silver_connection()

    try:
        connection.autocommit = False

        ensure_target_schema(
            connection,
            target_schema
        )

        if ANALYZE_TEMP_TABLE:
            analyze_table(
                connection,
                target_schema,
                stage_table
            )

        target_exists = table_exists(
            connection,
            target_schema,
            target_table
        )

        with connection.cursor() as cursor:
            if target_exists:
                cursor.execute(
                    sql.SQL("TRUNCATE TABLE {}.{}").format(
                        sql.Identifier(target_schema),
                        sql.Identifier(target_table),
                    )
                )

                target_columns = get_table_columns(
                    connection,
                    target_schema,
                    target_table
                )

                stage_columns = get_table_columns(
                    connection,
                    target_schema,
                    stage_table
                )

                target_map = {
                    item["column_name"].upper(): item["column_name"]
                    for item in target_columns
                }

                stage_map = {
                    item["column_name"].upper(): item["column_name"]
                    for item in stage_columns
                }

                common_normalized = [
                    name
                    for name in target_map
                    if name in stage_map
                ]

                if not common_normalized:
                    raise RuntimeError(
                        "No common columns found between stage and target"
                    )

                target_identifier_list = sql.SQL(", ").join(
                    [
                        sql.Identifier(target_map[name])
                        for name in common_normalized
                    ]
                )

                stage_identifier_list = sql.SQL(", ").join(
                    [
                        sql.Identifier(stage_map[name])
                        for name in common_normalized
                    ]
                )

                insert_statement = sql.SQL("""
                    INSERT INTO {}.{} ({})
                    SELECT {}
                    FROM {}.{}
                """).format(
                    sql.Identifier(target_schema),
                    sql.Identifier(target_table),
                    target_identifier_list,
                    stage_identifier_list,
                    sql.Identifier(target_schema),
                    sql.Identifier(stage_table),
                )

                cursor.execute(insert_statement)

            else:
                cursor.execute(
                    sql.SQL("""
                        ALTER TABLE {}.{}
                        RENAME TO {}
                    """).format(
                        sql.Identifier(target_schema),
                        sql.Identifier(stage_table),
                        sql.Identifier(target_table),
                    )
                )

                stage_table = None

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if stage_table:
            try:
                drop_table_if_exists(
                    connection,
                    target_schema,
                    stage_table
                )
                connection.commit()
            except Exception:
                connection.rollback()

        connection.close()


def rolling_window_replace(
    dataframe,
    target_schema,
    target_table,
    timestamp_column,
    window_start
):
    stage_table = safe_stage_table_name(target_table)

    write_stage_dataframe(
        dataframe,
        target_schema,
        stage_table
    )

    connection = get_silver_connection()

    try:
        connection.autocommit = False

        ensure_target_schema(
            connection,
            target_schema
        )

        if ANALYZE_TEMP_TABLE:
            analyze_table(
                connection,
                target_schema,
                stage_table
            )

        target_exists = table_exists(
            connection,
            target_schema,
            target_table
        )

        with connection.cursor() as cursor:
            if not target_exists:
                cursor.execute(
                    sql.SQL("""
                        ALTER TABLE {}.{}
                        RENAME TO {}
                    """).format(
                        sql.Identifier(target_schema),
                        sql.Identifier(stage_table),
                        sql.Identifier(target_table),
                    )
                )

                stage_table = None

            else:
                target_columns = get_table_columns(
                    connection,
                    target_schema,
                    target_table
                )

                stage_columns = get_table_columns(
                    connection,
                    target_schema,
                    stage_table
                )

                target_map = {
                    item["column_name"].upper(): item["column_name"]
                    for item in target_columns
                }

                stage_map = {
                    item["column_name"].upper(): item["column_name"]
                    for item in stage_columns
                }

                timestamp_normalized = timestamp_column.upper()

                if timestamp_normalized not in target_map:
                    raise RuntimeError(
                        f"Timestamp column {timestamp_column} "
                        f"does not exist in target table "
                        f"{target_schema}.{target_table}"
                    )

                common_normalized = [
                    name
                    for name in target_map
                    if name in stage_map
                ]

                if not common_normalized:
                    raise RuntimeError(
                        "No common columns found between stage and target"
                    )

                cursor.execute(
                    sql.SQL("""
                        DELETE FROM {}.{}
                        WHERE {} >= %s
                    """).format(
                        sql.Identifier(target_schema),
                        sql.Identifier(target_table),
                        sql.Identifier(
                            target_map[timestamp_normalized]
                        ),
                    ),
                    (window_start,),
                )

                target_identifier_list = sql.SQL(", ").join(
                    [
                        sql.Identifier(target_map[name])
                        for name in common_normalized
                    ]
                )

                stage_identifier_list = sql.SQL(", ").join(
                    [
                        sql.Identifier(stage_map[name])
                        for name in common_normalized
                    ]
                )

                cursor.execute(
                    sql.SQL("""
                        INSERT INTO {}.{} ({})
                        SELECT {}
                        FROM {}.{}
                    """).format(
                        sql.Identifier(target_schema),
                        sql.Identifier(target_table),
                        target_identifier_list,
                        stage_identifier_list,
                        sql.Identifier(target_schema),
                        sql.Identifier(stage_table),
                    )
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if stage_table:
            try:
                drop_table_if_exists(
                    connection,
                    target_schema,
                    stage_table
                )

                connection.commit()

            except Exception:
                connection.rollback()

        connection.close()


# ============================================================
# COUNT FUNCTIONS
# ============================================================

def get_source_count(
    source_schema,
    source_table,
    timestamp_column=None,
    window_start=None
):
    table_name = qualified_name(
        source_schema,
        source_table
    )

    connection = get_bronze_connection()

    try:
        if timestamp_column and window_start:
            query = f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE {quote_identifier(timestamp_column)} >= %s
            """

            return int(
                execute_scalar(
                    connection,
                    query,
                    (window_start,),
                )
                or 0
            )

        query = f"""
            SELECT COUNT(*)
            FROM {table_name}
        """

        return int(
            execute_scalar(connection, query) or 0
        )

    finally:
        connection.close()


def get_target_count(
    target_schema,
    target_table
):
    connection = get_silver_connection()

    try:
        if not table_exists(
            connection,
            target_schema,
            target_table
        ):
            return 0

        query = f"""
            SELECT COUNT(*)
            FROM {qualified_name(target_schema, target_table)}
        """

        return int(
            execute_scalar(connection, query) or 0
        )

    finally:
        connection.close()


# ============================================================
# STRATEGY RESOLUTION
# ============================================================

def resolve_strategy(
    requested_strategy,
    timestamp_column,
    primary_keys
):
    strategy = requested_strategy.strip().upper()

    if strategy not in SUPPORTED_STRATEGIES:
        raise ValueError(
            f"Unsupported load_strategy={strategy}. "
            f"Expected one of: "
            f"{', '.join(sorted(SUPPORTED_STRATEGIES))}"
        )

    if strategy == "AUTO":
        if timestamp_column:
            return "ROLLING_WINDOW_REPLACE"

        return "SNAPSHOT_REPLACE"

    if (
        strategy == "ROLLING_WINDOW_REPLACE"
        and not timestamp_column
    ):
        return "SNAPSHOT_REPLACE"

    if strategy == "UPSERT" and not primary_keys:
        raise ValueError(
            "UPSERT requires primary key columns"
        )

    return strategy


# ============================================================
# TABLE PROCESSING
# ============================================================

def process_table(table_config):
    source_schema = table_config["source_schema"]
    source_table = table_config["source_table"]

    target_schema = table_config["target_schema"]
    target_table = table_config["target_table"]

    requested_strategy = (
        table_config.get("load_strategy")
        or DEFAULT_LOAD_STRATEGY
    ).upper()

    configured_keys = table_config.get("primary_keys") or []

    configured_timestamp = table_config.get(
        "timestamp_column"
    )

    control_id = None

    bronze_count = None
    silver_count = None
    rows_processed = 0

    start_time = time.time()

    log("=" * 90)

    log(
        f"Processing "
        f"{source_schema}.{source_table} -> "
        f"{target_schema}.{target_table}"
    )

    try:
        bronze_connection = get_bronze_connection()

        try:
            source_columns = get_table_columns(
                bronze_connection,
                source_schema,
                source_table
            )

            if not source_columns:
                raise RuntimeError(
                    f"Source table not found or has no columns: "
                    f"{source_schema}.{source_table}"
                )

            discovered_keys = get_primary_keys(
                bronze_connection,
                source_schema,
                source_table
            )

        finally:
            bronze_connection.close()

        primary_keys = (
            configured_keys
            if configured_keys
            else discovered_keys
        )

        timestamp_column = detect_timestamp_column(
            source_columns=source_columns,
            configured_timestamp_column=configured_timestamp,
        )

        available_column_names = [
            item["column_name"]
            for item in source_columns
        ]

        log(
            f"[{source_table}] "
            f"Available columns={available_column_names}"
        )

        log(
            f"[{source_table}] "
            f"Timestamp candidates="
            f"{TIMESTAMP_COLUMN_CANDIDATES}"
        )

        log(
            f"[{source_table}] "
            f"Configured timestamp="
            f"{configured_timestamp}"
        )

        log(
            f"[{source_table}] "
            f"Detected timestamp column="
            f"{timestamp_column}"
        )

        resolved_strategy = resolve_strategy(
            requested_strategy=requested_strategy,
            timestamp_column=timestamp_column,
            primary_keys=primary_keys,
        )

        log(
            f"[{source_table}] "
            f"requested_strategy={requested_strategy}, "
            f"resolved_strategy={resolved_strategy}, "
            f"primary_keys="
            f"{','.join(primary_keys) if primary_keys else 'NONE'}"
        )

        control_id = insert_control_start(
            source_schema=source_schema,
            source_table=source_table,
            target_schema=target_schema,
            target_table=target_table,
            load_strategy=resolved_strategy,
        )

        window_start = None

        if resolved_strategy == "ROLLING_WINDOW_REPLACE":
            if not timestamp_column:
                log(
                    f"[{source_table}] "
                    "No timestamp column found; "
                    "starting atomic SNAPSHOT_REPLACE."
                )

                resolved_strategy = "SNAPSHOT_REPLACE"

            else:
                window_start = (
                    datetime.now(timezone.utc)
                    - timedelta(days=ROLLING_WINDOW_DAYS)
                ).replace(tzinfo=None)

                log(
                    f"[{source_table}] "
                    f"Using timestamp column={timestamp_column}; "
                    f"window_start={window_start}; "
                    f"rolling_days={ROLLING_WINDOW_DAYS}"
                )

        dataframe = read_source_dataframe(
            source_schema=source_schema,
            source_table=source_table,
            timestamp_column=(
                timestamp_column
                if resolved_strategy
                == "ROLLING_WINDOW_REPLACE"
                else None
            ),
            window_start=(
                window_start
                if resolved_strategy
                == "ROLLING_WINDOW_REPLACE"
                else None
            ),
        )

        if ENABLE_EXACT_COUNTS:
            bronze_count = dataframe.count()
        else:
            # rows_processed still requires a Spark action.
            bronze_count = dataframe.count()

        rows_processed = bronze_count

        log(
            f"[{source_table}] "
            f"Rows selected from Bronze={bronze_count}"
        )

        if resolved_strategy == "ROLLING_WINDOW_REPLACE":
            rolling_window_replace(
                dataframe=dataframe,
                target_schema=target_schema,
                target_table=target_table,
                timestamp_column=timestamp_column,
                window_start=window_start,
            )

        elif resolved_strategy == "SNAPSHOT_REPLACE":
            log(
                f"[{source_table}] "
                "Starting atomic SNAPSHOT_REPLACE."
            )

            snapshot_replace(
                dataframe=dataframe,
                target_schema=target_schema,
                target_table=target_table,
            )

        else:
            raise NotImplementedError(
                f"Strategy {resolved_strategy} is recognized "
                "but is not implemented in this version. "
                "Use AUTO, ROLLING_WINDOW_REPLACE, "
                "or SNAPSHOT_REPLACE."
            )

        silver_count = get_target_count(
            target_schema,
            target_table
        )

        elapsed_seconds = round(
            time.time() - start_time,
            2
        )

        message = (
            f"{resolved_strategy} completed in "
            f"{elapsed_seconds} seconds. "
            f"timestamp_column={timestamp_column}; "
            f"window_start={window_start}"
        )

        update_control_end(
            control_id=control_id,
            status="SUCCESS",
            bronze_count=bronze_count,
            silver_count=silver_count,
            rows_processed=rows_processed,
            error_count=0,
            message=message,
        )

        log(
            f"[{source_table}] "
            f"{resolved_strategy} completed in "
            f"{elapsed_seconds} seconds."
        )

        log(
            f"[{source_table}] "
            f"status=SUCCESS, "
            f"bronze_count={bronze_count}, "
            f"silver_count={silver_count}, "
            f"rows_processed={rows_processed}, "
            f"error_count=0"
        )

        return {
            "table": source_table,
            "status": "SUCCESS",
            "strategy": resolved_strategy,
            "bronze_count": bronze_count,
            "silver_count": silver_count,
        }

    except Exception as exc:
        elapsed_seconds = round(
            time.time() - start_time,
            2
        )

        error_message = (
            f"{type(exc).__name__}: {exc}\n"
            f"{traceback.format_exc()}"
        )

        update_control_end(
            control_id=control_id,
            status="FAILED",
            bronze_count=bronze_count,
            silver_count=silver_count,
            rows_processed=rows_processed,
            error_count=1,
            message=error_message,
        )

        log(
            f"[{source_table}] "
            f"status=FAILED after "
            f"{elapsed_seconds} seconds"
        )

        log(error_message)

        # Continue with the next table.
        return {
            "table": source_table,
            "status": "FAILED",
            "error": str(exc),
        }


# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 90)

    log(
        f"[FRAMEWORK] Job={JOB_NAME}, "
        f"source_schema={SOURCE_SCHEMA}, "
        f"target_schema={TARGET_SCHEMA}"
    )

    log(
        f"[FRAMEWORK] "
        f"default_strategy={DEFAULT_LOAD_STRATEGY}, "
        f"rolling_window_days={ROLLING_WINDOW_DAYS}"
    )

    log(
        f"[FRAMEWORK] "
        f"timestamp_candidates="
        f"{TIMESTAMP_COLUMN_CANDIDATES}"
    )

    tables = get_source_tables()

    log(
        f"[FRAMEWORK] Tables selected={len(tables)}"
    )

    results = []

    for table_config in tables:
        result = process_table(table_config)
        results.append(result)

    success_count = sum(
        1
        for result in results
        if result["status"] == "SUCCESS"
    )

    failure_count = sum(
        1
        for result in results
        if result["status"] == "FAILED"
    )

    log("=" * 90)

    log(
        f"[FRAMEWORK] Completed. "
        f"success={success_count}, "
        f"failed={failure_count}, "
        f"total={len(results)}"
    )

    if failure_count:
        failed_tables = [
            result["table"]
            for result in results
            if result["status"] == "FAILED"
        ]

        log(
            f"[FRAMEWORK] Failed tables="
            f"{failed_tables}"
        )


try:
    main()
    job.commit()

except Exception:
    log(
        "[FRAMEWORK] Fatal framework error:\n"
        + traceback.format_exc()
    )
    raise
