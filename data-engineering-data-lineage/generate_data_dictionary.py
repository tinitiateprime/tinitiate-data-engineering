import csv
from pathlib import Path
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "tinitiateai",
    "user": "ti_dbuser",
    "password": "tiuser!23456",
}

OUTPUT_DIR = Path("C:/Projects/openmetadata-demo/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCHEMAS = ("bronze_layer", "silver_layer", "gold_layer")


def get_columns(conn):
    sql = """
    SELECT
        table_schema,
        table_name,
        column_name,
        data_type,
        is_nullable,
        ordinal_position
    FROM information_schema.columns
    WHERE table_schema IN %s
    ORDER BY table_schema, table_name, ordinal_position;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (SCHEMAS,))
        return cur.fetchall()


def write_csv(rows):
    path = OUTPUT_DIR / "data_dictionary.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Layer",
            "Schema",
            "Object Name",
            "Column Name",
            "Data Type",
            "Nullable",
            "Description",
            "Source / Lineage Notes",
        ])

        for schema, table, column, data_type, nullable, position in rows:
            layer = schema.replace("_layer", "").upper()
            writer.writerow([
                layer,
                schema,
                table,
                column,
                data_type,
                nullable,
                "",
                "",
            ])

    print(f"CSV created: {path}")


def write_markdown(rows):
    path = OUTPUT_DIR / "data_dictionary.md"

    grouped = {}
    for schema, table, column, data_type, nullable, position in rows:
        grouped.setdefault((schema, table), []).append(
            (column, data_type, nullable)
        )

    with path.open("w", encoding="utf-8") as f:
        f.write("# Data Dictionary\n\n")
        f.write("## Scope\n\n")
        f.write("This dictionary covers Bronze, Silver, and Gold layer database objects.\n\n")

        for (schema, table), columns in grouped.items():
            layer = schema.replace("_layer", "").upper()

            f.write(f"## {schema}.{table}\n\n")
            f.write(f"**Layer:** {layer}\n\n")
            f.write("| Column | Data Type | Nullable | Description | Source / Lineage Notes |\n")
            f.write("|---|---|---|---|---|\n")

            for column, data_type, nullable in columns:
                f.write(f"| {column} | {data_type} | {nullable} |  |  |\n")

            f.write("\n")

    print(f"Markdown created: {path}")


def main():
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        rows = get_columns(conn)
        write_csv(rows)
        write_markdown(rows)
    finally:
        conn.close()


if __name__ == "__main__":
    main()