# api_test_config.py

from pathlib import Path


# ============================================================
# ROOT DIRECTORIES
# ============================================================

API_ROOT = Path(__file__).resolve().parent

MAIN_FUNCTION_ROOT = API_ROOT / "main-function"

TEST_ROOT = (
    MAIN_FUNCTION_ROOT
    / "tests"
    / "unit"
)


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
# PROJECT FINANCIAL TEMPLATE FILES
#
# These are the known-good tests that are used as templates.
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
# TEMPLATE BASE INFORMATION
#
# This tells the generator what names belong to the
# Project Financial template.
# ============================================================

TEMPLATE_BASE = {
    "module_name": "project_financial",

    "plural_name": "project_financials",

    "route_name": "project-financials",

    "class_name": "ProjectFinancial",

    "repository_module": "project_financial_repo",

    "service_module": "project_financial_service",

    # Search service/repository function
    "search_function": "search_project_financial",

    # Key lookup service/repository function
    "lookup_function": "get_project_financial_by_project_id",

    # Handler functions
    "search_handler": "search_project_financials_v1",

    "lookup_handler": "get_project_financial_details",

    "key_column": "project_id",

    "sample_key": "P-1001",

    "sample_field": "customer_name",

    "sample_value": "Test Customer",
}


# ============================================================
# API CONFIGURATION
#
# ADD FUTURE APIs HERE.
#
# You should NOT need to modify generate_api_tests.py.
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

        "plural_name": "po_funding_details",

        "route_name": "po-funding-detail",

        "class_name": "PoFundingDetail",

        # ----------------------------------------------------
        # Source object
        # ----------------------------------------------------

        "source_view": "po_funding_detail_vw",

        # ----------------------------------------------------
        # Primary/key column
        # ----------------------------------------------------

        "key_column": "project_id",

        "sample_key": "P-1001",

        # ----------------------------------------------------
        # Sample field used by tests
        # ----------------------------------------------------

        "sample_field": "vendor_name",

        "sample_value": "Test Vendor",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------

        "repository_module": "po_funding_detail_repo",

        "search_function": "get_po_funding_detail",

        "lookup_function": "get_po_funding_detail_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------

        "service_module": "po_funding_detail_service",

        "service_search_function": "search_po_funding_detail",

        "service_lookup_function": "get_po_funding_detail_by_project",

        # ----------------------------------------------------
        # Handler
        #
        # IMPORTANT:
        # These names must match the REAL functions in:
        #
        # mt-dm-lambda-src/v1/handlers/po_funding_detail.py
        #
        # From your screenshots the search handler is:
        #
        # search_po_funding_detail_v1
        #
        # ----------------------------------------------------

        "handler_module": "po_funding_detail",

        "search_handler": "search_po_funding_detail_v1",

        # Change this ONLY if your actual handler has a
        # different function name.
        "lookup_handler": "get_po_funding_detail_by_project_v1",

        # ----------------------------------------------------
        # Defaults used by generated tests
        # ----------------------------------------------------

        "default_sort_field": "order_date",

        "default_sort_order": "desc",

        "default_page_size": 100,

        # ----------------------------------------------------
        # Test data
        # ----------------------------------------------------

        "sample_record": {
            "project_id": "P-1001",
            "vendor_name": "Test Vendor",
        },

        # ----------------------------------------------------
        # Extra direct replacements
        #
        # Normally this can remain empty.
        # Add entries only for unusual APIs.
        # ----------------------------------------------------

        "replacements": {
        },
    },


    # ========================================================
    # GL DETAILS
    #
    # Keep this if you want to test it later.
    # ========================================================

    "gl_details": {

        "module_name": "gl_details",

        "plural_name": "gl_details",

        "route_name": "gl-details",

        "class_name": "GlDetails",

        "source_view": "gl_details_vw",

        "key_column": "proj_id",

        "sample_key": "1001",

        "sample_field": "description",

        "sample_value": "Test GL Detail",

        "repository_module": "gl_details_repo",

        "search_function": "get_gl_details",

        "lookup_function": "get_gl_details_by_id",

        "service_module": "gl_details_service",

        "service_search_function": "search_gl_details",

        "service_lookup_function": "get_gl_details_by_id",

        "handler_module": "gl_details",

        "search_handler": "search_gl_details_v1",

        "lookup_handler": "get_gl_details_v1",

        "default_sort_field": "proj_id",

        "default_sort_order": "asc",

        "default_page_size": 100,

        "sample_record": {
            "proj_id": "1001",
            "description": "Test GL Detail",
        },

        "replacements": {
        },
    },
}


