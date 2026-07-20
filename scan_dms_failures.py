###############################################################################
#
# PARAMETERIZED BRONZE-TO-SILVER METADATA-DRIVEN ETL FRAMEWORK
#
# Technology:
#   AWS Glue Python Shell / Spark Job runtime
#   Python
#   psycopg2
#   PostgreSQL
#
# Purpose:
#   This framework loads every enabled table from a parameterized Bronze PostgreSQL schema
#   into a parameterized Silver PostgreSQL schema using one reusable script.
#
# Main capabilities:
#   1. Discover all CLM source tables automatically.
#   2. Optionally use a metadata configuration table to control processing.
#   3. Detect new Bronze columns and add them to Silver.
#   4. Preserve Silver columns that no longer exist in Bronze.
#   5. Apply only approved safe datatype widening changes automatically.
#   6. Block the complete table when a risky datatype change is detected.
#   7. Check for dependent views and materialized views before changing types.
#   8. Use PostgreSQL TEMP tables instead of permanent staging tables.
#   9. Stream PostgreSQL COPY directly from Bronze to Silver TEMP storage.
#  10. Support INITIAL_INSERT, INSERT_MISSING, UPSERT, FULL_REFRESH and APPEND.
#  11. Store daily source/target counts in the load-control table.
#  12. Store processing failures in the error table.
#  13. Store datatype issues in the schema-review table.
#  14. Continue with the next table when one table fails or is blocked.
#
# Important design rules:
#   - Never drop a Silver column automatically.
#   - Never partially load a table when a datatype issue is found.
#   - Never automatically apply risky or narrowing datatype changes.
#   - Never alter a datatype while dependent database objects exist.
#   - Always record a final control-table entry for every attempted table.
#   - AUTO selects INITIAL_INSERT/INSERT_MISSING for keyed tables and FULL_REFRESH for no-key tables.
#
###############################################################################

import os
import re
import sys
import uuid
import traceback
import threading
import time
from datetime import datetime, timezone

import psycopg2
from psycopg2 import sql


###############################################################################
# AWS GLUE JOB PARAMETERS
#
# Required:
#   --BRONZE_USERNAME
#   --BRONZE_PASSWORD
#   --SILVER_USERNAME
#   --SILVER_PASSWORD
#
# Connection parameters:
#   --BRONZE_HOST
#   --BRONZE_PORT
#   --BRONZE_DB
#   --SILVER_HOST
#   --SILVER_PORT
#   --SILVER_DB
#
# Schema parameters:
#   --SOURCE_SCHEMA
#   --TARGET_SCHEMA
#   --CONTROL_SCHEMA
#
# Processing parameters:
#   --DEFAULT_LOAD_STRATEGY AUTO
#   --ACTIVE_FLAG_COLUMN bronze_record_active_flg
#   --ACTIVE_FLAG_Y Y
#   --ACTIVE_FLAG_N N
#   --BUCKET_COUNT 16
#   --BUCKET_ROW_THRESHOLD 1000000
#   --VALIDATE_KEY_OVERRIDE false
#   --ENABLE_EXACT_COUNTS false
#   --ANALYZE_TEMP_TABLE true
#   --COPY_PIPE_BUFFER_BYTES 1048576
#   --INCLUDE_TABLES table1,table2
#   --EXCLUDE_TABLES table3,table4
#
# AUTO strategy:
#   Keyed table + empty Silver    -> INITIAL_INSERT
#   Keyed table + populated Silver -> INSERT_MISSING
#   Table has no PK               -> FULL_REFRESH
###############################################################################

###############################################################################
# STEP 0 - FRAMEWORK CONFIGURATION
#
# This section defines:
#   - Bronze and Silver PostgreSQL connection properties
#   - Source, target and control schemas
#   - Job name and run identifier
#   - Optional include/exclude table lists for the configured schema
#
# Credentials are parameterized. They may be supplied as AWS Glue job
# parameters or environment variables, so usernames/passwords are never
# hardcoded in this script. AWS Secrets Manager remains the recommended
# production source for passwords.
###############################################################################

def get_runtime_parameter(
    parameter_name,
    default=None,
    required=False,
):
    """
    Read a parameter from either:

      1. AWS Glue / command-line arguments:
           --BRONZE_USERNAME value
           --BRONZE_USERNAME=value

      2. Environment variables:
           BRONZE_USERNAME=value

      3. The supplied default value.

    Glue examples:
      --BRONZE_USERNAME bronze_service_user
      --BRONZE_PASSWORD ********
      --SILVER_USERNAME silver_service_user
      --SILVER_PASSWORD ********
    """
    normalized_name = parameter_name.strip().upper()
    cli_name = f"--{normalized_name}"

    # Support: --PARAMETER=value
    for argument in sys.argv[1:]:
        if argument.startswith(cli_name + "="):
            value = argument.split("=", 1)[1].strip()
            if value:
                return value

    # Support: --PARAMETER value
    for index, argument in enumerate(sys.argv[1:], start=1):
        if argument == cli_name:
            if index + 1 >= len(sys.argv):
                raise ValueError(
                    f"Missing value after command-line parameter {cli_name}"
                )

            value = sys.argv[index + 1].strip()

            if value.startswith("--"):
                raise ValueError(
                    f"Missing value after command-line parameter {cli_name}"
                )

            if value:
                return value

    environment_value = os.getenv(normalized_name)

    if environment_value is not None and environment_value.strip():
        return environment_value.strip()

    if default is not None:
        return default

    if required:
        raise ValueError(
            f"Required parameter {normalized_name} was not supplied. "
            f"Pass {cli_name} in the Glue job parameters or define the "
            f"{normalized_name} environment variable."
        )

    return None


def get_required_secret_parameter(parameter_name):
    """
    Retrieve a required credential without printing or logging its value.
    """
    return get_runtime_parameter(
        parameter_name,
        required=True,
    )


# Bronze PostgreSQL connection parameters
BRONZE_HOST = get_runtime_parameter(
    "BRONZE_HOST",
    default="gsapdi-pg-stg.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com",
)
BRONZE_PORT = int(get_runtime_parameter("BRONZE_PORT", default="5432"))
BRONZE_DB = get_runtime_parameter("BRONZE_DB", default="gsapdi")
BRONZE_USER = get_required_secret_parameter("BRONZE_USERNAME")
BRONZE_PASSWORD = get_required_secret_parameter("BRONZE_PASSWORD")

# Silver PostgreSQL connection parameters
SILVER_HOST = get_runtime_parameter(
    "SILVER_HOST",
    default="gsapdi-pg-mt-dm-dev.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com",
)
SILVER_PORT = int(get_runtime_parameter("SILVER_PORT", default="5432"))
SILVER_DB = get_runtime_parameter("SILVER_DB", default="mtdm")
SILVER_USER = get_required_secret_parameter("SILVER_USERNAME")
SILVER_PASSWORD = get_required_secret_parameter("SILVER_PASSWORD")

# Schema and framework parameters
SOURCE_SCHEMA = get_runtime_parameter("SOURCE_SCHEMA", default="CLM")
TARGET_SCHEMA = get_runtime_parameter("TARGET_SCHEMA", default=SOURCE_SCHEMA)
CONTROL_SCHEMA = get_runtime_parameter("CONTROL_SCHEMA", default="etl_control")
JOB_NAME = get_runtime_parameter(
    "JOB_NAME",
    default="postgres_bronze_to_silver_framework",
)

