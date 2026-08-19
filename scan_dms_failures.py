from pathlib import Path


# ============================================================
# ROOT DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MAIN_FUNCTION_ROOT = (
    BASE_DIR
    / "main-function"
)

SRC_ROOT = (
    MAIN_FUNCTION_ROOT
    / "mt-dm-lambda-src"
)

TEST_ROOT = (
    MAIN_FUNCTION_ROOT
    / "tests"
    / "unit"
)


# ============================================================
# PROJECT FINANCIAL TEMPLATE FILES
# ============================================================
# These are your already-working unit tests.
# The generator copies/transforms these.
# ============================================================

TEMPLATE_FILES = {
    "db": (
        TEST_ROOT
        / "db"
        / "test_project_financial_repo.py"
    ),

    "model": (
        TEST_ROOT
        / "domain"
        / "models"
        / "test_project_financial.py"
    ),

    "service": (
        TEST_ROOT
        / "domain"
        / "services"
        / "test_project_financial_service.py"
    ),

    "handler": (
        TEST_ROOT
        / "v1"
        / "test_project_financial.py"
    ),
}


# ============================================================
# DESTINATION DIRECTORIES
# ============================================================

DESTINATION_DIRS = {
    "db": (
        TEST_ROOT
        / "db"
    ),

    "model": (
        TEST_ROOT
        / "domain"
        / "models"
    ),

    "service": (
        TEST_ROOT
        / "domain"
        / "services"
    ),

    "handler": (
        TEST_ROOT
        / "v1"
    ),
}


# ============================================================
# TEST TYPES
# ============================================================

TEST_TYPES = (
    "db",
    "model",
    "service",
    "handler",
)


# ============================================================
# API CONFIGURATION
# ============================================================
#
# For every new API:
#
# 1. Add one entry here.
# 2. Set key_column.
# 3. Set lookup functions.
# 4. Set source view.
# 5. Set sample values.
#
# Generator does not need to change.
# ============================================================

APIS = {

    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================

    "po_funding_detail": {

        # ----------------------------------------------------
        # Naming
        # ----------------------------------------------------

        "module_name": "po_funding_detail",

        "route_name": "po-funding-detail",

        "plural_name": "po_funding_detail",


        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------

        "key_column": "project_id",

        "sample_key": "P-1001",


        # ----------------------------------------------------
        # Sample field used in tests
        # ----------------------------------------------------

        "sample_field": "vendor_name",

        "sample_value": "Test Vendor",


        # ----------------------------------------------------
        # Source materialized view
        # ----------------------------------------------------

        "source_view": "po_funding_detail_vw",


        # ----------------------------------------------------
        # Actual repository functions
        # ----------------------------------------------------

        "repo_list_function": (
            "get_po_funding_detail"
        ),

        "repo_lookup_function": (
            "get_po_funding_detail_by_project_id"
        ),


        # ----------------------------------------------------
        # Actual service functions
        # ----------------------------------------------------

        "service_search_function": (
            "search_po_funding_detail"
        ),

        "service_lookup_function": (
            "get_po_funding_detail_by_project"
        ),


        # ----------------------------------------------------
        # Actual handler functions
        # ----------------------------------------------------

        "handler_search_function": (
            "search_po_funding_detail_v1"
        ),

        "handler_lookup_function": (
            "get_po_funding_detail_details"
        ),


        # ----------------------------------------------------
        # Function signature behavior
        # ----------------------------------------------------
        #
        # Your actual service lookup:
        #
        # def get_po_funding_detail_by_project(
        #     project_id,
        #     page=None,
        #     sort=None,
        #     columns=None,
        # )
        #
        # It DOES NOT accept filters.
        # ----------------------------------------------------

        "lookup_supports_filters": False,

        "lookup_supports_page": True,

        "lookup_supports_sort": True,

        "lookup_supports_columns": True,


        # ----------------------------------------------------
        # Default sort
        # ----------------------------------------------------

        "default_sort_field": "order_date",

        "default_sort_order": "desc",


        # ----------------------------------------------------
        # Sample columns
        # ----------------------------------------------------

        "sample_columns": [
            "project_id",
            "vendor_name",
        ],


        # ----------------------------------------------------
        # Sample object
        # ----------------------------------------------------

        "sample_item": {
            "project_id": "P-1001",
            "vendor_name": "Test Vendor",
        },


        # ----------------------------------------------------
        # Text replacements
        # ----------------------------------------------------
        #
        # First generic Project Financial replacements happen.
        # These API-specific replacements happen afterwards.
        # ----------------------------------------------------

        "replacements": {

            # names
            "project_financial": "po_funding_detail",
            "project_financials": "po_funding_detail",

            "ProjectFinancial": "PoFundingDetail",
            "ProjectFinancials": "PoFundingDetails",

            "PROJECT_FINANCIAL": "PO_FUNDING_DETAIL",
            "PROJECT_FINANCIALS": "PO_FUNDING_DETAIL",

            # key
            "proj_id": "project_id",

            # repository
            "get_project_financials":
                "get_po_funding_detail",

            "get_project_financial_by_id":
                "get_po_funding_detail_by_project_id",

            # service
            "search_project_financials":
                "search_po_funding_detail",

            "get_project_financial_details":
                "get_po_funding_detail_by_project",

            # handler
            "search_project_financials_v1":
                "search_po_funding_detail_v1",

            # source view
            "project_financials_source_vw":
                "po_funding_detail_vw",

            # sample field
            "proj_name":
                "vendor_name",

            "Test Project":
                "Test Vendor",

            # sort
            'field="proj_name"':
                'field="vendor_name"',

            # sample key
            "P-1001":
                "P-1001",
        },
    },
}

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Generator
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
import re
import sys
from pathlib import Path

