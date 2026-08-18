from pathlib import Path


# ============================================================
# PROJECT ROOTS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEST_ROOT = BASE_DIR / "main-function" / "tests" / "unit"


# ============================================================
# TEMPLATE FILES
# ============================================================

TEMPLATES = {
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

DESTINATIONS = {
    "db": TEST_ROOT / "db",

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
# API CONFIGURATION
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

        "source_view": "po_funding_detail_vw",

        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------

        "key_column": "project_id",

        "sample_key": "P-1001",

        # ----------------------------------------------------
        # Sample field for filter tests
        # ----------------------------------------------------

        "sample_field": "vendor_name",

        "sample_value": "Test Vendor",

        # ----------------------------------------------------
        # LIST FUNCTION
        #
        # Real repository:
        #
        # get_po_funding_detail(
        #     filters=None,
        #     sort=None,
        #     page=None,
        #     columns=None
        # )
        # ----------------------------------------------------

        "list_function": "get_po_funding_detail",

        "list_supports_filters": True,

        "list_supports_sort": True,

        "list_supports_page": True,

        "list_supports_columns": True,

        # ----------------------------------------------------
        # LOOKUP FUNCTION
        #
        # Real repository:
        #
        # get_po_funding_detail_by_project_id(
        #     project_id,
        #     page=None,
        #     sort=None,
        #     columns=None
        # )
        #
        # Notice:
        # NO filters argument.
        # ----------------------------------------------------

        "lookup_function":
            "get_po_funding_detail_by_project_id",

        "lookup_argument": "project_id",

        "lookup_supports_filters": False,

        "lookup_supports_sort": True,

        "lookup_supports_page": True,

        "lookup_supports_columns": True,

        # ----------------------------------------------------
        # execute_query behavior
        #
        # Your repository currently calls:
        #
        # execute_query(
        #     plan.sql,
        #     plan.params,
        #     limit=100
        # )
        # ----------------------------------------------------

        "lookup_query_limit": 100,

        "list_query_limit": 100,

        # ----------------------------------------------------
        # Generic template replacement overrides
        # ----------------------------------------------------

        "replacements": {

            # Repository function
            "get_project_financials":
                "get_po_funding_detail",

            "get_project_financial_by_id":
                "get_po_funding_detail_by_project_id",

            "get_project_financials_by_id":
                "get_po_funding_detail_by_project_id",

            "get_project_financial_details":
                "get_po_funding_detail_by_project_id",

            # Source view
            "project_financials_source_vw":
                "po_funding_detail_vw",

            # Project Financial naming
            "project_financials":
                "po_funding_detail",

            "project_financial":
                "po_funding_detail",

            "ProjectFinancial":
                "PoFundingDetail",

            "PROJECT_FINANCIAL":
                "PO_FUNDING_DETAIL",

            # Sample values
            "proj_name":
                "vendor_name",

            "Test Project":
                "Test Vendor",

            # Key naming
            "proj_id":
                "project_id",

            "P-1001":
                "P-1001",
        },
    },


    # ========================================================
    # GL DETAILS
    # Keep this available for later.
    # ========================================================

    "gl_details": {

        "module_name": "gl_details",

        "route_name": "gl-details",

        "plural_name": "gl_details",

        "source_view": "gl_details_vw",

        "key_column": "proj_id",

        "sample_key": "1001",

        "sample_field": "description",

        "sample_value": "Test GL Detail",

        "list_function": "get_gl_details",

        "lookup_function": None,

        "lookup_argument": None,

        "lookup_supports_filters": False,

        "lookup_query_limit": None,

        "list_query_limit": None,

        "replacements": {

            "project_financials_source_vw":
                "gl_details_vw",

            "project_financials":
                "gl_details",

            "project_financial":
                "gl_details",

            "ProjectFinancial":
                "GlDetails",

            "PROJECT_FINANCIAL":
                "GL_DETAILS",

            "proj_name":
                "description",

            "Test Project":
                "Test GL Detail",

            "P-1001":
                "1001",
        },
    },
}

+++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
import ast
import re
import sys
from pathlib import Path

from api_test_config import (
    APIS,
    TEMPLATES,
    DESTINATIONS,
)


# ============================================================
# CONSTANTS
# ============================================================

TEST_TYPES = (
    "db",
    "model",
    "service",
    "handler",
)


# ============================================================
# BASIC HELPERS
# ============================================================

def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8"
    )


def write_text(
    path: Path,
    content: str,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )


def snake_to_pascal(value: str) -> str:

    return "".join(
        part.capitalize()
        for part in value.split("_")
    )


def snake_to_kebab(value: str) -> str:

    return value.replace(
        "_",
        "-",
    )


# ============================================================
# DESTINATION FILE NAME
# ============================================================