# AUTO means:
#   - Keyed table and empty Silver: simple INITIAL_INSERT.
#   - Keyed table and populated Silver: INSERT_MISSING by key.
#   - No reliable key: FULL_REFRESH.
DEFAULT_LOAD_STRATEGY = get_runtime_parameter(
    "DEFAULT_LOAD_STRATEGY",
    default="AUTO",
).strip().upper()

ACTIVE_FLAG_COLUMN = get_runtime_parameter(
    "ACTIVE_FLAG_COLUMN",
    default="bronze_record_active_flg",
).strip()
ACTIVE_FLAG_Y = get_runtime_parameter("ACTIVE_FLAG_Y", default="Y")
ACTIVE_FLAG_N = get_runtime_parameter("ACTIVE_FLAG_N", default="N")


BUCKET_COUNT = int(get_runtime_parameter("BUCKET_COUNT", default="16"))

# Tables at or below this Bronze row count run once without buckets.
# Larger keyed tables automatically loop from bucket 0 through BUCKET_COUNT - 1.
BUCKET_ROW_THRESHOLD = int(
    get_runtime_parameter(
        "BUCKET_ROW_THRESHOLD",
        default="1000000",
    )
)

if BUCKET_COUNT < 1:
    raise ValueError("BUCKET_COUNT must be at least 1.")

if BUCKET_ROW_THRESHOLD < 0:
    raise ValueError("BUCKET_ROW_THRESHOLD cannot be negative.")

VALIDATE_KEY_OVERRIDE = (
    get_runtime_parameter("VALIDATE_KEY_OVERRIDE", default="false")
    .strip()
    .lower()
    in {"1", "true", "t", "yes", "y"}
)

ENABLE_EXACT_COUNTS = (
    get_runtime_parameter("ENABLE_EXACT_COUNTS", default="false")
    .strip()
    .lower()
    in {"1", "true", "t", "yes", "y"}
)

ANALYZE_TEMP_TABLE = (
    get_runtime_parameter("ANALYZE_TEMP_TABLE", default="true")
    .strip()
    .lower()
    in {"1", "true", "t", "yes", "y"}
)

# Producer/consumer pipe buffer used while streaming PostgreSQL COPY output
# directly from Bronze into Silver TEMP storage.
COPY_PIPE_BUFFER_BYTES = int(
    get_runtime_parameter(
        "COPY_PIPE_BUFFER_BYTES",
        default="1048576",
    )
)

if COPY_PIPE_BUFFER_BYTES < 8192:
    raise ValueError(
        "COPY_PIPE_BUFFER_BYTES must be at least 8192."
    )

RUN_ID = uuid.uuid4().hex

# Optional comma-separated controls.
# Empty INCLUDE_TABLES means discover all base tables under SOURCE_SCHEMA.
INCLUDE_TABLES = {
    item.strip()
    for item in get_runtime_parameter("INCLUDE_TABLES", default="").split(",")
    if item.strip()
}
EXCLUDE_TABLES = {
    item.strip()
    for item in get_runtime_parameter("EXCLUDE_TABLES", default="").split(",")
    if item.strip()
}


###############################################################################
# STEP 1 - DATABASE CONNECTION HELPERS
#
# Two independent psycopg2 connections are created:
#   - Bronze connection: reads source metadata and data
#   - Silver connection: manages target schema, TEMP tables, merge and auditing
#
# Connections are opened once for the framework run and reused for all tables.
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
# STEP 2 - CREATE FRAMEWORK CONTROL TABLES
#
# The following tables are created in the Silver control schema:
#
# etl_table_config
#   Optional metadata table used to enable/disable tables, set execution order,
#   rename targets, and provide primary-key overrides.
#
# etl_load_control
#   Stores one audit row per table per framework execution, including Bronze
#   count, Silver count, rows processed, status, timing and message.
#
# etl_error_log
#   Stores technical failures such as connection, COPY, merge or cleanup errors.
#
# etl_schema_change_review
#   Stores risky datatype differences and dependency-related schema changes that
#   require developer review before the table can be loaded.
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
                    load_strategy          varchar(30) NOT NULL DEFAULT 'AUTO',
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

        # Add load_strategy to existing configuration tables created by
        # an earlier version of the framework.
        cur.execute(
            sql.SQL(
                """
                ALTER TABLE {}.etl_table_config
                ADD COLUMN IF NOT EXISTS load_strategy varchar(30)
                NOT NULL DEFAULT 'AUTO'
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
# STEP 3 - AUDIT AND ERROR-LOGGING HELPERS
#
# These functions isolate the logging logic from the loading logic.
#
# log_error()
#   Inserts technical error details into etl_error_log.
#
# log_schema_review()
#   Inserts one review record for each affected column.
#
# write_control_record()
#   Writes the final table-level execution result to etl_load_control.
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
# STEP 4 - POSTGRESQL METADATA DISCOVERY
#
# Metadata is read directly from PostgreSQL system catalogs.
#
# The framework discovers:
#   - All source base tables
#   - Enabled metadata configuration
#   - Ordered table columns and exact PostgreSQL datatypes
#   - Declared primary-key columns
#   - Current source and target row counts
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


def get_table_config(
    silver_conn,
    source_schema,
    target_schema,
):
    """
    Return table-level overrides for one schema mapping.

    Important behavior:
      - No config row: table is included automatically.
      - enabled = false: table is excluded.
      - enabled = true: table is included and overrides may be applied.
    """
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT
                    source_table,
                    target_table,
                    enabled,
                    primary_key_override,
                    load_strategy,
                    load_order
                FROM {}.etl_table_config
                WHERE source_schema = %s
                  AND target_schema = %s
                """
            ).format(sql.Identifier(CONTROL_SCHEMA)),
            (source_schema, target_schema),
        )

        return {
            row[0]: {
                "target_table": row[1],
                "enabled": row[2],
                "primary_key_override": row[3],
                "load_strategy": row[4],
                "load_order": row[5],
            }
            for row in cur.fetchall()
        }


def build_table_jobs(bronze_conn, silver_conn):
    """
    Build the ordered work list for the single configured schema.

    The schema mapping is controlled only by:
      SOURCE_SCHEMA -> TARGET_SCHEMA

    A job contains:
      source_schema
      source_table
      target_schema
      target_table
      primary_key_override
      load_order
    """
    table_jobs = []

    discovered_tables = discover_source_tables(bronze_conn)
    table_config = get_table_config(
        silver_conn,
        SOURCE_SCHEMA,
        TARGET_SCHEMA,
    )

    for source_table in discovered_tables:
        config = table_config.get(source_table)

        # A disabled metadata row explicitly excludes the table.
        if config and not config["enabled"]:
            print(f"Skipping excluded table {SOURCE_SCHEMA}.{source_table}")
            continue

        target_table = (
            config["target_table"]
            if config and config["target_table"]
            else source_table
        )

        table_jobs.append(
            {
                "source_schema": SOURCE_SCHEMA,
                "source_table": source_table,
                "target_schema": TARGET_SCHEMA,
                "target_table": target_table,
                "primary_key_override": (
                    config["primary_key_override"]
                    if config
                    else None
                ),
                "load_strategy": (
                    str(config["load_strategy"]).strip().upper()
                    if config and config["load_strategy"]
                    else DEFAULT_LOAD_STRATEGY
                ),
                "table_load_order": (
                    config["load_order"]
                    if config
                    else 1000
                ),
            }
        )

    table_jobs.sort(
        key=lambda job: (
            job["table_load_order"],
            job["source_table"],
        )
    )

    return table_jobs


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
    """Return an exact row count. This can scan the complete table."""
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )
        return cur.fetchone()[0]


