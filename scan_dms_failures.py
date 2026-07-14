"""
AWS Glue Job: DMS Task Failure Inventory

Purpose:
    Read AWS DMS apply failures from:
        public.awsdms_apply_exceptions

    Categorize failures as:
        1. Column/type drift on source
        2. Dependent object lock during matview refresh
        3. Permission/ownership issue
        4. Missing object/schema drift
        5. Unclassified

Output:
    CSV file written to /tmp and optionally uploaded to S3.

Required Glue parameters:
    --DB_HOST
    --DB_PORT
    --DB_NAME
    --DB_USER
    --DB_PASSWORD

Optional Glue parameters:
    --DAYS_BACK
    --OUTPUT_S3_URI
"""

import csv
import os
import re
import sys
import traceback
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import boto3
import psycopg2
from awsglue.utils import getResolvedOptions
from psycopg2.extras import RealDictCursor


# =============================================================================
# GLUE ARGUMENT HELPERS
# =============================================================================

def argument_exists(argument_name: str) -> bool:
    """
    Check whether a Glue argument was provided.

    Example:
        argument_exists("DAYS_BACK")
        checks for --DAYS_BACK in sys.argv.
    """
    return f"--{argument_name}" in sys.argv


def get_optional_argument(
    argument_name: str,
    default_value: str,
) -> str:
    """
    Read an optional Glue argument or return its default value.
    """
    if argument_exists(argument_name):
        resolved = getResolvedOptions(sys.argv, [argument_name])
        return resolved[argument_name]

    return default_value


# =============================================================================
# REQUIRED GLUE PARAMETERS
# =============================================================================

REQUIRED_ARGUMENTS = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ],
)

JOB_NAME = REQUIRED_ARGUMENTS["JOB_NAME"]

DB_HOST = REQUIRED_ARGUMENTS["DB_HOST"]
DB_PORT = int(REQUIRED_ARGUMENTS["DB_PORT"])
DB_NAME = REQUIRED_ARGUMENTS["DB_NAME"]
DB_USER = REQUIRED_ARGUMENTS["DB_USER"]
DB_PASSWORD = REQUIRED_ARGUMENTS["DB_PASSWORD"]


# =============================================================================
# OPTIONAL PARAMETERS
# =============================================================================

DAYS_BACK = int(
    get_optional_argument(
        "DAYS_BACK",
        "30",
    )
)

OUTPUT_S3_URI = get_optional_argument(
    "OUTPUT_S3_URI",
    "",
)

LOCAL_OUTPUT_FILE = (
    f"/tmp/dms_task_failures_last_{DAYS_BACK}_days.csv"
)

FETCH_BATCH_SIZE = 1000


# =============================================================================
# FAILURE CLASSIFICATION PATTERNS
# =============================================================================

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
    r"\bcannot be cast\b",
    r"\bout of range for type\b",
    r"\bviolates not-null constraint\b",
]

MATVIEW_LOCK_PATTERNS = [
    r"\bcould not obtain lock\b",
    r"\block timeout\b",
    r"\bcanceling statement due to lock timeout\b",
    r"\bdeadlock detected\b",
    r"\brelation\b.*\bis being used\b",
    r"\bmaterialized view\b.*\block\b",
    r"\block\b.*\bmaterialized view\b",
    r"\brefresh materialized view\b.*\bfailed\b",
    r"\bcannot refresh materialized view\b",
    r"\brefresh materialized view\b",
    r"\bconcurrent update\b",
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
    r"\bpermission denied for database\b",
    r"\bpermission denied for function\b",
]

MISSING_OBJECT_PATTERNS = [
    r"\brelation\b.*\bdoes not exist\b",
    r"\btable\b.*\bdoes not exist\b",
    r"\bschema\b.*\bdoes not exist\b",
    r"\bsequence\b.*\bdoes not exist\b",
    r"\bfunction\b.*\bdoes not exist\b",
]


# =============================================================================
# CLASSIFICATION FUNCTIONS
# =============================================================================

def matches_any(
    text: str,
    patterns: List[str],
) -> bool:
    """
    Return True when any regular-expression pattern matches the text.
    """
    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for pattern in patterns
    )


