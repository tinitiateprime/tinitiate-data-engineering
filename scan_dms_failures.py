import os
import uuid
import tempfile
import traceback
from datetime import datetime, timezone

import psycopg2
from psycopg2 import sql


###############################################################################
# CONFIGURATION
###############################################################################

# Bronze PostgreSQL
BRONZE_HOST = os.getenv(
    "BRONZE_HOST",
    "gsapdi-pg-stg.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com",
)
BRONZE_PORT = int(os.getenv("BRONZE_PORT", "5432"))
BRONZE_DB = os.getenv("BRONZE_DB", "gsapdi")
BRONZE_USER = os.getenv("BRONZE_USERNAME", "<BRONZE_USERNAME>")
BRONZE_PASSWORD = os.getenv("BRONZE_PASSWORD", "<BRONZE_PASSWORD>")

# Silver PostgreSQL
SILVER_HOST = os.getenv(
    "SILVER_HOST",
    "gsapdi-pg-mt-dm-dev.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com",
)
SILVER_PORT = int(os.getenv("SILVER_PORT", "5432"))
SILVER_DB = os.getenv("SILVER_DB", "mtdm")
SILVER_USER = os.getenv("SILVER_USERNAME", "<SILVER_USERNAME>")
SILVER_PASSWORD = os.getenv("SILVER_PASSWORD", "<SILVER_PASSWORD>")

# Framework settings
SOURCE_SCHEMA = os.getenv("SOURCE_SCHEMA", "CLM")
TARGET_SCHEMA = os.getenv("TARGET_SCHEMA", "CLM")
CONTROL_SCHEMA = os.getenv("CONTROL_SCHEMA", "etl_control")
JOB_NAME = os.getenv("JOB_NAME", "clm_bronze_to_silver_framework")
RUN_ID = uuid.uuid4().hex

# Optional comma-separated controls.
# Empty INCLUDE_TABLES means discover all base tables under SOURCE_SCHEMA.
INCLUDE_TABLES = {
    item.strip()
    for item in os.getenv("INCLUDE_TABLES", "").split(",")
    if item.strip()
}
EXCLUDE_TABLES = {
    item.strip()
    for item in os.getenv("EXCLUDE_TABLES", "").split(",")
    if item.strip()
}


###############################################################################
# DATABASE CONNECTIONS
###############################################################################

def connect_bronze():
    return psycopg2.connect(
        host=BRONZE_HOST,
        port=BRONZE_PORT,
        dbname=BRONZE_DB,
        user=BRONZE_USER,
        password=BRONZE_PASSWORD,
        connect_timeout=30,
        application_name=JOB_NAME,
    )


def connect_silver():
    return psycopg2.connect(
        host=SILVER_HOST,
        port=SILVER_PORT,
        dbname=SILVER_DB,
        user=SILVER_USER,
        password=SILVER_PASSWORD,
        connect_timeout=30,
        application_name=JOB_NAME,
    )


###############################################################################
# FRAMEWORK TABLES
###############################################################################