def get_estimated_row_count(conn, schema_name, table_name):
    """Return PostgreSQL's estimated live-row count without COUNT(*)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(
                stats.n_live_tup,
                class.reltuples::bigint,
                0
            )::bigint
            FROM pg_catalog.pg_class class
            JOIN pg_catalog.pg_namespace namespace
              ON namespace.oid = class.relnamespace
            LEFT JOIN pg_catalog.pg_stat_user_tables stats
              ON stats.relid = class.oid
            WHERE namespace.nspname = %s
              AND class.relname = %s
              AND class.relkind IN ('r', 'p')
            """,
            (schema_name, table_name),
        )
        row = cur.fetchone()
        return int(row[0]) if row else 0


def get_audit_row_count(conn, schema_name, table_name):
    if ENABLE_EXACT_COUNTS:
        return get_row_count(conn, schema_name, table_name)

    return get_estimated_row_count(conn, schema_name, table_name)


###############################################################################
# STEP 5 - DATATYPE CLASSIFICATION RULES
#
# Every Bronze/Silver datatype difference is classified as:
#
# SAME
#   Datatypes are identical.
#
# COMPATIBLE
#   Silver is already wide enough to accept the Bronze values.
#
# SAFE_WIDEN
#   Silver can be safely widened automatically.
#
# MANUAL_REVIEW
#   The change may truncate, reinterpret or reject existing data.
#   The entire table is blocked and no data is loaded.
###############################################################################

def normalize_type(type_name):
    """
    Convert PostgreSQL datatype aliases and equivalent precision formats into
    a canonical representation before comparing Bronze and Silver.

    PostgreSQL's default timestamp precision is 6. Therefore these are treated
    as equivalent:

        timestamp with time zone
        timestamp(6) with time zone

        timestamp without time zone
        timestamp(6) without time zone

        time with time zone
        time(6) with time zone

        time without time zone
        time(6) without time zone
    """
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

    normalized = aliases.get(normalized, normalized)

    # PostgreSQL default precision is 6; remove it so equivalent timestamp/time
    # declarations do not create false datatype-change alerts.
    default_precision_patterns = {
        r"^timestamp\(6\) with time zone$":
            "timestamp with time zone",
        r"^timestamp\(6\) without time zone$":
            "timestamp without time zone",
        r"^time\(6\) with time zone$":
            "time with time zone",
        r"^time\(6\) without time zone$":
            "time without time zone",
    }

    for pattern, canonical_type in default_precision_patterns.items():
        if re.match(pattern, normalized):
            return canonical_type

    return normalized


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
# STEP 6 - DEPENDENT OBJECT CHECKS
#
# PostgreSQL does not allow ALTER COLUMN TYPE when views or materialized views
# depend on the affected column.
#
# Before applying a safe datatype change, the framework searches PostgreSQL
# dependency catalogs and returns:
#   - Dependent schema
#   - Dependent object name
#   - Object type
#
# If dependencies exist:
#   - ALTER TABLE is not attempted
#   - The entire table load is blocked
#   - Dependency details are written to the control, error and review tables
###############################################################################

def get_column_dependencies(
    silver_conn,
    schema_name,
    table_name,
    column_name,
):
    """
    Return direct and indirect views/materialized views that depend on a
    target-table column.

    Direct example:
        table.column -> materialized_view

    Indirect example:
        table.column -> view_1 -> materialized_view_2

    PostgreSQL blocks ALTER COLUMN TYPE when a dependent view or materialized
    view exists anywhere in the dependency chain.
    """
    with silver_conn.cursor() as cur:
        cur.execute(
            """
            WITH RECURSIVE dependency_tree AS
            (
                -- Level 1: objects directly dependent on the source column.
                SELECT DISTINCT
                    dependent_class.oid AS dependent_oid,
                    dependent_ns.nspname AS dependent_schema,
                    dependent_class.relname AS dependent_object,
                    dependent_class.relkind AS dependent_relkind,
                    1 AS dependency_level
                FROM pg_catalog.pg_depend dep
                JOIN pg_catalog.pg_rewrite rewrite_rule
                  ON rewrite_rule.oid = dep.objid
                JOIN pg_catalog.pg_class dependent_class
                  ON dependent_class.oid = rewrite_rule.ev_class
                JOIN pg_catalog.pg_namespace dependent_ns
                  ON dependent_ns.oid = dependent_class.relnamespace
                JOIN pg_catalog.pg_class source_class
                  ON source_class.oid = dep.refobjid
                JOIN pg_catalog.pg_namespace source_ns
                  ON source_ns.oid = source_class.relnamespace
                JOIN pg_catalog.pg_attribute source_attribute
                  ON source_attribute.attrelid = source_class.oid
                 AND source_attribute.attnum = dep.refobjsubid
                WHERE source_ns.nspname = %s
                  AND source_class.relname = %s
                  AND source_attribute.attname = %s
                  AND dep.refobjsubid > 0
                  AND dependent_class.relkind IN ('v', 'm')

                UNION

                -- Next levels: objects that depend on an already dependent
                -- view or materialized view.
                SELECT DISTINCT
                    next_class.oid AS dependent_oid,
                    next_ns.nspname AS dependent_schema,
                    next_class.relname AS dependent_object,
                    next_class.relkind AS dependent_relkind,
                    tree.dependency_level + 1
                FROM dependency_tree tree
                JOIN pg_catalog.pg_depend next_dep
                  ON next_dep.refobjid = tree.dependent_oid
                JOIN pg_catalog.pg_rewrite next_rewrite
                  ON next_rewrite.oid = next_dep.objid
                JOIN pg_catalog.pg_class next_class
                  ON next_class.oid = next_rewrite.ev_class
                JOIN pg_catalog.pg_namespace next_ns
                  ON next_ns.oid = next_class.relnamespace
                WHERE next_class.relkind IN ('v', 'm')
                  AND tree.dependency_level < 20
                  AND next_class.oid <> tree.dependent_oid
            )
            SELECT DISTINCT
                dependent_schema,
                dependent_object,
                CASE dependent_relkind
                    WHEN 'v' THEN 'VIEW'
                    WHEN 'm' THEN 'MATERIALIZED VIEW'
                    ELSE dependent_relkind::text
                END AS dependent_object_type,
                MIN(dependency_level) AS dependency_level
            FROM dependency_tree
            GROUP BY
                dependent_schema,
                dependent_object,
                dependent_relkind
            ORDER BY
                MIN(dependency_level),
                dependent_schema,
                dependent_object
            """,
            (schema_name, table_name, column_name),
        )

        return [
            {
                "schema": row[0],
                "object": row[1],
                "type": row[2],
                "level": row[3],
            }
            for row in cur.fetchall()
        ]