def get_destination_file(
    api_name: str,
    test_type: str,
) -> Path:

    if test_type == "db":

        filename = (
            f"test_{api_name}_repo.py"
        )

    elif test_type == "model":

        filename = (
            f"test_{api_name}.py"
        )

    elif test_type == "service":

        filename = (
            f"test_{api_name}_service.py"
        )

    elif test_type == "handler":

        filename = (
            f"test_{api_name}.py"
        )

    else:

        raise ValueError(
            f"Unknown test type: {test_type}"
        )

    return (
        DESTINATIONS[test_type]
        / filename
    )


# ============================================================
# GENERIC REPLACEMENTS
# ============================================================

def build_generic_replacements(
    api_name: str,
    config: dict,
) -> dict:

    module_name = config.get(
        "module_name",
        api_name,
    )

    route_name = config.get(
        "route_name",
        snake_to_kebab(api_name),
    )

    pascal_name = snake_to_pascal(
        module_name
    )

    plural_name = config.get(
        "plural_name",
        module_name,
    )

    source_view = config.get(
        "source_view",
        f"{module_name}_vw",
    )

    key_column = config.get(
        "key_column",
        "id",
    )

    sample_key = str(
        config.get(
            "sample_key",
            "1001",
        )
    )

    sample_field = config.get(
        "sample_field",
        "name",
    )

    sample_value = str(
        config.get(
            "sample_value",
            "Test Value",
        )
    )

    return {

        # ----------------------------------------------------
        # Snake case
        # ----------------------------------------------------

        "project_financial":
            module_name,

        "project_financials":
            plural_name,

        # ----------------------------------------------------
        # Pascal case
        # ----------------------------------------------------

        "ProjectFinancial":
            pascal_name,

        "ProjectFinancials":
            f"{pascal_name}s",

        # ----------------------------------------------------
        # Upper case
        # ----------------------------------------------------

        "PROJECT_FINANCIAL":
            module_name.upper(),

        "PROJECT_FINANCIALS":
            plural_name.upper(),

        # ----------------------------------------------------
        # Route
        # ----------------------------------------------------

        "project-financial":
            route_name,

        "project-financials":
            route_name,

        # ----------------------------------------------------
        # View
        # ----------------------------------------------------

        "project_financials_source_vw":
            source_view,

        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------

        "proj_id":
            key_column,

        '"P-1001"':
            f'"{sample_key}"',

        "'P-1001'":
            f"'{sample_key}'",

        # ----------------------------------------------------
        # Sample field/value
        # ----------------------------------------------------

        "proj_name":
            sample_field,

        '"Test Project"':
            f'"{sample_value}"',

        "'Test Project'":
            f"'{sample_value}'",
    }


# ============================================================
# SAFE REPLACEMENT
# ============================================================

def apply_replacements(
    content: str,
    replacements: dict,
) -> str:

    # Longest keys first.
    #
    # Prevent:
    #
    # project_financial
    #
    # from modifying:
    #
    # project_financials
    #
    keys = sorted(
        replacements.keys(),
        key=len,
        reverse=True,
    )

    for old in keys:

        new = str(
            replacements[old]
        )

        content = content.replace(
            old,
            new,
        )

    return content


# ============================================================
# REMOVE TEST FUNCTIONS
# ============================================================

def remove_test_functions(
    content: str,
    predicate,
) -> str:

    try:

        tree = ast.parse(
            content
        )

    except SyntaxError:

        return content

    lines = content.splitlines(
        keepends=True
    )

    ranges = []

    for node in tree.body:

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            continue

        if not predicate(
            node.name
        ):

            continue

        start = node.lineno

        if node.decorator_list:

            start = min(
                decorator.lineno
                for decorator
                in node.decorator_list
            )

        end = node.end_lineno

        ranges.append(
            (
                start,
                end,
            )
        )

    for start, end in reversed(
        ranges
    ):

        del lines[
            start - 1:end
        ]

    return "".join(
        lines
    )


# ============================================================
# REMOVE INVALID LOOKUP FILTER TESTS
# ============================================================

def remove_lookup_filter_tests(
    content: str,
) -> str:

    filter_test_names = (
        "_with_filter_group",
        "_with_existing_envelope",
        "_filters_normalization",
        "_with_filters",
        "_exact_filters",
    )

    return remove_test_functions(
        content,
        lambda name:
            any(
                token in name
                for token
                in filter_test_names
            )
            and (
                "by_id" in name
                or
                "by_project_id" in name
                or
                "details" in name
            ),
    )


# ============================================================
# REMOVE LOOKUP TESTS COMPLETELY
# ============================================================

def remove_lookup_tests(
    content: str,
) -> str:

    return remove_test_functions(
        content,
        lambda name:
            (
                "by_id" in name
                or
                "by_project_id" in name
            ),
    )


# ============================================================
# FIX FUNCTION NAME
# ============================================================