def create_framework_tables(silver_conn):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
            .format(sql.Identifier(CONTROL_SCHEMA))
        )

        # Optional metadata-driven configuration.
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.etl_table_config
                (
                    config_id              bigserial PRIMARY KEY,
                    source_schema          varchar(255) NOT NULL,
                    source_table           varchar(255) NOT NULL,
                    target_schema          varchar(255) NOT NULL,
                    target_table           varchar(255) NOT NULL,
                    enabled                boolean NOT NULL DEFAULT true,
                    primary_key_override   text,
                    load_order             integer NOT NULL DEFAULT 100,
                    created_datetime       timestamptz NOT NULL
                                           DEFAULT CURRENT_TIMESTAMP,
                    updated_datetime       timestamptz NOT NULL
                                           DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (source_schema, source_table)
                )
                """
            ).format(sql.Identifier(CONTROL_SCHEMA))
        )

        # One record per table per framework run.
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.etl_load_control
                (
                    control_id              bigserial PRIMARY KEY,
                    run_id                  varchar(64) NOT NULL,
                    job_name                varchar(255) NOT NULL,
                    source_schema           varchar(255) NOT NULL,
                    source_table            varchar(255) NOT NULL,
                    target_schema           varchar(255) NOT NULL,
                    target_table            varchar(255) NOT NULL,
                    bronze_count            bigint,
                    silver_count            bigint,
                    rows_processed          bigint,
                    status                  varchar(40) NOT NULL,
                    schema_review_required  boolean NOT NULL DEFAULT false,
                    start_datetime          timestamptz NOT NULL,
                    end_datetime            timestamptz NOT NULL,
                    error_count             integer NOT NULL DEFAULT 0,
                    message                 text
                )
                """
            ).format(sql.Identifier(CONTROL_SCHEMA))
        )

        cur.execute(
            sql.SQL(
                """
                CREATE INDEX IF NOT EXISTS idx_etl_load_control_daily
                ON {}.etl_load_control
                (source_table, start_datetime)
                """
            ).format(sql.Identifier(CONTROL_SCHEMA))
        )

        # Processing failures.
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.etl_error_log
                (
                    error_id          bigserial PRIMARY KEY,
                    run_id            varchar(64) NOT NULL,
                    job_name          varchar(255) NOT NULL,
                    source_schema     varchar(255),
                    source_table      varchar(255),
                    target_schema     varchar(255),
                    target_table      varchar(255),
                    error_step        varchar(100) NOT NULL,
                    severity          varchar(20) NOT NULL DEFAULT 'ERROR',
                    column_name       varchar(255),
                    source_datatype   text,
                    target_datatype   text,
                    error_message     text,
                    error_detail      text,
                    error_datetime    timestamptz NOT NULL
                                      DEFAULT CURRENT_TIMESTAMP
                )
                """
            ).format(sql.Identifier(CONTROL_SCHEMA))
        )

        # Developer review queue for risky schema changes.
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.etl_schema_change_review
                (
                    review_id            bigserial PRIMARY KEY,
                    run_id               varchar(64) NOT NULL,
                    source_schema        varchar(255) NOT NULL,
                    source_table         varchar(255) NOT NULL,
                    target_schema        varchar(255) NOT NULL,
                    target_table         varchar(255) NOT NULL,
                    column_name          varchar(255) NOT NULL,
                    source_datatype      text NOT NULL,
                    target_datatype      text,
                    change_type          varchar(50) NOT NULL,
                    reason               text,
                    review_status        varchar(30) NOT NULL DEFAULT 'PENDING',
                    reviewed_by          varchar(255),
                    review_notes         text,
                    detected_datetime    timestamptz NOT NULL
                                         DEFAULT CURRENT_TIMESTAMP,
                    reviewed_datetime    timestamptz,
                    implemented_datetime timestamptz
                )
                """
            ).format(sql.Identifier(CONTROL_SCHEMA))
        )

    silver_conn.commit()


###############################################################################
# AUDIT HELPERS
###############################################################################

def log_error(
    silver_conn,
    source_table,
    target_table,
    error_step,
    error_message,
    severity="ERROR",
    error_detail=None,
    column_name=None,
    source_datatype=None,
    target_datatype=None,
):
    try:
        with silver_conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    INSERT INTO {}.etl_error_log
                    (
                        run_id,
                        job_name,
                        source_schema,
                        source_table,
                        target_schema,
                        target_table,
                        error_step,
                        severity,
                        column_name,
                        source_datatype,
                        target_datatype,
                        error_message,
                        error_detail
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s)
                    """
                ).format(sql.Identifier(CONTROL_SCHEMA)),
                (
                    RUN_ID,
                    JOB_NAME,
                    SOURCE_SCHEMA,
                    source_table,
                    TARGET_SCHEMA,
                    target_table,
                    error_step,
                    severity,
                    column_name,
                    source_datatype,
                    target_datatype,
                    error_message,
                    error_detail,
                ),
            )
        silver_conn.commit()
    except Exception as audit_error:
        silver_conn.rollback()
        print(f"WARNING: Error-table insert failed: {audit_error}")


def log_schema_review(
    silver_conn,
    source_table,
    target_table,
    column_name,
    source_type,
    target_type,
    change_type,
    reason,
):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.etl_schema_change_review
                (
                    run_id,
                    source_schema,
                    source_table,
                    target_schema,
                    target_table,
                    column_name,
                    source_datatype,
                    target_datatype,
                    change_type,
                    reason,
                    review_status
                )
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
                """
            ).format(sql.Identifier(CONTROL_SCHEMA)),
            (
                RUN_ID,
                SOURCE_SCHEMA,
                source_table,
                TARGET_SCHEMA,
                target_table,
                column_name,
                source_type,
                target_type,
                change_type,
                reason,
            ),
        )
    silver_conn.commit()