def format_dependencies(dependencies):
    return ", ".join(
        (
            f'{dependency["schema"]}.{dependency["object"]} '
            f'({dependency["type"]}, level={dependency.get("level", 1)})'
        )
        for dependency in dependencies
    )


###############################################################################
# STEP 7 - SILVER TARGET SCHEMA MANAGEMENT
#
# This section performs controlled schema evolution.
#
# New target table:
#   Create it from Bronze metadata and add the primary key.
#
# New Bronze column:
#   Add the column to Silver automatically.
#
# Bronze column removed:
#   Leave the Silver column unchanged to preserve historical data.
#
# Safe datatype widening:
#   Check dependencies, then alter Silver automatically.
#
# Risky datatype change:
#   Block the complete table and send it to developer review.
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

    column_definitions.append(
        sql.SQL("{} varchar(1) NOT NULL DEFAULT {}").format(
            sql.Identifier(ACTIVE_FLAG_COLUMN),
            sql.Literal(ACTIVE_FLAG_Y),
        )
    )

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

    if ACTIVE_FLAG_COLUMN not in target_map:
        with silver_conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    ALTER TABLE {}.{}
                    ADD COLUMN {} varchar(1)
                    NOT NULL DEFAULT {}
                    """
                ).format(
                    sql.Identifier(TARGET_SCHEMA),
                    sql.Identifier(target_table),
                    sql.Identifier(ACTIVE_FLAG_COLUMN),
                    sql.Literal(ACTIVE_FLAG_Y),
                )
            )
        silver_conn.commit()

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
        detailed_changes = []

        for change in risky_changes:
            dependencies = get_column_dependencies(
                silver_conn,
                TARGET_SCHEMA,
                target_table,
                change["column_name"],
            )

            dependency_text = (
                format_dependencies(dependencies)
                if dependencies
                else "None detected"
            )

            detailed_changes.append(
                {
                    **change,
                    "dependencies": dependencies,
                    "dependency_text": dependency_text,
                }
            )

        problem_details = "; ".join(
            (
                f'{change["column_name"]}: '
                f'Bronze={change["source_type"]}, '
                f'Silver={change["target_type"]}, '
                f'Dependent objects={change["dependency_text"]}'
            )
            for change in detailed_changes
        )

        control_message = (
            f"{len(detailed_changes)} datatype change(s) require "
            "developer review. "
            f"Affected columns: {problem_details}. "
            "The complete table load was blocked."
        )

        for change in detailed_changes:
            column_reason = (
                "Risky or narrowing datatype change requires developer review. "
                f'Column={change["column_name"]}, '
                f'Bronze datatype={change["source_type"]}, '
                f'Silver datatype={change["target_type"]}, '
                f'Dependent objects={change["dependency_text"]}. '
                "The complete table load was blocked."
            )

            change_type = (
                "DATATYPE_AND_DEPENDENCY_REVIEW_REQUIRED"
                if change["dependencies"]
                else "MANUAL_REVIEW_REQUIRED"
            )

            log_schema_review(
                silver_conn,
                source_table,
                target_table,
                change["column_name"],
                change["source_type"],
                change["target_type"],
                change_type,
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
            "review_count": len(detailed_changes),
            "reason": control_message,
        }

    # Check dependent views and materialized views before safe ALTERs.
    dependency_blocks = []

    for change in safe_changes:
        dependencies = get_column_dependencies(
            silver_conn,
            TARGET_SCHEMA,
            target_table,
            change["column_name"],
        )

        if dependencies:
            dependency_blocks.append(
                {
                    **change,
                    "dependencies": dependencies,
                }
            )

    if dependency_blocks:
        dependency_messages = []

        for change in dependency_blocks:
            dependency_text = format_dependencies(change["dependencies"])

            reason = (
                "Datatype change is classified as safe, but dependent database "
                "objects prevent ALTER COLUMN TYPE. "
                f'Column={change["column_name"]}, '
                f'Bronze datatype={change["source_type"]}, '
                f'Silver datatype={change["target_type"]}, '
                f'Dependent objects={dependency_text}. '
                "Developer must review and recreate or update the dependent "
                "objects before rerunning this table."
            )

            dependency_messages.append(
                (
                    f'{change["column_name"]}: '
                    f'Bronze={change["source_type"]}, '
                    f'Silver={change["target_type"]}, '
                    f'Dependencies={dependency_text}'
                )
            )

            log_schema_review(
                silver_conn,
                source_table,
                target_table,
                change["column_name"],
                change["source_type"],
                change["target_type"],
                "DEPENDENT_OBJECT_REVIEW_REQUIRED",
                reason,
            )

            log_error(
                silver_conn,
                source_table,
                target_table,
                "COLUMN_DEPENDENCY_CHECK",
                reason,
                severity="CRITICAL",
                column_name=change["column_name"],
                source_datatype=change["source_type"],
                target_datatype=change["target_type"],
            )

        return {
            "blocked": True,
            "review_count": len(dependency_blocks),
            "reason": (
                f"{len(dependency_blocks)} datatype change(s) are blocked by "
                "dependent database objects. Affected columns: "
                + "; ".join(dependency_messages)
                + ". The complete table load was blocked."
            ),
        }

    # Add new columns and apply safe changes only after all validation passes.
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

        affected_columns = ", ".join(
            (
                f'{change["column_name"]} '
                f'({change["target_type"]} -> {change["source_type"]})'
            )
            for change in safe_changes
        )

        reason = (
            "An approved safe schema change failed. "
            f"Affected columns: {affected_columns or 'unknown'}. "
            f"PostgreSQL error: {exc}. "
            "The complete table load was blocked."
        )

        log_error(
            silver_conn,
            source_table,
            target_table,
            "APPLY_SCHEMA_CHANGE",
            reason,
            severity="CRITICAL",
            error_detail=traceback.format_exc(),
        )

        return {
            "blocked": True,
            "review_count": max(len(safe_changes), 1),
            "reason": reason,
        }

    return {
        "blocked": False,
        "review_count": 0,
        "reason": None,
    }


###############################################################################
# STEP 8 - TEMP TABLE, BULK COPY AND MERGE
#
# A PostgreSQL session TEMP table is created for the current table.
#
# Data transfer:
#   Bronze COPY TO STDOUT
#       -> temporary disk-backed transfer file
#       -> Silver COPY FROM STDIN into the TEMP table
#
# Merge:
#   INSERT INTO target
#   SELECT FROM temp
#   ON CONFLICT(primary key)
#   DO UPDATE
#
# The TEMP table is explicitly dropped after processing and would also disappear
# automatically when the Silver connection closes.
###############################################################################

def build_bucket_predicate(
    alias,
    primary_keys,
    bucket_count=1,
    bucket_id=0,
):
    """
    Build a deterministic predicate for one bucket.

    bucket_count=1 processes the complete table.
    """
    if bucket_count == 1:
        return sql.SQL("TRUE")

    if not primary_keys:
        raise RuntimeError(
            "Bucket processing requires a primary key or "
            "primary_key_override."
        )

    key_text = sql.SQL(", ").join(
        sql.SQL("COALESCE({}.{}::text, '<NULL>')").format(
            sql.Identifier(alias),
            sql.Identifier(key),
        )
        for key in primary_keys
    )

    return sql.SQL(
        """
        mod(
            (
                hashtextextended(concat_ws('|', {}), 0)
                & 9223372036854775807
            ),
            {}
        ) = {}
        """
    ).format(
        key_text,
        sql.Literal(bucket_count),
        sql.Literal(bucket_id),
    )


def create_temp_table(
    silver_conn,
    source_table,
    target_table,
    source_columns,
):
    """Create an empty TEMP table containing only Bronze/source columns."""
    temp_table = f"tmp_{target_table}_{RUN_ID[:8]}"

    source_column_list = sql.SQL(", ").join(
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
                source_column_list,
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
    primary_keys,
    bucket_count=1,
    bucket_id=0,
):
    """
    Stream PostgreSQL COPY output directly from Bronze to Silver TEMP storage.

    The earlier implementation first wrote the complete source extract to the
    Glue worker's local disk and only then started Silver COPY. This version
    uses an OS pipe:

        Bronze COPY TO STDOUT
            -> bounded pipe
            -> Silver COPY FROM STDIN

    Benefits:
      - Silver starts loading immediately.
      - No full-table local temporary file.
      - Lower Glue ephemeral-disk usage.
      - Natural backpressure between Bronze and Silver.
    """
    source_select_columns = sql.SQL(", ").join(
        sql.SQL("src.{}").format(sql.Identifier(column["name"]))
        for column in source_columns
    )

    target_columns = sql.SQL(", ").join(
        sql.Identifier(column["name"]) for column in source_columns
    )

    bucket_predicate = build_bucket_predicate(
        "src",
        primary_keys,
        bucket_count,
        bucket_id,
    )

    source_copy = sql.SQL(
        """
        COPY
        (
            SELECT {}
            FROM {}.{} src
            WHERE {}
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
        source_select_columns,
        sql.Identifier(SOURCE_SCHEMA),
        sql.Identifier(source_table),
        bucket_predicate,
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
        target_columns,
    )

    read_fd, write_fd = os.pipe()
    producer_errors = []
    copy_started = time.monotonic()

    def bronze_copy_producer():
        try:
            with os.fdopen(
                write_fd,
                mode="w",
                buffering=COPY_PIPE_BUFFER_BYTES,
                encoding="utf-8",
                newline="",
            ) as pipe_writer:
                with bronze_conn.cursor() as bronze_cur:
                    bronze_cur.copy_expert(
                        source_copy.as_string(bronze_conn),
                        pipe_writer,
                    )
        except BaseException as exc:
            producer_errors.append(exc)
            try:
                os.close(write_fd)
            except OSError:
                pass

    producer_thread = threading.Thread(
        target=bronze_copy_producer,
        name=f"bronze-copy-{source_table}",
        daemon=True,
    )

    print(
        f"[{source_table}] Starting streaming COPY "
        f"for bucket {bucket_id + 1}/{bucket_count}"
    )

    producer_thread.start()

    consumer_error = None

    try:
        with os.fdopen(
            read_fd,
            mode="r",
            buffering=COPY_PIPE_BUFFER_BYTES,
            encoding="utf-8",
            newline="",
        ) as pipe_reader:
            with silver_conn.cursor() as silver_cur:
                silver_cur.copy_expert(
                    target_copy.as_string(silver_conn),
                    pipe_reader,
                )
    except BaseException as exc:
        consumer_error = exc
        try:
            os.close(read_fd)
        except OSError:
            pass
    finally:
        producer_thread.join()

    elapsed_seconds = time.monotonic() - copy_started

    if consumer_error is not None:
        silver_conn.rollback()
        raise RuntimeError(
            f"Silver COPY failed for {source_table}: "
            f"{consumer_error}"
        ) from consumer_error

    if producer_errors:
        silver_conn.rollback()
        producer_error = producer_errors[0]
        raise RuntimeError(
            f"Bronze COPY failed for {source_table}: "
            f"{producer_error}"
        ) from producer_error

    print(
        f"[{source_table}] Streaming COPY completed in "
        f"{elapsed_seconds:.2f} seconds"
    )


