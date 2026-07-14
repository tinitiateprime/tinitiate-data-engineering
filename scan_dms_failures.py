"""
dms_task_failures.py

Reads AWS DMS apply failures from PostgreSQL:
    public.awsdms_apply_exceptions

Outputs:
    dms_task_failures_last_30_days.csv
"""

import csv
import os
import re
import sys
from collections import Counter
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
# Prefer environment variables instead of hardcoding passwords.

DB_HOST = os.getenv(
    "DB_HOST",
    "gsapdi-pg-mt-dm-dev.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com",
)
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "mtdm")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DAYS_BACK = int(os.getenv("DAYS_BACK", "30"))
OUTPUT_FILE = os.getenv(
    "OUTPUT_FILE",
    "dms_task_failures_last_30_days.csv",
)


# ---------------------------------------------------------
# CLASSIFICATION PATTERNS
# ---------------------------------------------------------

COLUMN_TYPE_DRIFT_PATTERNS = [
    r"\bcolumn\b.*\bdoes not exist\b",
    r"\bmissing column\b",
    r"\bunknown column\b",
    r"\btype mismatch\b",
    r"\bdata type mismatch\b",
    r"\bdatatype mismatch\b",
    r"\bis of type\b.*\bbut expression is of type\b",
    r"\binvalid input syntax for\b",
    r"\bvalue too long for type\b",
    r"\bnumeric field overflow\b",
    r"\binvalid byte sequence\b",
    r"\bextra data after last expected column\b",
    r"\btable definition.*changed\b",
    r"\bschema.*changed\b",
    r"\bsource table.*changed\b",
    r"\bcannot cast\b",
    r"\boperator does not exist\b",
]

MATVIEW_LOCK_PATTERNS = [
    r"\bcould not obtain lock\b",
    r"\block timeout\b",
    r"\bcanceling statement due to lock timeout\b",
    r"\bdeadlock detected\b",
    r"\brelation.*is being used\b",
    r"\bmaterialized view\b.*\block\b",
    r"\block\b.*\bmaterialized view\b",
    r"\brefresh materialized view\b.*\bfailed\b",
    r"\bcannot refresh materialized view\b",
]

PERMISSION_PATTERNS = [
    r"\bpermission denied\b",
    r"\binsufficient privilege\b",
    r"\bmust be owner\b",
    r"\bnot owner of\b",
    r"\baccess denied\b",
    r"\bnot authorized\b",
    r"\bpermission denied for schema\b",
    r"\bpermission denied for table\b",
    r"\bpermission denied for relation\b",
    r"\bpermission denied for sequence\b",
]

MISSING_OBJECT_PATTERNS = [
    r"\brelation\b.*\bdoes not exist\b",
    r"\btable\b.*\bdoes not exist\b",
    r"\bschema\b.*\bdoes not exist\b",
]


def matches_any(text: str, patterns: list[str]) -> bool:
    """Return True when any regular-expression pattern matches."""
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def classify_failure(error: Optional[str], statement: Optional[str]) -> str:
    """
    Categorize a DMS failure using the ERROR and STATEMENT values.

    Missing relations are kept separate because they are not always
    column/type drift. They may indicate a missing target object.
    """
    combined_text = f"{error or ''} {statement or ''}".strip()

    if matches_any(combined_text, PERMISSION_PATTERNS):
        return "Permission/ownership issue"

    if matches_any(combined_text, MATVIEW_LOCK_PATTERNS):
        return "Dependent object lock during matview refresh"

    if matches_any(combined_text, COLUMN_TYPE_DRIFT_PATTERNS):
        return "Column/type drift on source"

    if matches_any(combined_text, MISSING_OBJECT_PATTERNS):
        return "Missing table/relation - review for schema drift"

    return "Unclassified"


def clean_text(value: Optional[str]) -> str:
    """Make multiline database text safe for CSV."""
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def validate_configuration() -> None:
    """Make sure required credentials were supplied."""
    missing = []

    if not DB_USER:
        missing.append("DB_USER")

    if not DB_PASSWORD:
        missing.append("DB_PASSWORD")

    if missing:
        raise ValueError(
            "Missing environment variables: "
            + ", ".join(missing)
        )


def get_connection():
    """Create a secure PostgreSQL connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        connect_timeout=30,
        application_name="dms_failure_inventory",
    )


def pull_failures() -> list[dict]:
    """
    Read failures from the last configured number of days.

    The column names must be quoted because AWS DMS created them
    using uppercase identifiers.
    """
    sql = """
        SELECT
            "TASK_NAME",
            "TABLE_OWNER",
            "TABLE_NAME",
            "ERROR_TIME",
            "ERROR",
            "STATEMENT"
        FROM public.awsdms_apply_exceptions
        WHERE "ERROR_TIME" >= CURRENT_TIMESTAMP - (%s * INTERVAL '1 day')
        ORDER BY "ERROR_TIME" DESC;
    """

    results = []

    with get_connection() as connection:
        # Named cursor reads large tables in batches instead of loading
        # the complete result into memory at once.
        with connection.cursor(
            name="dms_failure_cursor",
            cursor_factory=RealDictCursor,
        ) as cursor:
            cursor.itersize = 1_000
            cursor.execute(sql, (DAYS_BACK,))

            while True:
                rows = cursor.fetchmany(1_000)

                if not rows:
                    break

                for row in rows:
                    error_text = clean_text(row["ERROR"])
                    statement_text = clean_text(row["STATEMENT"])

                    results.append(
                        {
                            "task_name": row["TASK_NAME"],
                            "table_owner": row["TABLE_OWNER"],
                            "table_name": row["TABLE_NAME"],
                            "error_time": row["ERROR_TIME"],
                            "category": classify_failure(
                                error_text,
                                statement_text,
                            ),
                            "error": error_text,
                            "statement": statement_text,
                        }
                    )

    return results


def write_csv(rows: list[dict]) -> None:
    """Write the Jira-ready DMS inventory report."""
    fieldnames = [
        "task_name",
        "table_owner",
        "table_name",
        "error_time",
        "category",
        "error",
        "statement",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for row in rows:
            output_row = row.copy()

            if isinstance(output_row["error_time"], datetime):
                output_row["error_time"] = (
                    output_row["error_time"].isoformat(
                        sep=" ",
                        timespec="seconds",
                    )
                )

            writer.writerow(output_row)


def print_summary(rows: list[dict]) -> None:
    """Print totals by failure category."""
    category_counts = Counter(
        row["category"]
        for row in rows
    )

    table_counts = Counter(
        f'{row["table_owner"]}.{row["table_name"]}'
        for row in rows
    )

    print("\nDMS TASK FAILURE INVENTORY")
    print("=" * 60)
    print(f"Period             : Last {DAYS_BACK} days")
    print(f"Total failure rows : {len(rows)}")
    print(f"Output file        : {OUTPUT_FILE}")

    print("\nFailures by category")
    print("-" * 60)

    for category, count in category_counts.most_common():
        print(f"{category}: {count}")

    print("\nTop affected tables")
    print("-" * 60)

    for table_name, count in table_counts.most_common(10):
        print(f"{table_name}: {count}")


def main() -> int:
    try:
        validate_configuration()

        print("Connecting to PostgreSQL...")
        print(f"Host: {DB_HOST}")
        print(f"Database: {DB_NAME}")
        print(f"Reading the last {DAYS_BACK} days...")

        failures = pull_failures()
        write_csv(failures)
        print_summary(failures)

        return 0

    except psycopg2.Error as exc:
        print("\nPostgreSQL error:")
        print(exc)
        return 1

    except Exception as exc:
        print(f"\nError: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