def write_control_record(
    silver_conn,
    source_table,
    target_table,
    bronze_count,
    silver_count,
    rows_processed,
    status,
    schema_review_required,
    start_datetime,
    end_datetime,
    error_count,
    message,
):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.etl_load_control
                (
                    run_id,
                    job_name,
                    source_schema,
                    source_table,
                    target_schema,
                    target_table,
                    bronze_count,
                    silver_count,
                    rows_processed,
                    status,
                    schema_review_required,
                    start_datetime,
                    end_datetime,
                    error_count,
                    message
                )
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s)
                """
            ).format(sql.Identifier(CONTROL_SCHEMA)),
            (
                RUN_ID,
                JOB_NAME,
                SOURCE_SCHEMA,
                source_table,
                TARGET_SCHEMA,
                target_table,
                bronze_count,
                silver_count,
                rows_processed,
                status,
                schema_review_required,
                start_datetime,
                end_datetime,
                error_count,
                message,
            ),
        )
    silver_conn.commit()


###############################################################################
# METADATA HELPERS
###############################################################################

def discover_source_tables(bronze_conn):
    with bronze_conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (SOURCE_SCHEMA,),
        )
        tables = [row[0] for row in cur.fetchall()]

    if INCLUDE_TABLES:
        tables = [table for table in tables if table in INCLUDE_TABLES]

    if EXCLUDE_TABLES:
        tables = [table for table in tables if table not in EXCLUDE_TABLES]

    return tables


def get_enabled_config(silver_conn):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT
                    source_table,
                    target_table,
                    primary_key_override
                FROM {}.etl_table_config
                WHERE source_schema = %s
                  AND target_schema = %s
                  AND enabled = true
                ORDER BY load_order, source_table
                """
            ).format(sql.Identifier(CONTROL_SCHEMA)),
            (SOURCE_SCHEMA, TARGET_SCHEMA),
        )

        return {
            row[0]: {
                "target_table": row[1],
                "primary_key_override": row[2],
            }
            for row in cur.fetchall()
        }


def table_exists(conn, schema_name, table_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
            )
            """,
            (schema_name, table_name),
        )
        return cur.fetchone()[0]


def get_table_columns(conn, schema_name, table_name):
    """
    Uses pg_catalog.format_type so varchar lengths, numeric precision/scale,
    arrays, timestamps and PostgreSQL-specific types are retained.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                a.attname,
                pg_catalog.format_type(a.atttypid, a.atttypmod),
                a.attnotnull,
                a.attnum
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c
              ON c.oid = a.attrelid
            JOIN pg_catalog.pg_namespace n
              ON n.oid = c.relnamespace
            WHERE n.nspname = %s
              AND c.relname = %s
              AND c.relkind IN ('r', 'p')
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
            """,
            (schema_name, table_name),
        )

        return [
            {
                "name": row[0],
                "type": row[1],
                "not_null": row[2],
                "position": row[3],
            }
            for row in cur.fetchall()
        ]


def get_primary_keys(conn, schema_name, table_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_class c
              ON c.oid = i.indrelid
            JOIN pg_namespace n
              ON n.oid = c.relnamespace
            JOIN unnest(i.indkey) WITH ORDINALITY AS keys(attnum, ord)
              ON true
            JOIN pg_attribute a
              ON a.attrelid = c.oid
             AND a.attnum = keys.attnum
            WHERE i.indisprimary
              AND n.nspname = %s
              AND c.relname = %s
            ORDER BY keys.ord
            """,
            (schema_name, table_name),
        )
        return [row[0] for row in cur.fetchall()]


def get_row_count(conn, schema_name, table_name):
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )
        return cur.fetchone()[0]


###############################################################################
# DATATYPE RULES
###############################################################################

def normalize_type(type_name):
    normalized = " ".join(type_name.lower().strip().split())

    aliases = {
        "int2": "smallint",
        "int4": "integer",
        "int8": "bigint",
        "float4": "real",
        "float8": "double precision",
        "bool": "boolean",
        "varchar": "character varying",
        "timestamp": "timestamp without time zone",
    }

    return aliases.get(normalized, normalized)


def parse_character_length(type_name):
    normalized = normalize_type(type_name)

    prefixes = ("character varying(", "varchar(", "character(")

    for prefix in prefixes:
        if normalized.startswith(prefix) and normalized.endswith(")"):
            return int(normalized[len(prefix):-1])

    return None