def validate_unique_key(
    bronze_conn,
    source_table,
    primary_keys,
):
    """
    Validate a configured primary-key override before using it for UPSERT.

    The key is considered valid only when:
      - none of the key columns contain NULL
      - no duplicate key combinations exist
    """
    if not primary_keys:
        return

    null_predicate = sql.SQL(" OR ").join(
        sql.SQL("{} IS NULL").format(sql.Identifier(column))
        for column in primary_keys
    )

    duplicate_columns = sql.SQL(", ").join(
        sql.Identifier(column) for column in primary_keys
    )

    with bronze_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT COUNT(*)
                FROM {}.{}
                WHERE {}
                """
            ).format(
                sql.Identifier(SOURCE_SCHEMA),
                sql.Identifier(source_table),
                null_predicate,
            )
        )
        null_count = cur.fetchone()[0]

        if null_count > 0:
            raise RuntimeError(
                "Configured UPSERT key contains NULL values. "
                f"Key columns={primary_keys}, null_rows={null_count}."
            )

        cur.execute(
            sql.SQL(
                """
                SELECT COUNT(*)
                FROM
                (
                    SELECT {}
                    FROM {}.{}
                    GROUP BY {}
                    HAVING COUNT(*) > 1
                ) duplicate_keys
                """
            ).format(
                duplicate_columns,
                sql.Identifier(SOURCE_SCHEMA),
                sql.Identifier(source_table),
                duplicate_columns,
            )
        )
        duplicate_group_count = cur.fetchone()[0]

        if duplicate_group_count > 0:
            raise RuntimeError(
                "Configured UPSERT key is not unique in Bronze. "
                f"Key columns={primary_keys}, "
                f"duplicate_key_groups={duplicate_group_count}."
            )


def ensure_target_unique_constraint(
    silver_conn,
    target_table,
    primary_keys,
):
    """
    ON CONFLICT requires a matching PRIMARY KEY or UNIQUE constraint.

    The unique-key comparison uses a comma-separated text value instead of
    PostgreSQL arrays. This avoids name[] versus text[] datatype errors while
    preserving the exact order of composite-key columns.

    For existing Silver tables, create a UNIQUE constraint when the configured
    business key is valid but is not already enforced in Silver.
    """
    if not primary_keys:
        return

    with silver_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM pg_catalog.pg_index i
                JOIN pg_catalog.pg_class c
                  ON c.oid = i.indrelid
                JOIN pg_catalog.pg_namespace n
                  ON n.oid = c.relnamespace
                WHERE n.nspname = %s
                  AND c.relname = %s
                  AND i.indisunique
                  AND
                  (
                      SELECT string_agg(
                          a.attname::text,
                          ',' ORDER BY keys.ord
                      )
                      FROM unnest(i.indkey) WITH ORDINALITY
                           AS keys(attnum, ord)
                      JOIN pg_catalog.pg_attribute a
                        ON a.attrelid = c.oid
                       AND a.attnum = keys.attnum
                  ) = %s
            )
            """,
            (
                TARGET_SCHEMA,
                target_table,
                ",".join(primary_keys),
            ),
        )

        constraint_exists = cur.fetchone()[0]

        if constraint_exists:
            return

        constraint_name = (
            f"uq_{target_table}_{'_'.join(primary_keys)}"
        )[:63]

        cur.execute(
            sql.SQL(
                """
                ALTER TABLE {}.{}
                ADD CONSTRAINT {} UNIQUE ({})
                """
            ).format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
                sql.Identifier(constraint_name),
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in primary_keys
                ),
            )
        )

    silver_conn.commit()