# ============================================================
# OPTIONAL COMPATIBILITY ALIASES
#
# These prevent the import errors you were receiving earlier:
#
#   cannot import name TEMPLATE_FILES
#   cannot import name DESTINATIONS
#
# ============================================================

TEMPLATES = TEMPLATE_FILES

DESTINATIONS = DESTINATION_DIRS



+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# generate_api_tests.py

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional


from api_test_config import (
    APIS,
    TEMPLATE_BASE,
    TEMPLATE_FILES,
    DESTINATION_DIRS,
    TEST_TYPES,
)


# ============================================================
# CONSTANTS
# ============================================================

VALID_TEST_TYPES = set(TEST_TYPES)


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_api_name(value: str) -> str:
    """
    Normalize API name supplied on command line.

    Example:
        po-funding-detail
        PO Funding Detail
        po_funding_detail

    all become:

        po_funding_detail
    """

    value = value.strip().lower()

    value = re.sub(
        r"[\s\-]+",
        "_",
        value,
    )

    value = re.sub(
        r"_+",
        "_",
        value,
    )

    return value.strip("_")


def snake_to_pascal(value: str) -> str:
    """
    po_funding_detail -> PoFundingDetail
    """

    return "".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def snake_to_title(value: str) -> str:
    """
    po_funding_detail -> Po Funding Detail
    """

    return " ".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
    )


def write_text(
    path: Path,
    content: str,
) -> None:

    ensure_parent(path)

    path.write_text(
        content,
        encoding="utf-8",
    )


# ============================================================
# CONFIG VALIDATION
# ============================================================

def require_config_value(
    api_name: str,
    config: dict,
    key: str,
) -> object:

    if key not in config:
        raise ValueError(
            f"API '{api_name}' is missing required "
            f"configuration value: {key}"
        )

    value = config[key]

    if value is None:
        raise ValueError(
            f"API '{api_name}' has None for required "
            f"configuration value: {key}"
        )

    return value


def validate_api_config(
    api_name: str,
    config: dict,
) -> None:

    required = [
        "module_name",
        "plural_name",
        "route_name",
        "class_name",
        "source_view",
        "key_column",
        "sample_key",
        "sample_field",
        "sample_value",
        "repository_module",
        "search_function",
        "lookup_function",
        "service_module",
        "service_search_function",
        "service_lookup_function",
        "handler_module",
        "search_handler",
        "lookup_handler",
    ]

    for key in required:
        require_config_value(
            api_name,
            config,
            key,
        )


# ============================================================
# CONFIG DISPLAY
# ============================================================

def list_apis() -> None:

    print()
    print("Configured APIs")
    print("=" * 78)

    if not APIS:
        print("No APIs configured.")
        return

    for api_name, config in APIS.items():

        key_column = config.get(
            "key_column",
            "<not configured>",
        )

        lookup_function = config.get(
            "lookup_function",
            "<not configured>",
        )

        print(
            f"{api_name:<30}"
            f" key={key_column:<20}"
            f" lookup={lookup_function}"
        )

    print()


# ============================================================
# DESTINATION FILE NAMES
# ============================================================

def destination_file(
    test_type: str,
    api_config: dict,
) -> Path:

    module_name = api_config["module_name"]

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
            f"Unsupported test type: {test_type}"
        )

    return (
        DESTINATION_DIRS[test_type]
        / filename
    )