def parse_numeric(type_name):
    normalized = normalize_type(type_name)

    if normalized.startswith("numeric(") and normalized.endswith(")"):
        values = normalized[len("numeric("):-1].split(",")

        if len(values) == 2:
            return int(values[0].strip()), int(values[1].strip())

    return None


def classify_datatype_change(source_type, target_type):
    """
    Result:
      SAME          - exact match
      COMPATIBLE    - Silver already accepts the Bronze datatype
      SAFE_WIDEN    - approved automatic Silver widening
      MANUAL_REVIEW - block the complete table
    """
    source = normalize_type(source_type)
    target = normalize_type(target_type)

    if source == target:
        return "SAME"

    widening_order = {
        "smallint": 1,
        "integer": 2,
        "bigint": 3,
    }

    if source in widening_order and target in widening_order:
        if widening_order[source] > widening_order[target]:
            return "SAFE_WIDEN"
        return "COMPATIBLE"

    if source == "double precision" and target == "real":
        return "SAFE_WIDEN"

    if source == "real" and target == "double precision":
        return "COMPATIBLE"

    if source == "timestamp without time zone" and target == "date":
        return "SAFE_WIDEN"

    if source == "date" and target == "timestamp without time zone":
        return "COMPATIBLE"

    source_length = parse_character_length(source)
    target_length = parse_character_length(target)

    if source_length is not None and target_length is not None:
        if source_length > target_length:
            return "SAFE_WIDEN"
        return "COMPATIBLE"

    if source == "text" and (
        target.startswith("character varying")
        or target.startswith("varchar")
        or target.startswith("character(")
    ):
        return "SAFE_WIDEN"

    if target == "text" and (
        source.startswith("character varying")
        or source.startswith("varchar")
        or source.startswith("character(")
    ):
        return "COMPATIBLE"

    source_numeric = parse_numeric(source)
    target_numeric = parse_numeric(target)

    if source_numeric and target_numeric:
        source_precision, source_scale = source_numeric
        target_precision, target_scale = target_numeric

        source_integer_digits = source_precision - source_scale
        target_integer_digits = target_precision - target_scale

        if (
            source_precision >= target_precision
            and source_scale >= target_scale
            and source_integer_digits >= target_integer_digits
        ):
            return "SAFE_WIDEN"

        if (
            target_precision >= source_precision
            and target_scale >= source_scale
            and target_integer_digits >= source_integer_digits
        ):
            return "COMPATIBLE"

    return "MANUAL_REVIEW"


###############################################################################
# TARGET SCHEMA MANAGEMENT
###############################################################################

def create_target_table(
    silver_conn,
    target_table,
    source_columns,
    primary_keys,
):
    column_definitions = []

    for column in source_columns:
        definition = sql.SQL("{} {}").format(
            sql.Identifier(column["name"]),
            sql.SQL(column["type"]),
        )

        if column["name"] in primary_keys:
            definition += sql.SQL(" NOT NULL")

        column_definitions.append(definition)

    if primary_keys:
        column_definitions.append(
            sql.SQL("PRIMARY KEY ({})").format(
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in primary_keys
                )
            )
        )

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
            .format(sql.Identifier(TARGET_SCHEMA))
        )

        cur.execute(
            sql.SQL("CREATE TABLE {}.{} ({})").format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
                sql.SQL(", ").join(column_definitions),
            )
        )

    silver_conn.commit()