def full_refresh_temp_to_target(
    silver_conn,
    temp_table,
    target_table,
    source_columns,
):
    """
    Replace the complete Silver table contents when no reliable key exists.

    TRUNCATE and INSERT run in one transaction. If INSERT fails, PostgreSQL
    rolls back the TRUNCATE as well.
    """
    column_names = [column["name"] for column in source_columns]

    column_list = sql.SQL(", ").join(
        sql.Identifier(column) for column in column_names
    )

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("TRUNCATE TABLE {}.{}").format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
            )
        )

        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.{} ({})
                SELECT {}
                FROM {}
                """
            ).format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
                column_list,
                column_list,
                sql.Identifier(temp_table),
            )
        )

        affected_rows = cur.rowcount

    silver_conn.commit()
    return affected_rows


def append_temp_to_target(
    silver_conn,
    temp_table,
    target_table,
    source_columns,
):
    """
    Append every source row to Silver.

    Use this only for true append-only/event tables. Re-running the same source
    data will create duplicates.
    """
    column_names = [column["name"] for column in source_columns]

    column_list = sql.SQL(", ").join(
        sql.Identifier(column) for column in column_names
    )

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.{} ({})
                SELECT {}
                FROM {}
                """
            ).format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
                column_list,
                column_list,
                sql.Identifier(temp_table),
            )
        )

        affected_rows = cur.rowcount

    silver_conn.commit()
    return affected_rows