def replace_lookup_function_name(
    content: str,
    config: dict,
) -> str:

    lookup_function = config.get(
        "lookup_function"
    )

    if not lookup_function:

        return content

    possible_template_names = [

        "get_project_financial_by_id",

        "get_project_financials_by_id",

        "get_project_financial_details",

        "get_po_funding_detail_by_id",

    ]

    for name in possible_template_names:

        content = content.replace(
            name,
            lookup_function,
        )

    return content


# ============================================================
# FIX LOOKUP ARGUMENT
# ============================================================

def replace_lookup_argument(
    content: str,
    config: dict,
) -> str:

    lookup_argument = config.get(
        "lookup_argument"
    )

    if not lookup_argument:

        return content

    possible_arguments = (
        "proj_id",
        "project_id",
        "id",
    )

    # We don't blindly replace every id=.
    #
    # Only replace likely generated lookup arguments.

    lookup_function = config.get(
        "lookup_function"
    )

    if not lookup_function:

        return content

    for old_arg in possible_arguments:

        pattern = (
            rf"({re.escape(lookup_function)}\s*\("
            rf"[\s\S]*?)\b"
            rf"{re.escape(old_arg)}="
        )

        replacement = (
            rf"\1{lookup_argument}="
        )

        content = re.sub(
            pattern,
            replacement,
            content,
            count=20,
        )

    return content


# ============================================================
# FIX execute_query ASSERTION LIMIT
# ============================================================

def add_limit_to_execute_query_assertions(
    content: str,
    limit: int,
) -> str:

    # --------------------------------------------------------
    # Case 1
    #
    # mock_execute_query.assert_called_once_with(
    #     plan.sql,
    #     plan.params,
    # )
    # --------------------------------------------------------

    pattern = re.compile(
        r"""
        mock_execute_query
        \.assert_called_once_with
        \(
        \s*
        plan\.sql
        \s*,
        \s*
        plan\.params
        \s*,
        \s*
        \)
        """,
        re.VERBOSE,
    )

    replacement = (
        "mock_execute_query.assert_called_once_with(\n"
        "        plan.sql,\n"
        "        plan.params,\n"
        f"        limit={limit},\n"
        "    )"
    )

    content = pattern.sub(
        replacement,
        content,
    )

    # --------------------------------------------------------
    # Avoid duplicate limit if generator reruns
    # --------------------------------------------------------

    content = content.replace(
        f"limit={limit},\n"
        f"        limit={limit},",
        f"limit={limit},",
    )

    return content


# ============================================================
# REMOVE FILTER ARGUMENT FROM LOOKUP CALL
# ============================================================

def remove_filters_from_lookup_calls(
    content: str,
    lookup_function: str,
) -> str:

    # Handles generated calls such as:
    #
    # get_x_by_project_id(
    #     project_id="P-1001",
    #     filters=filters,
    # )
    #
    # But generally we remove the entire invalid test.
    #
    # This is an extra safeguard.

    pattern = re.compile(
        rf"""
        (
        {re.escape(lookup_function)}
        \s*
        \(
        [\s\S]*?
        )
        \n
        \s*
        filters
        \s*
        =
        [^,\n]+
        ,
        """,
        re.VERBOSE,
    )

    return pattern.sub(
        r"\1",
        content,
    )


# ============================================================
# API BEHAVIOR
# ============================================================

def apply_api_behavior(
    content: str,
    config: dict,
    test_type: str,
) -> str:

    lookup_function = config.get(
        "lookup_function"
    )

    lookup_supports_filters = config.get(
        "lookup_supports_filters",
        True,
    )

    lookup_query_limit = config.get(
        "lookup_query_limit"
    )

    # ========================================================
    # DB TESTS
    # ========================================================

    if test_type == "db":

        # ----------------------------------------------------
        # No dedicated lookup function
        # ----------------------------------------------------

        if not lookup_function:

            content = remove_lookup_tests(
                content
            )

            return content

        # ----------------------------------------------------
        # Correct lookup function
        # ----------------------------------------------------

        content = replace_lookup_function_name(
            content,
            config,
        )

        # ----------------------------------------------------
        # Correct lookup argument
        # ----------------------------------------------------

        content = replace_lookup_argument(
            content,
            config,
        )

        # ----------------------------------------------------
        # Lookup does not support filters
        # ----------------------------------------------------

        if not lookup_supports_filters:

            content = remove_lookup_filter_tests(
                content
            )

            content = remove_filters_from_lookup_calls(
                content,
                lookup_function,
            )

        # ----------------------------------------------------
        # execute_query limit
        # ----------------------------------------------------

        if lookup_query_limit is not None:

            content = add_limit_to_execute_query_assertions(
                content,
                lookup_query_limit,
            )

    return content


# ============================================================
# NORMALIZE EXTRA BLANK LINES
# ============================================================