from api_test_config import (
    APIS,
    TEMPLATE_FILES,
    DESTINATION_DIRS,
    TEST_TYPES,
)


# ============================================================
# UTILITIES
# ============================================================


def print_separator():
    print("=" * 78)


def validate_api(api_name: str) -> dict:

    if api_name not in APIS:

        print()
        print(f"ERROR: Unknown API: {api_name}")
        print()
        print("Configured APIs:")

        for name in APIS:
            print(f"  - {name}")

        sys.exit(1)

    return APIS[api_name]


def validate_templates():

    missing = []

    for test_type in TEST_TYPES:

        path = TEMPLATE_FILES[test_type]

        if not path.exists():
            missing.append(
                f"{test_type}: {path}"
            )

    if missing:

        print()
        print("ERROR: Missing template files:")
        print()

        for item in missing:
            print(f"  {item}")

        print()
        print(
            "The generator requires the existing "
            "project_financial unit tests."
        )

        sys.exit(1)


# ============================================================
# DESTINATION FILE NAMES
# ============================================================


def get_destination_file(
    api_name: str,
    test_type: str,
) -> Path:

    module_name = APIS[api_name]["module_name"]

    if test_type == "db":

        filename = (
            f"test_{module_name}_repo.py"
        )

    elif test_type == "model":

        filename = (
            f"test_{module_name}.py"
        )

    elif test_type == "service":

        filename = (
            f"test_{module_name}_service.py"
        )

    elif test_type == "handler":

        filename = (
            f"test_{module_name}.py"
        )

    else:

        raise ValueError(
            f"Unknown test type: {test_type}"
        )

    return (
        DESTINATION_DIRS[test_type]
        / filename
    )


# ============================================================
# BASIC REPLACEMENTS
# ============================================================


def apply_basic_replacements(
    text: str,
    config: dict,
) -> str:

    replacements = config.get(
        "replacements",
        {},
    )

    # longest first prevents partial replacement problems
    ordered = sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for old, new in ordered:
        text = text.replace(
            old,
            new,
        )

    return text


# ============================================================
# REMOVE LOOKUP FILTER ARGUMENT
# ============================================================
#
# Project Financial lookup tests may contain:
#
# get_xxx(
#     project_id="...",
#     filters=filters,
# )
#
# PO Funding lookup doesn't accept filters.
# ============================================================


def remove_filters_from_lookup_calls(
    text: str,
    service_lookup_function: str,
) -> str:

    patterns = [

        # filters=filters
        rf"""
        ({re.escape(service_lookup_function)}
        \(
        .*?)
        \n\s*filters\s*=\s*filters\s*,?
        """,

        # filters=None
        rf"""
        ({re.escape(service_lookup_function)}
        \(
        .*?)
        \n\s*filters\s*=\s*None\s*,?
        """,
    ]

    for pattern in patterns:

        text = re.sub(
            pattern,
            r"\1",
            text,
            flags=(
                re.MULTILINE
                | re.DOTALL
                | re.VERBOSE
            ),
        )

    return text


