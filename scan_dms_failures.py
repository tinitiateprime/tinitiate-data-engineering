import base64
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

import boto3
import psycopg2  # type: ignore

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:

    def load_dotenv(*_args, **_kwargs):
        return False


import Authenticate
import AwardJson
import AwardList
import CLMIngestor
from models import AwardInfo


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# CERTIFICATE
# ============================================================

# s3://mt-dm-glue/Zscaler_Chain.pem

s3 = boto3.client("s3")

s3.download_file(
    "mt-dm-glue",
    "TSDCloudProjects_Root.pem",
    "/tmp/zscaler-cert.pem",
)

# Set certificate path
os.environ["REQUESTS_CA_BUNDLE"] = "/tmp/zscaler-cert.pem"
os.environ["SSL_CERT_FILE"] = "/tmp/zscaler-cert.pem"
os.environ["CURL_CA_BUNDLE"] = "/tmp/zscaler-cert.pem"


# ============================================================
# CONSTANTS
# ============================================================

DATE_FORMAT = "%m-%d-%Y"

DEFAULT_ERROR_REPORT_PATH = "/tmp/clm_manual_import.txt"


CONTRACT_AWARD_TYPES = [
    "Recorded%20Gsa",
    "Recorded%20Contract",
    "Recorded%20Do",
    "Recorded%20Gwac",
    "Recorded%20Boa",
    "Recorded%20Idiq",
    "Recorded%20Bpa",
    "Commercial%20Agreement",
    "Commercial%20Agreement%20Order",
]


AWARD_STATUSES = [
    "In%20Progress",
    "Pending",
    "Approved",
    "Disapproved",
    "Released",
    "Closed",
    "Canceled",
    "Pending%20Signature",
    "Pending%20Data%20Extraction",
]


# ============================================================
# JOB CONFIG
# ============================================================

@dataclass
class JobConfig:
    start_date: str | None
    end_date: str | None
    explicit_dates: bool
    clm_rest_url: str
    clm_api_key: str
    db_conn_params: dict[str, Any]
    dry_run: bool
    verify_ingest: bool
    skip_existing: bool
    error_report_uri: str
    aws_region: str | None


@dataclass
class ProcessResult:
    processed: list[AwardInfo]
    failed: list[AwardInfo]


# ============================================================
# MAIN
# ============================================================

def main(argv: list[str] | None = None) -> int:

    load_dotenv()

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # --------------------------------------------------------
    # Build configuration
    # --------------------------------------------------------

    config = build_config(argv or sys.argv)

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # START_DATE / END_DATE ARE OPTIONAL.
    #
    # If Glue does NOT pass dates, determine them automatically
    # from CLM.contract_header.
    # --------------------------------------------------------

    if config.start_date is None or config.end_date is None:

        logger.info(
            "START_DATE and END_DATE were not supplied. "
            "Determining date window automatically."
        )

        config.start_date, config.end_date = determine_date_window(
            config.db_conn_params
        )

    logger.info(
        "Starting CLM REST ingest for %s through %s",
        config.start_date,
        config.end_date,
    )

    logger.info(
        "Options: dry_run=%s verify_ingest=%s skip_existing=%s",
        config.dry_run,
        config.verify_ingest,
        config.skip_existing,
    )

    # --------------------------------------------------------
    # Authenticate
    # --------------------------------------------------------

    auth = Authenticate.Authenticate(
        config.clm_rest_url,
        config.clm_api_key,
    )

    auth_token = auth.bearer()

    if not auth_token:
        raise RuntimeError(
            "Unable to get authorization token from Unison CLM"
        )

    # --------------------------------------------------------
    # Get awards
    # --------------------------------------------------------

    awards = get_award_list(
        config,
        auth_token,
    )

    logger.info(
        "Found %s award list entries before filtering",
        len(awards),
    )

    # --------------------------------------------------------
    # Skip existing awards
    # --------------------------------------------------------

    if config.skip_existing:

        awards = filter_existing_awards(
            config.db_conn_params,
            awards,
        )

        logger.info(
            "Found %s award list entries after skip-existing filtering",
            len(awards),
        )

    # --------------------------------------------------------
    # Process awards
    # --------------------------------------------------------

    result = process_awards(
        config,
        auth,
        auth_token,
        awards,
    )

    # --------------------------------------------------------
    # Verify records made it into DB
    # --------------------------------------------------------

    missing_after_verify: list[AwardInfo] = []

    if (
        config.verify_ingest
        and not config.dry_run
        and result.processed
    ):

        missing_after_verify = verify_processed_awards(
            config.db_conn_params,
            result.processed,
        )

    # --------------------------------------------------------
    # Error report
    # --------------------------------------------------------

    error_items = result.failed + missing_after_verify

    if error_items:

        report_location = write_error_report(
            config,
            error_items,
        )

        logger.warning(
            "Manual follow-up required for %s awards: %s",
            len(error_items),
            report_location,
        )

    # --------------------------------------------------------
    # Final statistics
    # --------------------------------------------------------

    logger.info(
        "CLM REST ingest complete: "
        "requested=%s processed=%s failed=%s verified_missing=%s",
        len(awards),
        len(result.processed),
        len(result.failed),
        len(missing_after_verify),
    )

    return 1 if error_items else 0