def cleanup_content(
    content: str,
) -> str:

    content = re.sub(
        r"\n{5,}",
        "\n\n\n",
        content,
    )

    return (
        content.rstrip()
        + "\n"
    )


# ============================================================
# TRANSFORM TEMPLATE
# ============================================================

def transform_template(
    template_content: str,
    api_name: str,
    config: dict,
    test_type: str,
) -> str:

    # --------------------------------------------------------
    # Generic replacements
    # --------------------------------------------------------

    replacements = build_generic_replacements(
        api_name,
        config,
    )

    content = apply_replacements(
        template_content,
        replacements,
    )

    # --------------------------------------------------------
    # API-specific replacements
    # --------------------------------------------------------

    extra_replacements = config.get(
        "replacements",
        {},
    )

    content = apply_replacements(
        content,
        extra_replacements,
    )

    # --------------------------------------------------------
    # API behavior rules
    # --------------------------------------------------------

    content = apply_api_behavior(
        content,
        config,
        test_type,
    )

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    content = cleanup_content(
        content
    )

    return content


# ============================================================
# VALIDATE TEMPLATE FILES
# ============================================================

def validate_templates() -> bool:

    missing = []

    for test_type in TEST_TYPES:

        path = TEMPLATES[
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

        return True

    print(
        "\nERROR: Missing template files:\n"
    )

    for test_type, path in missing:

        print(
            f"{test_type:8}: {path}"
        )

    print(
        "\nThe generator requires the existing "
        "project_financial tests.\n"
    )

    return False


# ============================================================
# LIST APIs
# ============================================================

def list_apis() -> None:

    print()

    print(
        "=" * 70
    )

    print(
        "Configured APIs"
    )

    print(
        "=" * 70
    )

    for api_name, config in APIS.items():

        key = config.get(
            "key_column",
            "-"
        )

        lookup = config.get(
            "lookup_function",
            "-"
        )

        print(
            f"{api_name:25} "
            f"key={key:15} "
            f"lookup={lookup}"
        )

    print()


# ============================================================
# GENERATE ONE FILE
# ============================================================

def generate_file(
    api_name: str,
    config: dict,
    test_type: str,
    force: bool,
    dry_run: bool,
) -> str:

    template_path = TEMPLATES[
        test_type
    ]

    destination = get_destination_file(
        api_name,
        test_type,
    )

    # --------------------------------------------------------
    # Existing destination
    # --------------------------------------------------------

    if (
        destination.exists()
        and not force
    ):

        print(
            f"SKIP   "
            f"[{test_type:7}] "
            f"{destination}"
        )

        return "skipped"

    # --------------------------------------------------------
    # Read template
    # --------------------------------------------------------

    template_content = read_text(
        template_path
    )

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    generated_content = transform_template(
        template_content,
        api_name,
        config,
        test_type,
    )

    # --------------------------------------------------------
    # Dry run
    # --------------------------------------------------------

    if dry_run:

        print(
            f"DRY    "
            f"[{test_type:7}] "
            f"{destination}"
        )

        return "generated"

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    write_text(
        destination,
        generated_content,
    )

    print(
        f"CREATE "
        f"[{test_type:7}] "
        f"{destination}"
    )

    return "generated"


# ============================================================
# GENERATE API
# ============================================================

def generate_api(
    api_name: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:

    if api_name not in APIS:

        print(
            f"\nERROR: Unknown API: "
            f"{api_name}\n"
        )

        list_apis()

        raise SystemExit(
            1
        )

    if not validate_templates():

        raise SystemExit(
            1
        )

    config = APIS[
        api_name
    ]

    print()

    print(
        "=" * 70
    )

    print(
        f"Generating tests for API: "
        f"{api_name}"
    )

    print(
        f"Key column: "
        f"{config.get('key_column')}"
    )

    print(
        f"Lookup function: "
        f"{config.get('lookup_function')}"
    )

    print(
        "=" * 70
    )

    generated = 0
    skipped = 0

    for test_type in TEST_TYPES:

        result = generate_file(
            api_name=api_name,
            config=config,
            test_type=test_type,
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
# CLI
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Generate DB, model, "
            "service and handler tests "
            "from Project Financial templates."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help=(
            "API name from "
            "api_test_config.py"
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured APIs",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing "
            "generated tests"
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show files that would "
            "be generated without writing"
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    args = parse_args()

    if args.list:

        list_apis()

        return

    if not args.api:

        print(
            "\nERROR: API name required.\n"
        )

        print(
            "Examples:\n"
        )

        print(
            "  py generate_api_tests.py --list"
        )

        print(
            "  py generate_api_tests.py "
            "po_funding_detail --dry-run"
        )

        print(
            "  py generate_api_tests.py "
            "po_funding_detail --force"
        )

        return

    generate_api(
        api_name=args.api,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":

    main()