def initial_insert_temp_to_target(
    silver_conn,
    temp_table,
    target_table,
    source_columns,
):
    """Initial plain INSERT with active flag Y."""
    column_names = [column["name"] for column in source_columns]

    insert_columns = sql.SQL(", ").join(
        [sql.Identifier(column) for column in column_names]
        + [sql.Identifier(ACTIVE_FLAG_COLUMN)]
    )

    select_columns = sql.SQL(", ").join(
        [sql.SQL("b.{}").format(sql.Identifier(column))
         for column in column_names]
        + [sql.Literal(ACTIVE_FLAG_Y)]
    )

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.{} ({})
                SELECT {}
                FROM {} b
                """
            ).format(
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(target_table),
                insert_columns,
                select_columns,
                sql.Identifier(temp_table),
            )
        )
        affected_rows = cur.rowcount

    silver_conn.commit()
    return affected_rows


def synchronize_temp_to_target_with_flag(
    silver_conn,
    temp_table,
    target_table,
    source_columns,
    primary_keys,
    bucket_count=1,
    bucket_id=0,
):
    """
    Native PostgreSQL synchronization without hashes.

    Matching keys:
      - update only when a non-key source column changed
      - reactivate the row with active flag Y

    New Bronze keys:
      - insert with active flag Y

    Silver keys absent from Bronze:
      - retain the row and mark active flag N
    """
    if not primary_keys:
        raise RuntimeError(
            "SYNC_WITH_FLAG requires a primary key or primary_key_override."
        )

    column_names = [column["name"] for column in source_columns]
    non_key_columns = [
        column for column in column_names
        if column not in primary_keys
    ]

    key_match = sql.SQL(" AND ").join(
        sql.SQL("s.{} = b.{}").format(
            sql.Identifier(key),
            sql.Identifier(key),
        )
        for key in primary_keys
    )

    insert_columns = sql.SQL(", ").join(
        [sql.Identifier(column) for column in column_names]
        + [sql.Identifier(ACTIVE_FLAG_COLUMN)]
    )

    select_columns = sql.SQL(", ").join(
        [sql.SQL("b.{}").format(sql.Identifier(column))
         for column in column_names]
        + [sql.Literal(ACTIVE_FLAG_Y)]
    )

    inserted_rows = 0
    updated_rows = 0
    inactive_rows = 0

    try:
        with silver_conn.cursor() as cur:
            update_started = time.monotonic()
            print(f"[{target_table}] Starting native UPDATE comparison.")

            if non_key_columns:
                set_clause = sql.SQL(", ").join(
                    [
                        sql.SQL("{} = b.{}").format(
                            sql.Identifier(column),
                            sql.Identifier(column),
                        )
                        for column in non_key_columns
                    ]
                    + [
                        sql.SQL("{} = {}").format(
                            sql.Identifier(ACTIVE_FLAG_COLUMN),
                            sql.Literal(ACTIVE_FLAG_Y),
                        )
                    ]
                )

                changed_predicate = sql.SQL(" OR ").join(
                    sql.SQL("s.{} IS DISTINCT FROM b.{}").format(
                        sql.Identifier(column),
                        sql.Identifier(column),
                    )
                    for column in non_key_columns
                )

                cur.execute(
                    sql.SQL(
                        """
                        UPDATE {}.{} s
                        SET {}
                        FROM {} b
                        WHERE {}
                          AND
                          (
                              {}
                              OR s.{} IS DISTINCT FROM {}
                          )
                        """
                    ).format(
                        sql.Identifier(TARGET_SCHEMA),
                        sql.Identifier(target_table),
                        set_clause,
                        sql.Identifier(temp_table),
                        key_match,
                        changed_predicate,
                        sql.Identifier(ACTIVE_FLAG_COLUMN),
                        sql.Literal(ACTIVE_FLAG_Y),
                    )
                )
                updated_rows = cur.rowcount
            else:
                cur.execute(
                    sql.SQL(
                        """
                        UPDATE {}.{} s
                        SET {} = {}
                        FROM {} b
                        WHERE {}
                          AND s.{} IS DISTINCT FROM {}
                        """
                    ).format(
                        sql.Identifier(TARGET_SCHEMA),
                        sql.Identifier(target_table),
                        sql.Identifier(ACTIVE_FLAG_COLUMN),
                        sql.Literal(ACTIVE_FLAG_Y),
                        sql.Identifier(temp_table),
                        key_match,
                        sql.Identifier(ACTIVE_FLAG_COLUMN),
                        sql.Literal(ACTIVE_FLAG_Y),
                    )
                )
                updated_rows = cur.rowcount

            print(
                f"[{target_table}] Native UPDATE completed in "
                f"{time.monotonic() - update_started:.2f} seconds; "
                f"rows={updated_rows}."
            )

            insert_started = time.monotonic()
            print(f"[{target_table}] Starting missing-key INSERT.")

            cur.execute(
                sql.SQL(
                    """
                    INSERT INTO {}.{} ({})
                    SELECT {}
                    FROM {} b
                    WHERE NOT EXISTS
                    (
                        SELECT 1
                        FROM {}.{} s
                        WHERE {}
                    )
                    """
                ).format(
                    sql.Identifier(TARGET_SCHEMA),
                    sql.Identifier(target_table),
                    insert_columns,
                    select_columns,
                    sql.Identifier(temp_table),
                    sql.Identifier(TARGET_SCHEMA),
                    sql.Identifier(target_table),
                    key_match,
                )
            )
            inserted_rows = cur.rowcount

            print(
                f"[{target_table}] Missing-key INSERT completed in "
                f"{time.monotonic() - insert_started:.2f} seconds; "
                f"rows={inserted_rows}."
            )

            inactive_started = time.monotonic()
            print(f"[{target_table}] Starting inactive-flag update.")

            reverse_key_match = sql.SQL(" AND ").join(
                sql.SQL("b.{} = s.{}").format(
                    sql.Identifier(key),
                    sql.Identifier(key),
                )
                for key in primary_keys
            )

            target_bucket_predicate = build_bucket_predicate(
                "s",
                primary_keys,
                bucket_count,
                bucket_id,
            )

            cur.execute(
                sql.SQL(
                    """
                    UPDATE {}.{} s
                    SET {} = {}
                    WHERE {}
                      AND s.{} IS DISTINCT FROM {}
                      AND NOT EXISTS
                      (
                          SELECT 1
                          FROM {} b
                          WHERE {}
                      )
                    """
                ).format(
                    sql.Identifier(TARGET_SCHEMA),
                    sql.Identifier(target_table),
                    sql.Identifier(ACTIVE_FLAG_COLUMN),
                    sql.Literal(ACTIVE_FLAG_N),
                    target_bucket_predicate,
                    sql.Identifier(ACTIVE_FLAG_COLUMN),
                    sql.Literal(ACTIVE_FLAG_N),
                    sql.Identifier(temp_table),
                    reverse_key_match,
                )
            )
            inactive_rows = cur.rowcount

            print(
                f"[{target_table}] Inactive-flag update completed in "
                f"{time.monotonic() - inactive_started:.2f} seconds; "
                f"rows={inactive_rows}."
            )

        silver_conn.commit()

    except Exception:
        silver_conn.rollback()
        raise

    return {
        "inserted": inserted_rows,
        "updated_or_reactivated": updated_rows,
        "marked_inactive": inactive_rows,
        "rows_processed": inserted_rows + updated_rows + inactive_rows,
    }


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


def prepare_temp_table_for_sync(
    silver_conn,
    temp_table,
    primary_keys,
):
    """
    Create a TEMP-table key index and collect optimizer statistics.
    """
    if not primary_keys:
        return

    started = time.monotonic()
    index_name = f"idx_{temp_table}_pk"[:63]

    print(f"[{temp_table}] Creating TEMP key index.")

    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("CREATE INDEX {} ON {} ({})").format(
                sql.Identifier(index_name),
                sql.Identifier(temp_table),
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in primary_keys
                ),
            )
        )

        if ANALYZE_TEMP_TABLE:
            cur.execute(
                sql.SQL("ANALYZE {}").format(
                    sql.Identifier(temp_table)
                )
            )

    silver_conn.commit()

    print(
        f"[{temp_table}] TEMP preparation completed in "
        f"{time.monotonic() - started:.2f} seconds."
    )


def drop_temp_table(silver_conn, temp_table):
    with silver_conn.cursor() as cur:
        cur.execute(
            sql.SQL("DROP TABLE IF EXISTS {}")
            .format(sql.Identifier(temp_table))
        )
    silver_conn.commit()


###############################################################################
# STEP 9 - PROCESS ONE TABLE
#
# For each table, the framework performs the following sequence:
#
#   1. Read source columns.
#   2. Determine the primary key.
#   3. Count Bronze rows.
#   4. Compare and synchronize the Silver schema.
#   5. Block the table if any schema review is required.
#   6. Create the TEMP table.
#   7. COPY Bronze data to the TEMP table.
#   8. Initial insert, insert missing, upsert, full refresh or append.
#   9. Count Silver rows.
#  10. Drop the TEMP table.
#  11. Write the final control-table record.
#
# Any failure is isolated to the current table. The framework then continues
# with the remaining CLM tables.
###############################################################################

def process_table(
    bronze_conn,
    silver_conn,
    source_table,
    target_table,
    primary_key_override=None,
    load_strategy="AUTO",
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

        requested_load_strategy = str(
            load_strategy or DEFAULT_LOAD_STRATEGY
        ).strip().upper()

        if requested_load_strategy not in {
            "AUTO",
            "SYNC_WITH_FLAG",
            "UPSERT",
            "FULL_REFRESH",
            "APPEND",
        }:
            raise RuntimeError(
                "Unsupported load_strategy. Expected one of: "
                "AUTO, SYNC_WITH_FLAG, UPSERT, FULL_REFRESH, APPEND. "
                f"Received={requested_load_strategy}"
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

        if requested_load_strategy == "AUTO":
            load_strategy = (
                "SYNC_WITH_FLAG"
                if primary_keys
                else "FULL_REFRESH"
            )
        else:
            load_strategy = requested_load_strategy

        if load_strategy in {"UPSERT", "SYNC_WITH_FLAG"} and not primary_keys:
            raise RuntimeError(
                f"{load_strategy} requires a source primary key or a reliable "
                f"primary_key_override in {CONTROL_SCHEMA}.etl_table_config. "
                "Use load_strategy='AUTO' or 'FULL_REFRESH' for tables "
                "without a reliable key."
            )

        if load_strategy not in {"UPSERT", "SYNC_WITH_FLAG"}:
            # FULL_REFRESH and APPEND do not require a key.
            primary_keys = []

        print(
            f"[{source_table}] requested_strategy={requested_load_strategy}, "
            f"resolved_strategy={load_strategy}, "
            f"primary_keys={primary_keys or 'NONE'}"
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

        if (
            primary_key_override
            and VALIDATE_KEY_OVERRIDE
            and load_strategy in {"UPSERT", "SYNC_WITH_FLAG"}
        ):
            validate_unique_key(
                bronze_conn,
                source_table,
                primary_keys,
            )

        bronze_count = get_audit_row_count(
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
                silver_count = get_audit_row_count(
                    silver_conn,
                    TARGET_SCHEMA,
                    target_table,
                )

            print(
                f"[{source_table}] BLOCKED: {message}"
            )
            return

        if load_strategy in {"UPSERT", "SYNC_WITH_FLAG"}:
            ensure_target_unique_constraint(
                silver_conn,
                target_table,
                primary_keys,
            )

        target_count_before_load = get_audit_row_count(
            silver_conn,
            TARGET_SCHEMA,
            target_table,
        )

        # Small tables run once. Large keyed tables automatically process all
        # buckets in one Glue execution; no daily parameter changes are needed.
        if (
            load_strategy in {"SYNC_WITH_FLAG", "UPSERT"}
            and primary_keys
            and bronze_count > BUCKET_ROW_THRESHOLD
            and BUCKET_COUNT > 1
        ):
            effective_bucket_count = BUCKET_COUNT
        else:
            effective_bucket_count = 1

        print(
            f"[{source_table}] bronze_count={bronze_count}, "
            f"bucket_threshold={BUCKET_ROW_THRESHOLD}, "
            f"effective_bucket_count={effective_bucket_count}"
        )

        total_rows_processed = 0
        total_inserted = 0
        total_updated = 0
        total_inactive = 0
        actual_strategy = load_strategy

        for current_bucket_id in range(effective_bucket_count):
            print(
                f"[{source_table}] Processing bucket "
                f"{current_bucket_id + 1}/{effective_bucket_count}"
            )

            temp_table = create_temp_table(
                silver_conn,
                source_table,
                target_table,
                source_columns,
            )

            try:
                copy_bronze_to_temp(
                    bronze_conn,
                    silver_conn,
                    source_table,
                    temp_table,
                    source_columns,
                    primary_keys,
                    effective_bucket_count,
                    current_bucket_id,
                )

                prepare_temp_table_for_sync(
                    silver_conn,
                    temp_table,
                    primary_keys,
                )

                # Only a genuinely empty target on a non-bucketed run uses the
                # initial plain insert. For bucketed initial loads, bucket 0 uses
                # plain insert and later buckets use synchronization.
                current_target_count = get_audit_row_count(
                    silver_conn,
                    TARGET_SCHEMA,
                    target_table,
                )

                if load_strategy == "SYNC_WITH_FLAG":
                    if current_target_count == 0:
                        bucket_rows = initial_insert_temp_to_target(
                            silver_conn,
                            temp_table,
                            target_table,
                            source_columns,
                        )
                        bucket_metrics = {
                            "inserted": bucket_rows,
                            "updated_or_reactivated": 0,
                            "marked_inactive": 0,
                            "rows_processed": bucket_rows,
                        }
                        actual_strategy = "INITIAL_INSERT"
                    else:
                        bucket_metrics = synchronize_temp_to_target_with_flag(
                            silver_conn,
                            temp_table,
                            target_table,
                            source_columns,
                            primary_keys,
                            effective_bucket_count,
                            current_bucket_id,
                        )
                        bucket_rows = bucket_metrics["rows_processed"]
                        actual_strategy = "NATIVE_SYNC_WITH_FLAG"

                    total_inserted += bucket_metrics["inserted"]
                    total_updated += bucket_metrics["updated_or_reactivated"]
                    total_inactive += bucket_metrics["marked_inactive"]

                elif load_strategy == "UPSERT":
                    if current_target_count == 0:
                        bucket_rows = initial_insert_temp_to_target(
                            silver_conn,
                            temp_table,
                            target_table,
                            source_columns,
                        )
                        actual_strategy = "INITIAL_INSERT"
                    else:
                        bucket_rows = merge_temp_to_target(
                            silver_conn,
                            temp_table,
                            target_table,
                            source_columns,
                            primary_keys,
                        )
                        actual_strategy = "UPSERT"

                elif load_strategy == "FULL_REFRESH":
                    bucket_rows = full_refresh_temp_to_target(
                        silver_conn,
                        temp_table,
                        target_table,
                        source_columns,
                    )

                    with silver_conn.cursor() as cur:
                        cur.execute(
                            sql.SQL(
                                "UPDATE {}.{} SET {} = {}"
                            ).format(
                                sql.Identifier(TARGET_SCHEMA),
                                sql.Identifier(target_table),
                                sql.Identifier(ACTIVE_FLAG_COLUMN),
                                sql.Literal(ACTIVE_FLAG_Y),
                            )
                        )
                    silver_conn.commit()
                    actual_strategy = "FULL_REFRESH"

                else:
                    bucket_rows = append_temp_to_target(
                        silver_conn,
                        temp_table,
                        target_table,
                        source_columns,
                    )
                    actual_strategy = "APPEND"

                total_rows_processed += bucket_rows

            finally:
                if temp_table:
                    drop_temp_table(silver_conn, temp_table)
                    temp_table = None

        rows_processed = total_rows_processed

        if actual_strategy == "NATIVE_SYNC_WITH_FLAG":
            sync_metrics = {
                "inserted": total_inserted,
                "updated_or_reactivated": total_updated,
                "marked_inactive": total_inactive,
            }

        silver_count = get_audit_row_count(
            silver_conn,
            TARGET_SCHEMA,
            target_table,
        )

        status = "SUCCESS"
        if actual_strategy == "SYNC_WITH_FLAG":
            message = (
                "Table synchronized successfully. "
                f"Inserted={sync_metrics['inserted']}, "
                f"updated/reactivated={sync_metrics['updated_or_reactivated']}, "
                f"marked inactive={sync_metrics['marked_inactive']}, "
                f"buckets processed={effective_bucket_count}."
            )
        else:
            message = f"Table loaded successfully using {actual_strategy} strategy."

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
                silver_count = get_audit_row_count(
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
# STEP 10 - SINGLE-SCHEMA FRAMEWORK ENTRY POINT
#
# The main function:
#   - Opens Bronze and Silver connections
#   - Creates framework control tables
#   - Discovers all enabled tables in SOURCE_SCHEMA
#   - Applies optional metadata configuration
#   - Processes tables one by one
#   - Closes all database connections
###############################################################################

def main():
    bronze_conn = None
    silver_conn = None

    try:
        print("=" * 80)
        print("POSTGRES GLUE FRAMEWORK - VERSION 10 STREAMING MULTI-SCHEMA")
        print(f"Run ID             : {RUN_ID}")
        print(f"Job name           : {JOB_NAME}")
        print(f"Bronze host/database: {BRONZE_HOST}/{BRONZE_DB}")
        print(f"Bronze login       : {BRONZE_USER}")
        print(f"Silver host/database: {SILVER_HOST}/{SILVER_DB}")
        print(f"Silver login       : {SILVER_USER}")
        print(f"Source schema      : {SOURCE_SCHEMA}")
        print(f"Target schema      : {TARGET_SCHEMA}")
        print(f"Control schema     : {CONTROL_SCHEMA}")
        print(f"Default strategy   : {DEFAULT_LOAD_STRATEGY}")
        print(f"Active flag column : {ACTIVE_FLAG_COLUMN}")
        print(f"Active/Inactive    : {ACTIVE_FLAG_Y}/{ACTIVE_FLAG_N}")
        print(f"Maximum buckets    : {BUCKET_COUNT}")
        print(f"Bucket threshold   : {BUCKET_ROW_THRESHOLD}")
        print(f"Validate override  : {VALIDATE_KEY_OVERRIDE}")
        print(f"Exact counts       : {ENABLE_EXACT_COUNTS}")
        print(f"Analyze TEMP       : {ANALYZE_TEMP_TABLE}")
        print(f"COPY pipe buffer   : {COPY_PIPE_BUFFER_BYTES}")
        print("Passwords are parameterized and are not logged.")
        print("=" * 80)

        bronze_conn = connect_bronze()
        silver_conn = connect_silver()

        create_framework_tables(silver_conn)

        table_jobs = build_table_jobs(
            bronze_conn,
            silver_conn,
        )

        if not table_jobs:
            print("No enabled source tables were found.")
            return

        print(
            f"Starting framework run {RUN_ID}. "
            f"Tables selected for {SOURCE_SCHEMA} -> {TARGET_SCHEMA}: {len(table_jobs)}"
        )

        for table_job in table_jobs:
            process_table(
                bronze_conn,
                silver_conn,
                table_job["source_table"],
                table_job["target_table"],
                table_job["primary_key_override"],
                table_job["load_strategy"],
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