# ============================================================
# BUILD CONFIG
# ============================================================

def build_config(argv: list[str]) -> JobConfig:

    # --------------------------------------------------------
    # IMPORTANT CHANGE
    #
    # Previously:
    #
    # raw_args, positional = parse_job_args(argv)
    #
    # and then positional arguments were validated.
    #
    # We do NOT want positional START/END dates anymore.
    # Therefore positional arguments are ignored.
    # --------------------------------------------------------

    raw_args, _ = parse_job_args(argv)

    aws_region = first_value(
        [raw_args, os.environ],
        "AWS_REGION",
        "REGION",
    )

    # --------------------------------------------------------
    # Secrets
    # --------------------------------------------------------

    secret_values = load_secret_values(
        raw_args,
        aws_region,
    )

    # --------------------------------------------------------
    # START / END DATE
    #
    # OPTIONAL
    #
    # If not supplied, main() will calculate them.
    # --------------------------------------------------------

    start_date = first_value(
        [raw_args, os.environ],
        "START_DATE",
    )

    end_date = first_value(
        [raw_args, os.environ],
        "END_DATE",
    )

    # If one is supplied, both must be supplied.
    if bool(start_date) != bool(end_date):

        raise ValueError(
            "START_DATE and END_DATE must be supplied together"
        )

    # Validate only when dates were explicitly supplied.
    if start_date and end_date:

        validate_date(start_date)
        validate_date(end_date)

    # --------------------------------------------------------
    # Dry run
    # --------------------------------------------------------

    dry_run = parse_bool(
        first_value(
            [raw_args, os.environ],
            "DRY_RUN",
        ),
        default=False,
    )

    # --------------------------------------------------------
    # Skip existing
    # --------------------------------------------------------

    skip_existing = parse_bool(
        first_value(
            [raw_args, os.environ],
            "SKIP_EXISTING",
        ),
        default=False,
    )

    # --------------------------------------------------------
    # Database required?
    #
    # Since dates aren't normally supplied, we need the DB
    # because determine_date_window() queries contract_header.
    # --------------------------------------------------------

    needs_db = (
        not dry_run
        or not (start_date and end_date)
        or skip_existing
    )

    db_conn_params = (
        build_db_conn_params(
            [
                raw_args,
                secret_values,
                os.environ,
            ]
        )
        if needs_db
        else {}
    )

    # --------------------------------------------------------
    # CLM URL
    # --------------------------------------------------------

    clm_rest_url = required_value(
        [
            raw_args,
            secret_values,
            os.environ,
        ],
        "CLM_REST_URL",
        "CLMRestURL",
        "clm_rest_url",
        "rest_url",
    )

    # --------------------------------------------------------
    # CLM API KEY
    # --------------------------------------------------------

    clm_api_key = required_value(
        [
            raw_args,
            secret_values,
            os.environ,
        ],
        "CLM_API_KEY",
        "CLMAPIKey",
        "clm_api_key",
        "api_key",
    )

    # --------------------------------------------------------
    # Return configuration
    # --------------------------------------------------------

    return JobConfig(
        start_date=start_date,
        end_date=end_date,
        explicit_dates=bool(start_date and end_date),
        clm_rest_url=clm_rest_url.rstrip("/") + "/",
        clm_api_key=clm_api_key,
        db_conn_params=db_conn_params,
        dry_run=dry_run,
        verify_ingest=parse_bool(
            first_value(
                [raw_args, os.environ],
                "VERIFY_INGEST",
            ),
            default=True,
        ),
        skip_existing=skip_existing,
        error_report_uri=(
            first_value(
                [raw_args, os.environ],
                "ERROR_REPORT_URI",
                "ERROR_REPORT_S3_URI",
            )
            or DEFAULT_ERROR_REPORT_PATH
        ),
        aws_region=aws_region,
    )