def synchronize_target_schema(
    silver_conn,
    source_table,
    target_table,
    source_columns,
    primary_keys,
):
    """
    Rules:
      - New Bronze columns are added automatically.
      - Columns removed from Bronze are never dropped from Silver.
      - Safe widening changes are applied automatically.
      - Any risky datatype difference blocks the complete table.
      - Safe ALTER failures also block the complete table.
    """
    if not table_exists(silver_conn, TARGET_SCHEMA, target_table):
        create_target_table(
            silver_conn,
            target_table,
            source_columns,
            primary_keys,
        )
        return {
            "blocked": False,
            "review_count": 0,
            "reason": None,
        }

    target_columns = get_table_columns(
        silver_conn,
        TARGET_SCHEMA,
        target_table,
    )
    target_map = {column["name"]: column for column in target_columns}

    risky_changes = []
    safe_changes = []
    new_columns = []

    for source_column in source_columns:
        column_name = source_column["name"]
        source_type = source_column["type"]

        if column_name not in target_map:
            new_columns.append(source_column)
            continue

        target_type = target_map[column_name]["type"]
        classification = classify_datatype_change(
            source_type,
            target_type,
        )

        if classification == "SAFE_WIDEN":
            safe_changes.append(
                {
                    "column_name": column_name,
                    "source_type": source_type,
                    "target_type": target_type,
                }
            )
        elif classification == "MANUAL_REVIEW":
            risky_changes.append(
                {
                    "column_name": column_name,
                    "source_type": source_type,
                    "target_type": target_type,
                }
            )

    # Block before changing anything if a risky difference exists.
    if risky_changes:
        problem_details = "; ".join(
            (
                f'{change["column_name"]}: '
                f'Bronze={change["source_type"]}, '
                f'Silver={change["target_type"]}'
            )
            for change in risky_changes
        )

        control_message = (
            f"{len(risky_changes)} datatype change(s) require developer review. "
            f"Affected columns: {problem_details}. "
            "The complete table load was blocked."
        )

        for change in risky_changes:
            column_reason = (
                "Risky or narrowing datatype change requires developer review. "
                f'Column={change["column_name"]}, '
                f'Bronze datatype={change["source_type"]}, '
                f'Silver datatype={change["target_type"]}. '
                "The complete table load was blocked."
            )

            log_schema_review(
                silver_conn,
                source_table,
                target_table,
                change["column_name"],
                change["source_type"],
                change["target_type"],
                "MANUAL_REVIEW_REQUIRED",
                column_reason,
            )

            log_error(
                silver_conn,
                source_table,
                target_table,
                "SCHEMA_VALIDATION",
                column_reason,
                severity="CRITICAL",
                column_name=change["column_name"],
                source_datatype=change["source_type"],
                target_datatype=change["target_type"],
            )

        return {
            "blocked": True,
            "review_count": len(risky_changes),
            "reason": control_message,
        }

    # Add new columns only after confirming there are no risky changes.
    try:
        with silver_conn.cursor() as cur:
            for column in new_columns:
                cur.execute(
                    sql.SQL(
                        "ALTER TABLE {}.{} ADD COLUMN {} {}"
                    ).format(
                        sql.Identifier(TARGET_SCHEMA),
                        sql.Identifier(target_table),
                        sql.Identifier(column["name"]),
                        sql.SQL(column["type"]),
                    )
                )

            for change in safe_changes:
                cur.execute(
                    sql.SQL(
                        """
                        ALTER TABLE {}.{}
                        ALTER COLUMN {} TYPE {}
                        USING {}::{}
                        """
                    ).format(
                        sql.Identifier(TARGET_SCHEMA),
                        sql.Identifier(target_table),
                        sql.Identifier(change["column_name"]),
                        sql.SQL(change["source_type"]),
                        sql.Identifier(change["column_name"]),
                        sql.SQL(change["source_type"]),
                    )
                )

        silver_conn.commit()

    except Exception as exc:
        silver_conn.rollback()

        reason = (
            "An approved safe schema change failed. "
            "The complete table load was blocked."
        )

        log_error(
            silver_conn,
            source_table,
            target_table,
            "APPLY_SCHEMA_CHANGE",
            str(exc),
            severity="CRITICAL",
            error_detail=traceback.format_exc(),
        )

        return {
            "blocked": True,
            "review_count": 1,
            "reason": reason,
        }

    return {
        "blocked": False,
        "review_count": 0,
        "reason": None,
    }


###############################################################################
# TEMP TABLE, COPY, AND MERGE
###############################################################################