# ============================================================
# REMOVE FILTER-SPECIFIC LOOKUP TESTS
# ============================================================
#
# Instead of generating tests that are impossible for this
# function signature, remove them.
# ============================================================


def remove_lookup_filter_tests(
    text: str,
    service_lookup_function: str,
) -> str:

    test_patterns = [

        r"""
        \ndef\s+
        test_get_[A-Za-z0-9_]+
        _with_filter_group
        \(.*?
        (?=
            \ndef\s+
            |\Z
        )
        """,

        r"""
        \ndef\s+
        test_get_[A-Za-z0-9_]+
        _with_existing_envelope
        \(.*?
        (?=
            \ndef\s+
            |\Z
        )
        """,

        r"""
        \ndef\s+
        test_get_[A-Za-z0-9_]+
        _filters_normalization
        \(.*?
        (?=
            \ndef\s+
            |\Z
        )
        """,
    ]

    for pattern in test_patterns:

        text = re.sub(
            pattern,
            "\n",
            text,
            flags=(
                re.MULTILINE
                | re.DOTALL
                | re.VERBOSE
            ),
        )

    return text


# ============================================================
# FIX PAGINATION CALLS
# ============================================================
#
# Converts:
#
# func(
#     project_id="P-1001",
#     limit=25,
#     cursor="current-cursor",
# )
#
# to:
#
# page = PaginationModel(
#     limit=25,
#     cursor="current-cursor",
# )
#
# func(
#     project_id="P-1001",
#     page=page,
# )
# ============================================================


def convert_limit_cursor_to_page(
    text: str,
    service_lookup_function: str,
) -> str:

    # --------------------------------------------------------
    # First remove direct limit / cursor arguments
    # --------------------------------------------------------

    text = re.sub(
        r"\n(\s*)limit\s*=\s*(\d+)\s*,",
        "",
        text,
    )

    text = re.sub(
        r'\n(\s*)cursor\s*=\s*"([^"]*)"\s*,',
        "",
        text,
    )

    # --------------------------------------------------------
    # Ensure page=page exists for pagination lookup tests.
    #
    # Only applied to tests containing PaginationModel.
    # --------------------------------------------------------

    blocks = re.split(
        r"(?=\ndef\s+test_)",
        text,
    )

    updated_blocks = []

    for block in blocks:

        if (
            service_lookup_function
            in block
            and "PaginationModel(" in block
            and "page=" not in block
        ):

            pattern = (
                rf"({re.escape(service_lookup_function)}"
                rf"\(\s*\n(?:.*?)project_id\s*=\s*[^,\n]+,)"
            )

            block = re.sub(
                pattern,
                r"\1\n        page=page,",
                block,
                count=1,
                flags=re.DOTALL,
            )

        updated_blocks.append(
            block
        )

    return "".join(
        updated_blocks
    )


# ============================================================
# FIX MOCK RETURN VALUES
# ============================================================
#
# Main issue you hit:
#
# MagicMock .get("page").get("cursor")
#
# returns another MagicMock.
#
# We normalize generated repository mock responses to:
#
# {
#   "items": [...],
#   "page": {
#       "cursor": None,
#       "has_more": False
#   }
# }
# ============================================================


def normalize_mock_page_response(
    text: str,
) -> str:

    # convert old "page": {} into safe metadata

    text = re.sub(
        r'"page"\s*:\s*\{\s*\}',
        (
            '"page": {\n'
            '            "cursor": None,\n'
            '            "has_more": False,\n'
            '        }'
        ),
        text,
    )

    return text


# ============================================================
# SERVICE FUNCTION PATCH
# ============================================================


def patch_service_tests(
    text: str,
    config: dict,
) -> str:

    lookup_function = config[
        "service_lookup_function"
    ]

    supports_filters = config.get(
        "lookup_supports_filters",
        True,
    )

    if not supports_filters:

        text = remove_filters_from_lookup_calls(
            text,
            lookup_function,
        )

        text = remove_lookup_filter_tests(
            text,
            lookup_function,
        )

    if config.get(
        "lookup_supports_page",
        False,
    ):

        text = convert_limit_cursor_to_page(
            text,
            lookup_function,
        )

    text = normalize_mock_page_response(
        text
    )

    return text


# ============================================================
# MODEL TEST PATCH
# ============================================================


