# scan_dms_failures.py

import boto3
import re
import csv
from datetime import datetime, timedelta, timezone

REGION = "us-gov-west-1"
LOG_GROUP_NAME = "dms-tasks-postgres-migration-instance"
DAYS_BACK = 30
OUTPUT_FILE = "dms_failure_inventory.csv"


CATEGORY_PATTERNS = {
    "column/type drift on source": [
        "column",
        "does not exist",
        "relation",
        "type mismatch",
        "datatype",
        "invalid input syntax",
        "extra data after last expected column",
        "schema",
        "table definition",
        "missing column",
    ],
    "dependent object lock during matview refresh": [
        "lock",
        "deadlock",
        "lock timeout",
        "could not obtain lock",
        "materialized view",
        "matview",
        "refresh materialized view",
    ],
    "permission/ownership issue": [
        "permission denied",
        "must be owner",
        "insufficient privilege",
        "access denied",
        "not authorized",
        "owner of relation",
    ],
}


def classify_error(message):
    msg = message.lower()

    for category, keywords in CATEGORY_PATTERNS.items():
        for keyword in keywords:
            if keyword in msg:
                return category

    if "sql_error" in msg or "check target database logs" in msg:
        return "unknown - need target postgres logs"

    return "unknown"


def extract_table(message):
    patterns = [
        r"Table '([^']+)'",
        r'table "([^"]+)"',
        r"relation \"([^\"]+)\"",
        r"relation '([^']+)'",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""


def scan_logs():
    client = boto3.client("logs", region_name=REGION)

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=DAYS_BACK)

    start_ms = int(start_time.timestamp() * 1000)
    end_ms = int(end_time.timestamp() * 1000)

    filter_pattern = "error failed permission lock column relation materialized owner"

    results = []
    next_token = None

    while True:
        params = {
            "logGroupName": LOG_GROUP_NAME,
            "startTime": start_ms,
            "endTime": end_ms,
            "filterPattern": filter_pattern,
            "limit": 100,
        }

        if next_token:
            params["nextToken"] = next_token

        response = client.filter_log_events(**params)

        for event in response.get("events", []):
            message = event.get("message", "").strip()

            if not message:
                continue

            timestamp = datetime.fromtimestamp(
                event["timestamp"] / 1000,
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S UTC")

            results.append({
                "timestamp": timestamp,
                "log_stream": event.get("logStreamName", ""),
                "table": extract_table(message),
                "category": classify_error(message),
                "message": message.replace("\n", " ")
            })

        next_token = response.get("nextToken")

        if not next_token:
            break

    return results


def write_csv(rows):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "log_stream",
                "table",
                "category",
                "message",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = scan_logs()
    write_csv(rows)

    print(f"Done. Found {len(rows)} log records.")
    print(f"Output file: {OUTPUT_FILE}")