# ============================================================
# DATABASE CONNECTION PARAMETERS
# ============================================================

def build_db_conn_params(
    sources: list[Mapping[str, str]],
) -> dict[str, Any]:

    return {
        "host": required_value(
            sources,
            "DB_HOST",
            "PG_HOST",
            "host",
        ),
        "port": int(
            required_value(
                sources,
                "DB_PORT",
                "PG_PORT",
                "port",
            )
        ),
        "dbname": required_value(
            sources,
            "DB_NAME",
            "PG_DBNAME",
            "dbname",
            "database",
        ),
        "user": required_value(
            sources,
            "DB_USER",
            "PG_USER",
            "username",
            "user",
        ),
        "password": required_value(
            sources,
            "DB_PASS",
            "DB_PASSWORD",
            "PG_PASSWORD",
            "password",
        ),
    }


# ============================================================
# ARGUMENT PARSER
# ============================================================

def parse_job_args(
    argv: list[str],
) -> tuple[dict[str, str], list[str]]:

    args: dict[str, str] = {}
    positional: list[str] = []

    i = 1

    while i < len(argv):

        token = argv[i]

        if token.startswith("--"):

            key_value = token[2:]

            if "=" in key_value:

                key, value = key_value.split("=", 1)

            elif (
                i + 1 < len(argv)
                and not argv[i + 1].startswith("--")
            ):

                key, value = key_value, argv[i + 1]
                i += 1

            else:

                key, value = key_value, "true"

            args[normalize_key(key)] = value

        else:

            positional.append(token)

        i += 1

    return args, positional


# ============================================================
# NORMALIZE CONFIG KEY
# ============================================================

def normalize_key(key: str) -> str:

    return key.replace("-", "_").upper()


# ============================================================
# GET FIRST CONFIG VALUE
# ============================================================

def first_value(
    sources: list[Mapping[str, str]],
    *keys: str,
) -> str | None:

    for key in keys:

        normalized = normalize_key(key)

        for source in sources:

            for candidate in (
                key,
                normalized,
            ):

                value = source.get(candidate)

                if (
                    value is not None
                    and str(value).strip() != ""
                ):

                    return str(value)

    return None


# ============================================================
# REQUIRED CONFIG VALUE
# ============================================================

def required_value(
    sources: list[Mapping[str, str]],
    *keys: str,
) -> str:

    value = first_value(
        sources,
        *keys,
    )

    if value is None:

        raise ValueError(
            "Missing required configuration value. "
            f"Expected one of: {', '.join(keys)}"
        )

    return value


# ============================================================
# PARSE BOOLEAN
# ============================================================

def parse_bool(
    value: str | None,
    default: bool,
) -> bool:

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "t",
        "yes",
        "y",
    }


# ============================================================
# VALIDATE DATE
# ============================================================

def validate_date(value: str) -> None:

    datetime.strptime(
        value,
        DATE_FORMAT,
    )


# ============================================================
# LOAD SECRET VALUES
# ============================================================

def load_secret_values(
    raw_args: dict[str, str],
    aws_region: str | None,
) -> dict[str, str]:

    secret_ids = [
        first_value(
            [raw_args],
            "SECRET_ID",
        ),
        first_value(
            [raw_args],
            "DB_SECRET_ID",
        ),
        first_value(
            [raw_args],
            "CLM_SECRET_ID",
        ),
    ]

    values: dict[str, str] = {}

    for secret_id in [
        sid
        for sid in secret_ids
        if sid
    ]:

        values.update(
            load_json_secret(
                secret_id,
                aws_region,
            )
        )

    return values