def patch_model_tests(
    text: str,
    config: dict,
) -> str:

    lookup_function = config[
        "service_lookup_function"
    ]

    supports_filters = config.get(
        "lookup_supports_filters",
        True,
    )

    if not supports_filters:

        text = remove_filters_from_lookup_calls(
            text,
            lookup_function,
        )

        text = remove_lookup_filter_tests(
            text,
            lookup_function,
        )

    text = normalize_mock_page_response(
        text
    )

    return text


# ============================================================
# DB TEST PATCH
# ============================================================


def patch_db_tests(
    text: str,
    config: dict,
) -> str:

    repo_lookup = config[
        "repo_lookup_function"
    ]

    supports_filters = config.get(
        "lookup_supports_filters",
        True,
    )

    if not supports_filters:

        text = remove_filters_from_lookup_calls(
            text,
            repo_lookup,
        )

        text = remove_lookup_filter_tests(
            text,
            repo_lookup,
        )

    text = normalize_mock_page_response(
        text
    )

    return text


# ============================================================
# HANDLER PATCH
# ============================================================


def patch_handler_tests(
    text: str,
    config: dict,
) -> str:

    text = normalize_mock_page_response(
        text
    )

    return text


# ============================================================
# FINAL PATCH
# ============================================================


def apply_test_type_patches(
    text: str,
    test_type: str,
    config: dict,
) -> str:

    if test_type == "db":

        return patch_db_tests(
            text,
            config,
        )

    if test_type == "model":

        return patch_model_tests(
            text,
            config,
        )

    if test_type == "service":

        return patch_service_tests(
            text,
            config,
        )

    if test_type == "handler":

        return patch_handler_tests(
            text,
            config,
        )

    return text


# ============================================================
# GENERATE SINGLE TEST FILE
# ============================================================


def generate_test_file(
    api_name: str,
    test_type: str,
    force: bool = False,
    dry_run: bool = False,
) -> str:

    config = APIS[api_name]

    template = TEMPLATE_FILES[
        test_type
    ]

    destination = get_destination_file(
        api_name,
        test_type,
    )

    if destination.exists() and not force:

        print(
            f"SKIP   [{test_type:<7}] "
            f"{destination}"
        )

        return "skipped"

    text = template.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Generic replacements
    # --------------------------------------------------------

    text = apply_basic_replacements(
        text,
        config,
    )

    # --------------------------------------------------------
    # Test-type specific corrections
    # --------------------------------------------------------

    text = apply_test_type_patches(
        text,
        test_type,
        config,
    )

    if dry_run:

        print(
            f"DRY    [{test_type:<7}] "
            f"{destination}"
        )

        return "generated"

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        text,
        encoding="utf-8",
    )

    print(
        f"CREATE [{test_type:<7}] "
        f"{destination}"
    )

    return "generated"


# ============================================================
# GENERATE ONE API
# ============================================================


def generate_api(
    api_name: str,
    force: bool = False,
    dry_run: bool = False,
):

    config = validate_api(
        api_name
    )

    validate_templates()

    print()
    print_separator()

    print(
        f"Generating tests for API: "
        f"{api_name}"
    )

    print(
        f"Key column: "
        f"{config['key_column']}"
    )

    print(
        f"Lookup function: "
        f"{config['service_lookup_function']}"
    )

    print_separator()

    generated = 0
    skipped = 0

    for test_type in TEST_TYPES:

        result = generate_test_file(
            api_name,
            test_type,
            force=force,
            dry_run=dry_run,
        )

        if result == "generated":
            generated += 1

        elif result == "skipped":
            skipped += 1

    print()

    print(
        f"Generated: {generated}"
    )

    print(
        f"Skipped:   {skipped}"
    )

    print()


# ============================================================
# LIST APIS
# ============================================================


def list_apis():

    print()
    print("Configured APIs")
    print_separator()

    for api_name, config in APIS.items():

        print(
            f"{api_name:<30} "
            f"key={config['key_column']:<20} "
            f"lookup={config['service_lookup_function']}"
        )

    print()


# ============================================================
# COMMAND LINE
# ============================================================


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests using "
            "project_financial tests as templates."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help="API configuration name",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured APIs",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show files without writing",
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================


def main():

    args = parse_args()

    if args.list:

        list_apis()
        return

    if not args.api:

        print()
        print(
            "ERROR: API name is required."
        )

        print()
        print(
            "Example:"
        )

        print(
            "  py generate_api_tests.py "
            "po_funding_detail"
        )

        print()
        print(
            "Or:"
        )

        print(
            "  py generate_api_tests.py "
            "--list"
        )

        return

    generate_api(
        api_name=args.api,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