# ============================================================
# SAFE TEXT REPLACEMENT
#
# IMPORTANT:
#
# We do replacements ONCE from the original template.
#
# We do NOT repeatedly replace generated values.
#
# This is what prevents:
#
#     search_po_funding_detail_v1_v1_v1
#
# and:
#
#     get_po_funding_detail_details
#
# ============================================================

def replace_identifier(
    source: str,
    old: str,
    new: str,
) -> str:

    if not old:
        return source

    if old == new:
        return source

    pattern = (
        r"(?<![A-Za-z0-9_])"
        + re.escape(old)
        + r"(?![A-Za-z0-9_])"
    )

    return re.sub(
        pattern,
        lambda _: new,
        source,
    )


def replace_plain(
    source: str,
    old: str,
    new: str,
) -> str:

    if not old:
        return source

    if old == new:
        return source

    return source.replace(
        old,
        new,
    )


# ============================================================
# REPLACEMENT MAP
# ============================================================

def build_replacements(
    api_config: dict,
) -> Dict[str, str]:

    target_module = api_config["module_name"]
    target_plural = api_config["plural_name"]
    target_route = api_config["route_name"]
    target_class = api_config["class_name"]

    replacements = {

        # ----------------------------------------------------
        # Handler functions FIRST
        #
        # These are exact names.
        # ----------------------------------------------------

        TEMPLATE_BASE["search_handler"]:
            api_config["search_handler"],

        TEMPLATE_BASE["lookup_handler"]:
            api_config["lookup_handler"],

        # ----------------------------------------------------
        # Service functions
        # ----------------------------------------------------

        TEMPLATE_BASE["search_function"]:
            api_config["service_search_function"],

        TEMPLATE_BASE["lookup_function"]:
            api_config["service_lookup_function"],

        # ----------------------------------------------------
        # Repository/service modules
        # ----------------------------------------------------

        TEMPLATE_BASE["repository_module"]:
            api_config["repository_module"],

        TEMPLATE_BASE["service_module"]:
            api_config["service_module"],

        # ----------------------------------------------------
        # Class names
        # ----------------------------------------------------

        TEMPLATE_BASE["class_name"]:
            target_class,

        # Common Project Financial class variants
        "ProjectFinancialResponse":
            f"{target_class}Response",

        "ProjectFinancialSearchResponse":
            f"{target_class}SearchResponse",

        "ProjectFinancialSearchServiceResponse":
            f"{target_class}SearchServiceResponse",

        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------

        TEMPLATE_BASE["key_column"]:
            api_config["key_column"],

        TEMPLATE_BASE["sample_key"]:
            str(api_config["sample_key"]),

        # ----------------------------------------------------
        # Sample data
        # ----------------------------------------------------

        TEMPLATE_BASE["sample_field"]:
            api_config["sample_field"],

        TEMPLATE_BASE["sample_value"]:
            str(api_config["sample_value"]),

        # ----------------------------------------------------
        # Route
        # ----------------------------------------------------

        TEMPLATE_BASE["route_name"]:
            target_route,

        # ----------------------------------------------------
        # Plural module name BEFORE singular
        # ----------------------------------------------------

        TEMPLATE_BASE["plural_name"]:
            target_plural,

        TEMPLATE_BASE["module_name"]:
            target_module,
    }

    extra = api_config.get(
        "replacements",
        {},
    )

    if extra:
        replacements.update(extra)

    return replacements


# ============================================================
# CORE TEMPLATE TRANSFORMATION
# ============================================================

def transform_template(
    source: str,
    api_config: dict,
) -> str:

    replacements = build_replacements(
        api_config
    )

    # --------------------------------------------------------
    # Very important:
    #
    # Sort by longest original token first.
    #
    # Example:
    #
    # project_financials
    # project_financial
    #
    # must be replaced in this order.
    # --------------------------------------------------------

    ordered = sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    result = source

    for old, new in ordered:

        result = replace_plain(
            result,
            old,
            str(new),
        )

    return result


# ============================================================
# CLEAN DUPLICATED GENERATED NAMES
#
# This is intentionally conservative.
#
# It is a safety net only.
# ============================================================