# ============================================================
# LOAD SECRET FROM AWS SECRETS MANAGER
# ============================================================

def load_json_secret(
    secret_id: str,
    aws_region: str | None,
) -> dict[str, str]:

    client_kwargs = (
        {"region_name": aws_region}
        if aws_region
        else {}
    )

    client = boto3.client(
        "secretsmanager",
        **client_kwargs,
    )

    response = client.get_secret_value(
        SecretId=secret_id
    )

    secret_string = response.get(
        "SecretString"
    )

    if secret_string is None:

        secret_binary = response.get(
            "SecretBinary",
            b"",
        )

        secret_string = base64.b64decode(
            secret_binary
        ).decode(
            "utf-8"
        )

    secret = json.loads(secret_string)

    return {
        normalize_key(str(k)): str(v)
        for k, v in secret.items()
    }


# ============================================================
# DETERMINE DATE WINDOW
# ============================================================

def determine_date_window(
    conn_params: dict[str, Any],
) -> tuple[str, str]:

    query = """
        select TO_CHAR(min("stDate"), 'MM-DD-YYYY')
        from (
            select
                (max(cast(create_date as date)) - 1) AS "stDate"
            from "CLM".contract_header
            where create_date is not null

            union

            select
                (max(cast(status_date as date)) - 1) AS "stDate"
            from "CLM".contract_header
            where status_date is not null
        ) zz
    """

    with psycopg2.connect(
        **conn_params
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(query)

            row = cursor.fetchone()

    if row is None or row[0] is None:

        raise RuntimeError(
            "Unable to infer start date because "
            "CLM.contract_header has no create/status dates"
        )

    start_date = str(row[0])

    e_date = datetime.strptime(
        start_date,
        DATE_FORMAT,
    )

    end_date = "12-31-" + str(
        e_date.year + 1
    )

    logger.info(
        "Automatically determined date window: %s through %s",
        start_date,
        end_date,
    )

    return start_date, end_date


# ============================================================
# GET AWARD LIST
# ============================================================

def get_award_list(
    config: JobConfig,
    auth_token: str,
) -> list[AwardInfo]:

    awards: list[AwardInfo] = []

    seen: set[str] = set()

    logger.info(
        "Before get list of awards: %s",
        time.strftime(
            "%H:%M:%S",
            time.localtime(),
        ),
    )

    for award_type in CONTRACT_AWARD_TYPES:

        for award_status in AWARD_STATUSES:

            clm_date_type = date_type_for_status(
                award_status
            )

            aw_list = AwardList.AwardList(
                config.clm_rest_url,
                auth_token,
                award_type,
                award_status,
                config.start_date,
                config.end_date,
                clm_date_type,
            )

            response_text = aw_list.reqlist()

            if not response_text:

                raise RuntimeError(
                    "Empty Unison list response for "
                    f"awardType={award_type} "
                    f"status={award_status}"
                )

            response = json.loads(
                response_text
            )

            if int(
                response.get(
                    "TotalCount",
                    0,
                )
            ) <= 0:

                continue

            for item in response.get(
                "Content",
                [],
            ):

                award = award_info_from_dict(
                    item
                )

                key = award_key(
                    award
                )

                if key not in seen:

                    seen.add(key)

                    awards.append(
                        award
                    )

    logger.info(
        "After get list of awards: %s",
        time.strftime(
            "%H:%M:%S",
            time.localtime(),
        ),
    )

    return awards


# ============================================================
# DATE FIELD FOR STATUS
# ============================================================

def date_type_for_status(
    award_status: str,
) -> str:

    if award_status == "Released":
        return "ReleasedDate"

    if award_status == "Closed":
        return "ClosedDate"

    if award_status == "Canceled":
        return "CancelDate"

    return "CreateDate"


# ============================================================
# AWARD INFO
# ============================================================

def award_info_from_dict(
    item: dict[str, Any],
) -> AwardInfo:

    return AwardInfo(
        AwardNumber=str(
            item.get(
                "AwardNumber"
            )
            or ""
        ),
        ModificationNumber=str(
            item.get(
                "ModificationNumber"
            )
            or ""
        ),
        OrderNumber=str(
            item.get(
                "OrderNumber"
            )
            or ""
        ),
        ContractType=str(
            item.get(
                "ContractType"
            )
            or ""
        ),
        Status=str(
            item.get(
                "Status"
            )
            or ""
        ),
        Date=str(
            item.get(
                "Date"
            )
            or ""
        ),
    )


# ============================================================
# FILTER EXISTING AWARDS
# ============================================================

def filter_existing_awards(
    conn_params: dict[str, Any],
    awards: list[AwardInfo],
) -> list[AwardInfo]:

    keys = [
        award_key(award)
        for award in awards
    ]

    if not keys:
        return awards

    existing = fetch_existing_keys(
        conn_params,
        keys,
    )

    return [
        award
        for award in awards
        if award_key(award)
        not in existing
    ]


# ============================================================
# PROCESS AWARDS
# ============================================================

def process_awards(
    config: JobConfig,
    auth: Authenticate.Authenticate,
    auth_token: str,
    awards: list[AwardInfo],
) -> ProcessResult:

    logger.info(
        "Number of items to process: %s",
        len(awards),
    )

    processed: list[AwardInfo] = []

    failed: list[AwardInfo] = []

    ingestor = CLMIngestor.CLMIngestor(
        config.db_conn_params,
        dry_run=config.dry_run,
    )

    conn = (
        None
        if config.dry_run
        else ingestor.get_connection()
    )

    try:

        for index, award in enumerate(
            awards,
            start=1,
        ):

            # ------------------------------------------------
            # Get complete award JSON
            # ------------------------------------------------

            full_response = fetch_award_json(
                config,
                auth_token,
                award,
            )

            # ------------------------------------------------
            # Retry once with new bearer token
            # ------------------------------------------------

            if not full_response:

                logger.warning(
                    "Empty response for %s; "
                    "refreshing token and retrying",
                    award_log_label(award),
                )

                auth_token = auth.bearer()

                full_response = fetch_award_json(
                    config,
                    auth_token,
                    award,
                )

            if not full_response:

                logger.error(
                    "Unable to get award JSON for %s",
                    award_log_label(award),
                )

                failed.append(
                    award
                )

                continue

            # ------------------------------------------------
            # Parse JSON
            # ------------------------------------------------

            try:

                award_json = json.loads(
                    full_response
                )

            except json.JSONDecodeError as exc:

                logger.error(
                    "JSON parse failed for %s: %s",
                    award_log_label(award),
                    exc,
                )

                failed.append(
                    award
                )

                continue

            # ------------------------------------------------
            # Status date
            # ------------------------------------------------

            award_json.setdefault(
                "Header",
                {},
            )["StatusDate"] = award.Date

            # ------------------------------------------------
            # Insert data
            # ------------------------------------------------

            try:

                if config.dry_run:

                    ingestor.ingest(
                        award_json
                    )

                else:

                    ingestor.ingest_with_connection(
                        conn,
                        award_json,
                    )

                    conn.commit()

                processed.append(
                    award
                )

            except Exception as exc:

                if conn is not None:

                    conn.rollback()

                logger.exception(
                    "Unable to insert %s: %s",
                    award_log_label(award),
                    exc,
                )

                failed.append(
                    award
                )

            # ------------------------------------------------
            # Progress logging
            # ------------------------------------------------

            if index % 25 == 0:

                logger.info(
                    "Processed %s/%s award JSON records",
                    index,
                    len(awards),
                )

    finally:

        if conn is not None:
            conn.close()

    logger.info(
        "After get specific award data: %s",
        time.strftime(
            "%H:%M:%S",
            time.localtime(),
        ),
    )

    return ProcessResult(
        processed=processed,
        failed=failed,
    )


# ============================================================
# FETCH FULL AWARD JSON
# ============================================================

def fetch_award_json(
    config: JobConfig,
    auth_token: str,
    award: AwardInfo,
) -> str:

    full_data = AwardJson.AwardJson(
        config.clm_rest_url,
        auth_token,
        award.AwardNumber,
        award.OrderNumber,
        award.ModificationNumber,
    )

    return full_data.reqres()


# ============================================================
# VERIFY PROCESSED AWARDS
# ============================================================

def verify_processed_awards(
    conn_params: dict[str, Any],
    processed: list[AwardInfo],
) -> list[AwardInfo]:

    keys = [
        award_key(award)
        for award in processed
    ]

    existing = fetch_existing_keys(
        conn_params,
        keys,
    )

    missing = [
        award
        for award in processed
        if award_key(award)
        not in existing
    ]

    for award in missing:

        logger.warning(
            "Not found in DB after ingest: %s",
            award_key(award),
        )

    return missing


# ============================================================
# FETCH EXISTING KEYS
# ============================================================

def fetch_existing_keys(
    conn_params: dict[str, Any],
    keys: list[str],
) -> set[str]:

    if not keys:
        return set()

    query = """
        select
            award_number
            || '00'
            || coalesce(order_number, '')
            || 'MM'
            || modification_number
        from "CLM".contract_header
        where
            award_number
            || '00'
            || coalesce(order_number, '')
            || 'MM'
            || modification_number
            = ANY(%s)
    """

    with psycopg2.connect(
        **conn_params
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                query,
                (keys,),
            )

            return {
                row[0]
                for row in cursor.fetchall()
            }


# ============================================================
# WRITE ERROR REPORT
# ============================================================

def write_error_report(
    config: JobConfig,
    awards: list[AwardInfo],
) -> str:

    report_body = "".join(
        "documentNumber="
        + award.AwardNumber
        + " orderNumber="
        + award.OrderNumber
        + " versionNumber="
        + award.ModificationNumber
        + " StatusDate="
        + award.Date
        + "\n"
        for award in awards
    )

    # --------------------------------------------------------
    # Write to S3
    # --------------------------------------------------------

    if config.error_report_uri.startswith(
        "s3://"
    ):

        write_s3_text(
            config.error_report_uri,
            report_body,
            config.aws_region,
        )

        return config.error_report_uri

    # --------------------------------------------------------
    # Write locally
    # --------------------------------------------------------

    output_dir = os.path.dirname(
        config.error_report_uri
    )

    if output_dir:

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

    with open(
        config.error_report_uri,
        "w",
        encoding="utf-8",
    ) as output:

        output.write(
            report_body
        )

    return config.error_report_uri


# ============================================================
# WRITE TEXT TO S3
# ============================================================

def write_s3_text(
    uri: str,
    body: str,
    aws_region: str | None,
) -> None:

    bucket, key = parse_s3_uri(
        uri
    )

    client_kwargs = (
        {"region_name": aws_region}
        if aws_region
        else {}
    )

    client = boto3.client(
        "s3",
        **client_kwargs,
    )

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode(
            "utf-8"
        ),
    )


# ============================================================
# PARSE S3 URI
# ============================================================

def parse_s3_uri(
    uri: str,
) -> tuple[str, str]:

    path = uri.removeprefix(
        "s3://"
    )

    bucket, _, key = path.partition(
        "/"
    )

    if not bucket or not key:

        raise ValueError(
            f"Invalid S3 URI: {uri}"
        )

    return bucket, key


# ============================================================
# AWARD UNIQUE KEY
# ============================================================

def award_key(
    award: AwardInfo,
) -> str:

    return (
        award.AwardNumber
        + "00"
        + award.OrderNumber
        + "MM"
        + award.ModificationNumber
    )


# ============================================================
# AWARD LOG LABEL
# ============================================================

def award_log_label(
    award: AwardInfo,
) -> str:

    return (
        "documentNumber="
        + award.AwardNumber
        + " orderNumber="
        + award.OrderNumber
        + " versionNumber="
        + award.ModificationNumber
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        raise SystemExit(
            main()
        )

    except Exception as exc:

        logger.exception(
            "CLM REST ingest failed: %s",
            exc,
        )

        raise