def create_temp_table(
    silver_conn,
    source_table,
    target_table,
    source_columns,
):
    temp_table = f"tmp_{target_table}_{RUN_ID[:8]}"

    column_list = sql.SQL(", ").join(
        sql.Identifier(column["name"]) for column in source_columns
    )

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                CREATE TEMP TABLE {} AS
                SELECT {}
                FROM {}.{}
                WITH NO DATA
                """
            ).format(
                sql.Identifier(temp_table),
                column_list,
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
            )
        )

    return temp_table


def copy_bronze_to_temp(
    bronze_conn,
    silver_conn,
    source_table,
    temp_table,
    source_columns,
):
    column_list = sql.SQL(", ").join(
        sql.Identifier(column["name"]) for column in source_columns
    )

    source_copy = sql.SQL(
        """
        COPY
        (
            SELECT {}
            FROM {}.{}
        )
        TO STDOUT
        WITH
        (
            FORMAT CSV,
            HEADER FALSE,
            NULL '\\N',
            QUOTE '"',
            ESCAPE '"'
        )
        """
    ).format(
        column_list,
        sql.Identifier(SOURCE_SCHEMA),
        sql.Identifier(source_table),
    )

    target_copy = sql.SQL(
        """
        COPY {} ({})
        FROM STDIN
        WITH
        (
            FORMAT CSV,
            HEADER FALSE,
            NULL '\\N',
            QUOTE '"',
            ESCAPE '"'
        )
        """
    ).format(
        sql.Identifier(temp_table),
        column_list,
    )

    # Disk-backed temporary file prevents the entire table being stored
    # in Python memory.
    with tempfile.TemporaryFile(
        mode="w+",
        encoding="utf-8",
        newline="",
    ) as transfer_file:
        with bronze_conn.cursor() as bronze_cur:
            bronze_cur.copy_expert(
                source_copy.as_string(bronze_conn),
                transfer_file,
            )

        transfer_file.seek(0)

        with silver_conn.cursor() as silver_cur:
            silver_cur.copy_expert(
                target_copy.as_string(silver_conn),
                transfer_file,
            )


def merge_temp_to_target(
    silver_conn,
    temp_table,
    target_table,
    source_columns,
    primary_keys,
):
    column_names = [column["name"] for column in source_columns]

    insert_columns = sql.SQL(", ").join(
        sql.Identifier(column) for column in column_names
    )

    update_columns = [
        column for column in column_names if column not in primary_keys
    ]

    if update_columns:
        conflict_action = sql.SQL("DO UPDATE SET {}").format(
            sql.SQL(", ").join(
                sql.SQL("{} = EXCLUDED.{}").format(
                    sql.Identifier(column),
                    sql.Identifier(column),
                )
                for column in update_columns
            )
        )
    else:
        conflict_action = sql.SQL("DO NOTHING")

    merge_statement = sql.SQL(
        """
        INSERT INTO {}.{} ({})
        SELECT {}
        FROM {}
        ON CONFLICT ({})
        {}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(target_table),
        insert_columns,
        insert_columns,
        sql.Identifier(temp_table),
        sql.SQL(", ").join(
            sql.Identifier(column) for column in primary_keys
        ),
        conflict_action,
    )

    with silver_conn.cursor() as cur:
        cur.execute(merge_statement)
        affected_rows = cur.rowcount

    silver_conn.commit()
    return affected_rows


def drop_temp_table(silver_conn, temp_table):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("DROP TABLE IF EXISTS {}")
            .format(sql.Identifier(temp_table))
        )
    silver_conn.commit()


###############################################################################
# TABLE PROCESSOR
###############################################################################