def classify_failure(
    error: Optional[str],
    statement: Optional[str],
) -> str:
    """
    Classify a DMS failure by examining both ERROR and STATEMENT.

    Permission and lock checks are performed first so that generic words
    such as relation or type do not incorrectly classify the failure.
    """
    combined_text = (
        f"{error or ''} {statement or ''}"
    ).strip()

    if matches_any(
        combined_text,
        PERMISSION_PATTERNS,
    ):
        return "Permission/ownership issue"

    if matches_any(
        combined_text,
        MATVIEW_LOCK_PATTERNS,
    ):
        return (
            "Dependent object lock during "
            "matview refresh"
        )

    if matches_any(
        combined_text,
        COLUMN_TYPE_DRIFT_PATTERNS,
    ):
        return "Column/type drift on source"

    if matches_any(
        combined_text,
        MISSING_OBJECT_PATTERNS,
    ):
        return (
            "Missing table/relation - "
            "review for schema drift"
        )

    return "Unclassified"


def clean_text(
    value: Optional[str],
) -> str:
    """
    Remove line breaks and repeated whitespace from database text.
    """
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()


# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def get_connection():
    """
    Create a PostgreSQL connection to the Silver database.
    """
    print("Opening PostgreSQL connection...")

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        connect_timeout=30,
        application_name=JOB_NAME,
        options="-c statement_timeout=600000",
    )


