import os
from pathlib import Path

import psycopg2


# ============================================================
# CONFIGURATION
# ============================================================

DB_HOST = os.getenv("DB_HOST", "your-host")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "your-database")
DB_USER = os.getenv("DB_USER", "your-user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your-password")

SCHEMA_NAME = os.getenv("SCHEMA_NAME", "mtdm")

OUTPUT_DIR = Path("SQL Scripts") / "MVs"


# ============================================================
# SQL
# ============================================================

MV_QUERY = """
SELECT
    schemaname,
    matviewname,
    pg_get_viewdef(
        format('%I.%I', schemaname, matviewname)::regclass,
        true
    ) AS definition
FROM pg_matviews
WHERE schemaname = %s
ORDER BY matviewname;
"""


INDEX_QUERY = """
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = %s
  AND tablename = %s
ORDER BY indexname;
"""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_materialized_views(conn):
    with conn.cursor() as cur:
        cur.execute(MV_QUERY, (SCHEMA_NAME,))
        return cur.fetchall()


def get_indexes(conn, schema_name, mv_name):
    with conn.cursor() as cur:
        cur.execute(INDEX_QUERY, (schema_name, mv_name))
        return cur.fetchall()


def build_mv_sql(schema_name, mv_name, definition, indexes):
    lines = []

    lines.append("-- ============================================================")
    lines.append(f"-- Materialized View: {schema_name}.{mv_name}")
    lines.append("-- ============================================================")
    lines.append("")
    lines.append(f"CREATE MATERIALIZED VIEW {schema_name}.{mv_name} AS")
    lines.append("")
    lines.append(definition.rstrip(";"))
    lines.append("")
    lines.append("WITH DATA;")
    lines.append("")
    lines.append("")
    lines.append("-- ============================================================")
    lines.append("-- Indexes")
    lines.append("-- ============================================================")
    lines.append("")

    if indexes:
        for index_name, index_def in indexes:
            lines.append(f"-- Index: {index_name}")
            lines.append(index_def.rstrip(";") + ";")
            lines.append("")
    else:
        lines.append("-- No indexes defined for this materialized view")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to database: {DB_NAME}")
    print(f"Schema: {SCHEMA_NAME}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    print()

    conn = get_connection()

    try:
        materialized_views = get_materialized_views(conn)

        if not materialized_views:
            print(f"No materialized views found in schema '{SCHEMA_NAME}'.")
            return

        print(
            f"Found {len(materialized_views)} materialized view(s)."
        )
        print()

        generated_files = []

        for schema_name, mv_name, definition in materialized_views:

            indexes = get_indexes(
                conn,
                schema_name,
                mv_name
            )

            sql_content = build_mv_sql(
                schema_name=schema_name,
                mv_name=mv_name,
                definition=definition,
                indexes=indexes
            )

            file_path = OUTPUT_DIR / f"{mv_name}.sql"

            file_path.write_text(
                sql_content,
                encoding="utf-8"
            )

            generated_files.append(file_path)

            print(
                f"Created: {file_path} "
                f"({len(indexes)} index(es))"
            )

        print()
        print("============================================================")
        print("Generation complete")
        print("============================================================")
        print(f"Database MVs : {len(materialized_views)}")
        print(f"Files created: {len(generated_files)}")
        print(f"Output folder: {OUTPUT_DIR.resolve()}")

        if len(materialized_views) == len(generated_files):
            print("Validation: PASSED - one file created per MV")
        else:
            print("Validation: FAILED - MV/file count mismatch")

    finally:
        conn.close()


if __name__ == "__main__":
    main()


pip install psycopg2-binary


$env:DB_HOST="your-rds-host"
$env:DB_PORT="5432"
$env:DB_NAME="your_database"
$env:DB_USER="your_user"
$env:DB_PASSWORD="your_password"
$env:SCHEMA_NAME="mtdm"

python generate_mv_files.py