def clean_duplicate_suffixes(
    source: str,
) -> str:

    # _v1_v1_v1 -> _v1
    source = re.sub(
        r"(?:_v1){2,}",
        "_v1",
        source,
    )

    # _details_details -> _details
    source = re.sub(
        r"(?:_details){2,}",
        "_details",
        source,
    )

    # _service_service -> _service
    source = re.sub(
        r"(?:_service){2,}",
        "_service",
        source,
    )

    # _repo_repo -> _repo
    source = re.sub(
        r"(?:_repo){2,}",
        "_repo",
        source,
    )

    return source


# ============================================================
# HANDLER-SPECIFIC CORRECTIONS
#
# Instead of guessing handler names from the API name,
# use the configured handler names directly.
# ============================================================

def fix_handler_names(
    source: str,
    api_config: dict,
) -> str:

    search_handler = api_config[
        "search_handler"
    ]

    lookup_handler = api_config[
        "lookup_handler"
    ]

    module_name = api_config[
        "module_name"
    ]

    # --------------------------------------------------------
    # Remove malformed generated search handler variants
    # --------------------------------------------------------

    bad_search_patterns = [
        rf"search_{re.escape(module_name)}(?:_v1)+",
        rf"search_{re.escape(module_name)}s(?:_v1)+",
    ]

    for pattern in bad_search_patterns:

        source = re.sub(
            pattern,
            search_handler,
            source,
        )

    # --------------------------------------------------------
    # Remove malformed details handler variants
    # --------------------------------------------------------

    bad_lookup_patterns = [
        rf"get_{re.escape(module_name)}(?:_details)+",
        rf"get_{re.escape(module_name)}_by_project(?:_v1)+",
        rf"get_{re.escape(module_name)}_by_project_id(?:_v1)+",
    ]

    for pattern in bad_lookup_patterns:

        source = re.sub(
            pattern,
            lookup_handler,
            source,
        )

    return source


# ============================================================
# SERVICE-SPECIFIC CORRECTIONS
# ============================================================

def fix_service_names(
    source: str,
    api_config: dict,
) -> str:

    module_name = api_config[
        "module_name"
    ]

    search_function = api_config[
        "service_search_function"
    ]

    lookup_function = api_config[
        "service_lookup_function"
    ]

    # Known generic forms that may remain after template
    # replacement.

    source = re.sub(
        rf"\bsearch_{re.escape(module_name)}s\b",
        search_function,
        source,
    )

    source = re.sub(
        rf"\bget_{re.escape(module_name)}_details\b",
        lookup_function,
        source,
    )

    return source


# ============================================================
# REPOSITORY-SPECIFIC CORRECTIONS
# ============================================================

def fix_repository_names(
    source: str,
    api_config: dict,
) -> str:

    module_name = api_config[
        "module_name"
    ]

    search_function = api_config[
        "search_function"
    ]

    lookup_function = api_config[
        "lookup_function"
    ]

    source = re.sub(
        rf"\bget_{re.escape(module_name)}_details\b",
        lookup_function,
        source,
    )

    return source


# ============================================================
# MODEL-SPECIFIC CORRECTIONS
# ============================================================

def fix_model_names(
    source: str,
    api_config: dict,
) -> str:

    class_name = api_config[
        "class_name"
    ]

    # A final consistency pass for common model names.

    source = source.replace(
        "ProjectFinancial",
        class_name,
    )

    return source


# ============================================================
# POST PROCESS
# ============================================================

def post_process(
    test_type: str,
    source: str,
    api_config: dict,
) -> str:

    source = clean_duplicate_suffixes(
        source
    )

    if test_type == "db":

        source = fix_repository_names(
            source,
            api_config,
        )

    elif test_type == "model":

        source = fix_model_names(
            source,
            api_config,
        )

    elif test_type == "service":

        source = fix_service_names(
            source,
            api_config,
        )

    elif test_type == "handler":

        source = fix_handler_names(
            source,
            api_config,
        )

    source = clean_duplicate_suffixes(
        source
    )

    return source


# ============================================================
# TEMPLATE VALIDATION
# ============================================================