def verify_exception_table(
    connection,
) -> None:
    """
    Confirm that public.awsdms_apply_exceptions exists.
    """
    validation_sql = """
        SELECT EXISTS
        (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'awsdms_apply_exceptions'
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(validation_sql)
        table_exists = cursor.fetchone()[0]

    if not table_exists:
        raise RuntimeError(
            "The table "
            "public.awsdms_apply_exceptions "
            "was not found in database "
            f"{DB_NAME}."
        )


def pull_failures() -> List[Dict]:
    """
    Read DMS failures from the configured number of days.

    ORDER BY is intentionally omitted from PostgreSQL to avoid an expensive
    database-wide sort. The returned records are sorted in Python after they
    have been retrieved.
    """
    query = """
        SELECT
            "TASK_NAME",
            "TABLE_OWNER",
            "TABLE_NAME",
            "ERROR_TIME",
            "ERROR",
            "STATEMENT"
        FROM public.awsdms_apply_exceptions
        WHERE "ERROR_TIME" >=
              CURRENT_TIMESTAMP - (%s * INTERVAL '1 day');
    """

    results: List[Dict] = []

    with get_connection() as connection:
        verify_exception_table(connection)

        print(
            "Reading DMS apply exceptions for "
            f"the last {DAYS_BACK} days..."
        )

        with connection.cursor(
            name="dms_failure_server_cursor",
            cursor_factory=RealDictCursor,
        ) as cursor:
            cursor.itersize = FETCH_BATCH_SIZE
            cursor.execute(
                query,
                (DAYS_BACK,),
            )

            processed_count = 0

            while True:
                rows = cursor.fetchmany(
                    FETCH_BATCH_SIZE
                )

                if not rows:
                    break

                for row in rows:
                    error_text = clean_text(
                        row["ERROR"]
                    )

                    statement_text = clean_text(
                        row["STATEMENT"]
                    )

                    results.append(
                        {
                            "task_name": clean_text(
                                row["TASK_NAME"]
                            ),
                            "table_owner": clean_text(
                                row["TABLE_OWNER"]
                            ),
                            "table_name": clean_text(
                                row["TABLE_NAME"]
                            ),
                            "error_time": row[
                                "ERROR_TIME"
                            ],
                            "category": classify_failure(
                                error_text,
                                statement_text,
                            ),
                            "error": error_text,
                            "statement": statement_text,
                        }
                    )

                processed_count += len(rows)

                print(
                    "Failure records processed: "
                    f"{processed_count}"
                )

    results.sort(
        key=lambda record: (
            record["error_time"]
            if record["error_time"] is not None
            else datetime.min
        ),
        reverse=True,
    )

    return results


# =============================================================================
# CSV OUTPUT
# =============================================================================

def write_csv(
    rows: List[Dict],
) -> None:
    """
    Write the DMS failure inventory to a CSV file under /tmp.
    """
    fieldnames = [
        "task_name",
        "table_owner",
        "table_name",
        "error_time",
        "category",
        "error",
        "statement",
    ]

    print(
        f"Writing CSV file: {LOCAL_OUTPUT_FILE}"
    )

    with open(
        LOCAL_OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:
            output_row = row.copy()

            error_time = output_row.get(
                "error_time"
            )

            if isinstance(
                error_time,
                datetime,
            ):
                output_row["error_time"] = (
                    error_time.isoformat(
                        sep=" ",
                        timespec="seconds",
                    )
                )

            writer.writerow(output_row)


# =============================================================================
# S3 UPLOAD
# =============================================================================

def parse_s3_uri(
    s3_uri: str,
) -> Tuple[str, str]:
    """
    Convert an S3 URI into bucket and key.

    Example:
        s3://my-bucket/reports/file.csv
    """
    parsed = urlparse(s3_uri)

    if parsed.scheme != "s3":
        raise ValueError(
            "OUTPUT_S3_URI must begin with s3://"
        )

    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    if not bucket:
        raise ValueError(
            "OUTPUT_S3_URI does not contain "
            "an S3 bucket name."
        )

    if not key:
        key = os.path.basename(
            LOCAL_OUTPUT_FILE
        )

    if key.endswith("/"):
        key = (
            key
            + os.path.basename(
                LOCAL_OUTPUT_FILE
            )
        )

    return bucket, key


def upload_csv_to_s3() -> Optional[str]:
    """
    Upload the generated CSV to S3 when OUTPUT_S3_URI is provided.
    """
    if not OUTPUT_S3_URI:
        print(
            "OUTPUT_S3_URI was not provided. "
            "The CSV remains only in Glue /tmp."
        )
        return None

    bucket, key = parse_s3_uri(
        OUTPUT_S3_URI
    )

    print(
        "Uploading report to "
        f"s3://{bucket}/{key}"
    )

    s3_client = boto3.client("s3")

    s3_client.upload_file(
        LOCAL_OUTPUT_FILE,
        bucket,
        key,
    )

    return f"s3://{bucket}/{key}"


# =============================================================================
# REPORT SUMMARY
# =============================================================================

def print_summary(
    rows: List[Dict],
    uploaded_s3_uri: Optional[str],
) -> None:
    """
    Print Jira-ready totals by category and affected table.
    """
    category_counts = Counter(
        row["category"]
        for row in rows
    )

    table_counts = Counter(
        (
            f'{row["table_owner"]}.'
            f'{row["table_name"]}'
        )
        for row in rows
    )

    print("")
    print("=" * 80)
    print("DMS TASK FAILURE INVENTORY")
    print("=" * 80)
    print(
        f"Period              : "
        f"Last {DAYS_BACK} days"
    )
    print(
        f"Total failure rows  : "
        f"{len(rows)}"
    )
    print(
        f"Local output        : "
        f"{LOCAL_OUTPUT_FILE}"
    )

    if uploaded_s3_uri:
        print(
            f"S3 output           : "
            f"{uploaded_s3_uri}"
        )

    print("")
    print("FAILURES BY CATEGORY")
    print("-" * 80)

    if not category_counts:
        print("No DMS failures were found.")

    for category, count in (
        category_counts.most_common()
    ):
        print(
            f"{category}: {count}"
        )

    print("")
    print("TOP AFFECTED TABLES")
    print("-" * 80)

    if not table_counts:
        print("No affected tables were found.")

    for table_name, count in (
        table_counts.most_common(20)
    ):
        print(
            f"{table_name}: {count}"
        )

    print("=" * 80)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """
    Main Glue job execution.
    """
    print("=" * 80)
    print("STARTING DMS FAILURE INVENTORY")
    print("=" * 80)

    print(f"Glue job name : {JOB_NAME}")
    print(f"DB host       : {DB_HOST}")
    print(f"DB port       : {DB_PORT}")
    print(f"DB name       : {DB_NAME}")
    print(f"DB user       : {DB_USER}")
    print(f"Days back     : {DAYS_BACK}")

    failures = pull_failures()

    print(
        f"Retrieved {len(failures)} "
        "DMS failure rows."
    )

    write_csv(failures)

    uploaded_s3_uri = upload_csv_to_s3()

    print_summary(
        failures,
        uploaded_s3_uri,
    )

    print(
        "DMS failure inventory completed "
        "successfully."
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        main()

    except psycopg2.Error as database_error:
        print("")
        print("=" * 80)
        print("POSTGRESQL ERROR")
        print("=" * 80)
        print(
            f"Error type : "
            f"{type(database_error).__name__}"
        )
        print(
            f"Message    : "
            f"{database_error}"
        )
        print(
            f"PG code    : "
            f"{getattr(database_error, 'pgcode', None)}"
        )
        print(
            f"PG error   : "
            f"{getattr(database_error, 'pgerror', None)}"
        )
        print("")
        traceback.print_exc()

        # Re-raise the original error so Glue displays the
        # actual database failure instead of SystemExit: 1.
        raise

    except Exception as application_error:
        print("")
        print("=" * 80)
        print("APPLICATION ERROR")
        print("=" * 80)
        print(
            f"Error type : "
            f"{type(application_error).__name__}"
        )
        print(
            f"Message    : "
            f"{application_error}"
        )
        print("")
        traceback.print_exc()

        # Re-raise the original error so Glue displays the
        # actual failure.
        raise