def process_table(
    bronze_conn,
    silver_conn,
    source_table,
    target_table,
    primary_key_override=None,
):
    start_datetime = datetime.now(timezone.utc)

    bronze_count = None
    silver_count = None
    rows_processed = 0
    status = "FAILED"
    schema_review_required = False
    error_count = 0
    message = None
    temp_table = None

    try:
        print("=" * 80)
        print(
            f"Processing {SOURCE_SCHEMA}.{source_table} "
            f"-> {TARGET_SCHEMA}.{target_table}"
        )

        source_columns = get_table_columns(
            bronze_conn,
            SOURCE_SCHEMA,
            source_table,
        )

        if not source_columns:
            raise RuntimeError("No Bronze columns were found.")

        if primary_key_override:
            primary_keys = [
                value.strip()
                for value in primary_key_override.split(",")
                if value.strip()
            ]
        else:
            primary_keys = get_primary_keys(
                bronze_conn,
                SOURCE_SCHEMA,
                source_table,
            )

        if not primary_keys:
            raise RuntimeError(
                "No primary key was found. Add primary_key_override "
                "to etl_control.etl_table_config."
            )

        source_column_names = {
            column["name"] for column in source_columns
        }

        missing_primary_keys = [
            key for key in primary_keys
            if key not in source_column_names
        ]

        if missing_primary_keys:
            raise RuntimeError(
                "Primary-key columns are missing from Bronze: "
                + ", ".join(missing_primary_keys)
            )

        bronze_count = get_row_count(
            bronze_conn,
            SOURCE_SCHEMA,
            source_table,
        )

        schema_result = synchronize_target_schema(
            silver_conn,
            source_table,
            target_table,
            source_columns,
            primary_keys,
        )

        if schema_result["blocked"]:
            status = "BLOCKED_SCHEMA_REVIEW"
            schema_review_required = True
            error_count += schema_result["review_count"]
            message = schema_result["reason"]

            if table_exists(
                silver_conn,
                TARGET_SCHEMA,
                target_table,
            ):
                silver_count = get_row_count(
                    silver_conn,
                    TARGET_SCHEMA,
                    target_table,
                )

            print(
                f"[{source_table}] BLOCKED: {message}"
            )
            return

        temp_table = create_temp_table(
            silver_conn,
            source_table,
            target_table,
            source_columns,
        )

        copy_bronze_to_temp(
            bronze_conn,
            silver_conn,
            source_table,
            temp_table,
            source_columns,
        )

        rows_processed = merge_temp_to_target(
            silver_conn,
            temp_table,
            target_table,
            source_columns,
            primary_keys,
        )

        silver_count = get_row_count(
            silver_conn,
            TARGET_SCHEMA,
            target_table,
        )

        status = "SUCCESS"
        message = "Table loaded successfully."

    except Exception as exc:
        silver_conn.rollback()
        status = "FAILED"
        error_count += 1
        message = str(exc)

        log_error(
            silver_conn,
            source_table,
            target_table,
            "PROCESS_TABLE",
            str(exc),
            severity="ERROR",
            error_detail=traceback.format_exc(),
        )

        try:
            if table_exists(
                silver_conn,
                TARGET_SCHEMA,
                target_table,
            ):
                silver_count = get_row_count(
                    silver_conn,
                    TARGET_SCHEMA,
                    target_table,
                )
        except Exception:
            silver_conn.rollback()

    finally:
        if temp_table:
            try:
                drop_temp_table(silver_conn, temp_table)
            except Exception as cleanup_error:
                silver_conn.rollback()
                error_count += 1

                if status == "SUCCESS":
                    status = "PARTIAL_SUCCESS"

                log_error(
                    silver_conn,
                    source_table,
                    target_table,
                    "DROP_TEMP_TABLE",
                    str(cleanup_error),
                    severity="WARNING",
                    error_detail=traceback.format_exc(),
                )

        end_datetime = datetime.now(timezone.utc)

        write_control_record(
            silver_conn,
            source_table,
            target_table,
            bronze_count,
            silver_count,
            rows_processed,
            status,
            schema_review_required,
            start_datetime,
            end_datetime,
            error_count,
            message,
        )

        print(
            f"[{source_table}] status={status}, "
            f"bronze_count={bronze_count}, "
            f"silver_count={silver_count}, "
            f"rows_processed={rows_processed}, "
            f"error_count={error_count}"
        )


###############################################################################
# ENTRY POINT
###############################################################################

def main():
    bronze_conn = None
    silver_conn = None

    try:
        bronze_conn = connect_bronze()
        silver_conn = connect_silver()

        create_framework_tables(silver_conn)

        discovered_tables = discover_source_tables(bronze_conn)
        configured_tables = get_enabled_config(silver_conn)

        # When config has rows, it controls which tables run.
        # When config is empty, all discovered CLM tables are loaded.
        if configured_tables:
            table_jobs = []

            for source_table, settings in configured_tables.items():
                if source_table in discovered_tables:
                    table_jobs.append(
                        (
                            source_table,
                            settings["target_table"],
                            settings["primary_key_override"],
                        )
                    )
        else:
            table_jobs = [
                (table_name, table_name, None)
                for table_name in discovered_tables
            ]

        if not table_jobs:
            print("No enabled CLM tables were found.")
            return

        print(
            f"Starting framework run {RUN_ID}. "
            f"Tables selected: {len(table_jobs)}"
        )

        # A failure or blocked schema in one table does not stop the next table.
        for source_table, target_table, pk_override in table_jobs:
            process_table(
                bronze_conn,
                silver_conn,
                source_table,
                target_table,
                pk_override,
            )

        print(f"Framework run {RUN_ID} completed.")

    except Exception as framework_error:
        print(f"Framework-level failure: {framework_error}")
        print(traceback.format_exc())
        raise

    finally:
        if bronze_conn is not None:
            bronze_conn.close()

        if silver_conn is not None:
            silver_conn.close()


if __name__ == "__main__":
    main()