def validate_templates(
    selected_types: Iterable[str],
) -> None:

    missing = []

    for test_type in selected_types:

        path = TEMPLATE_FILES[
            test_type
        ]

        if not path.exists():

            missing.append(
                (
                    test_type,
                    path,
                )
            )

    if not missing:
        return

    print()
    print(
        "ERROR: Missing template files:"
    )
    print()

    for test_type, path in missing:

        print(
            f"  {test_type:<10} {path}"
        )

    print()
    print(
        "The generator requires the existing "
        "project_financial tests."
    )

    raise FileNotFoundError(
        "One or more template files are missing."
    )


# ============================================================
# GENERATE ONE TEST FILE
# ============================================================

def generate_one(
    test_type: str,
    api_config: dict,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> str:

    template_path = TEMPLATE_FILES[
        test_type
    ]

    destination = destination_file(
        test_type,
        api_config,
    )

    if (
        destination.exists()
        and not force
        and not dry_run
    ):

        print(
            f"SKIP   [{test_type:<7}] "
            f"{destination}"
        )

        return "skipped"

    source = read_text(
        template_path
    )

    source = transform_template(
        source,
        api_config,
    )

    source = post_process(
        test_type,
        source,
        api_config,
    )

    if dry_run:

        print(
            f"DRY    [{test_type:<7}] "
            f"{destination}"
        )

        return "generated"

    write_text(
        destination,
        source,
    )

    print(
        f"CREATE [{test_type:<7}] "
        f"{destination}"
    )

    return "generated"


# ============================================================
# GENERATE API
# ============================================================

def generate_api(
    api_name: str,
    *,
    force: bool = False,
    dry_run: bool = False,
    selected_type: Optional[str] = None,
) -> None:

    normalized = normalize_api_name(
        api_name
    )

    if normalized not in APIS:

        print()
        print(
            f"ERROR: API '{api_name}' "
            "is not configured."
        )

        print()
        list_apis()

        raise KeyError(
            normalized
        )

    config = APIS[
        normalized
    ]

    validate_api_config(
        normalized,
        config,
    )

    if selected_type:

        if selected_type not in VALID_TEST_TYPES:

            raise ValueError(
                f"Invalid test type "
                f"'{selected_type}'. "
                f"Valid values: "
                f"{', '.join(TEST_TYPES)}"
            )

        selected_types = (
            selected_type,
        )

    else:

        selected_types = TEST_TYPES

    validate_templates(
        selected_types
    )

    print()
    print(
        "=" * 78
    )

    print(
        f"Generating tests for API: "
        f"{normalized}"
    )

    print(
        f"Key column: "
        f"{config['key_column']}"
    )

    print(
        f"Lookup function: "
        f"{config['lookup_function']}"
    )

    print(
        f"Search handler: "
        f"{config['search_handler']}"
    )

    print(
        f"Lookup handler: "
        f"{config['lookup_handler']}"
    )

    print(
        "=" * 78
    )

    generated = 0
    skipped = 0

    for test_type in selected_types:

        status = generate_one(
            test_type,
            config,
            force=force,
            dry_run=dry_run,
        )

        if status == "generated":
            generated += 1
        else:
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
# COMMAND LINE
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests using "
            "Project Financial tests as templates."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help=(
            "API name from APIS configuration. "
            "Example: po_funding_detail"
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_apis",
        help="List configured APIs.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing generated tests."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show files that would be generated "
            "without writing them."
        ),
    )

    parser.add_argument(
        "--type",
        dest="test_type",
        choices=TEST_TYPES,
        help=(
            "Generate only one test type."
        ),
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    parser = build_parser()

    args = parser.parse_args()

    if args.list_apis:

        list_apis()
        return

    if not args.api:

        parser.print_help()

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
            "List APIs:"
        )

        print(
            "  py generate_api_tests.py --list"
        )

        return

    try:

        generate_api(
            args.api,
            force=args.force,
            dry_run=args.dry_run,
            selected_type=args.test_type,
        )

    except Exception as exc:

        print()
        print(
            f"ERROR: {exc}"
        )

        sys.exit(1)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
