# api_test_config.py

"""
Configuration for generate_api_tests.py

Normal usage:

    py generate_api_tests.py --list

    py generate_api_tests.py po_funding_detail --dry-run

    py generate_api_tests.py po_funding_detail

    py generate_api_tests.py po_funding_detail --force
"""


APIS = {

    # ==========================================================
    # PO FUNDING DETAIL
    # ==========================================================
    "po_funding_detail": {

        # ------------------------------------------------------
        # LOOKUP / KEY INFORMATION
        # ------------------------------------------------------

        # Column exposed by the MV/API that the dedicated
        # repository lookup is based on.
        "key_column": "project_id",

        # Fake value used only in unit tests.
        "sample_key": "P-1001",

        # Actual repository function used for specific project
        # retrieval.
        "lookup_function":
            "get_po_funding_detail_by_project_id",

        # Actual Python argument accepted by lookup_function.
        "lookup_argument": "project_id",

        # ------------------------------------------------------
        # NORMAL FILTER TEST
        # ------------------------------------------------------

        "sample_field": "vendor_name",
        "sample_value": "Test Vendor",

        # ------------------------------------------------------
        # NAMING
        # ------------------------------------------------------

        "module_name": "po_funding_detail",

        "route_name": "po-funding-detail",

        "plural_name": "po_funding_detail",

        # ------------------------------------------------------
        # DATABASE VIEW
        # ------------------------------------------------------

        "source_view": "po_funding_detail_vw",

        # ------------------------------------------------------
        # OPTIONAL EXTRA REPLACEMENTS
        #
        # These are applied after standard replacements.
        # Usually you should only change this config file when
        # another API has special naming.
        # ------------------------------------------------------

        "replacements": {

            # In case the Project Financial template contains
            # this exact generated function reference.
            "get_po_funding_detail_by_id":
                "get_po_funding_detail_by_project_id",
        },
    },


    # ==========================================================
    # GL DETAILS
    #
    # Keep this available for later.
    # ==========================================================
    #
    # "gl_details": {
    #
    #     "key_column": "proj_id",
    #     "sample_key": "1001",
    #
    #     "lookup_function": "get_gl_details",
    #     "lookup_argument": None,
    #
    #     "sample_field": "description",
    #     "sample_value": "Test GL Detail",
    #
    #     "module_name": "gl_details",
    #     "route_name": "gl-details",
    #     "plural_name": "gl_details",
    #
    #     "source_view": "gl_details_vw",
    #
    #     "replacements": {},
    # },
}



=====================================================================

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from api_test_config import APIS


# ==============================================================
# PATHS
# ==============================================================

ROOT = Path(__file__).resolve().parent

TEST_ROOT = (
    ROOT
    / "main-function"
    / "tests"
    / "unit"
)


# ==============================================================
# MASTER PROJECT FINANCIAL TEST FILES
#
# These are your known-good tests and act as templates.
# ==============================================================

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


# ==============================================================
# DESTINATION DIRECTORIES
# ==============================================================

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


# ==============================================================
# HELPER
# ==============================================================

def get_destination_file(
    test_type: str,
    module_name: str,
) -> Path:

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


# ==============================================================
# VALIDATE TEMPLATE FILES
# ==============================================================

def validate_templates() -> bool:

    missing = []

    for name, path in TEMPLATES.items():

        if not path.exists():

            missing.append(
                (name, path)
            )

    if not missing:

        return True

    print()
    print(
        "ERROR: Missing template files:"
    )
    print()

    for name, path in missing:

        print(
            f"{name}: {path}"
        )

    print()
    print(
        "The generator requires the existing "
        "project_financial tests."
    )

    return False


# ==============================================================
# STANDARD TEXT REPLACEMENTS
# ==============================================================

def build_standard_replacements(
    api_name: str,
    config: Dict[str, Any],
) -> Dict[str, str]:

    module_name = config.get(
        "module_name",
        api_name,
    )

    route_name = config.get(
        "route_name",
        module_name.replace("_", "-"),
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
        "proj_id",
    )

    sample_key = str(
        config.get(
            "sample_key",
            "1001",
        )
    )

    sample_field = config.get(
        "sample_field",
        "description",
    )

    sample_value = str(
        config.get(
            "sample_value",
            "Test Value",
        )
    )

    lookup_function = config.get(
        "lookup_function"
    )

    lookup_argument = config.get(
        "lookup_argument"
    )

    # ----------------------------------------------------------
    # Start with naming replacements.
    #
    # Longer strings first is important.
    # ----------------------------------------------------------

    replacements = {

        # Python function/module variants
        "project_financials":
            plural_name,

        "project_financial":
            module_name,

        # Route variants
        "project-financials":
            route_name,

        "project-financial":
            route_name,

        # Human-readable text
        "Project Financials":
            plural_name.replace(
                "_",
                " ",
            ).title(),

        "Project Financial":
            module_name.replace(
                "_",
                " ",
            ).title(),

        "PROJECT_FINANCIAL":
            module_name.upper(),

        # Known mocked MV/view pattern
        "project_financials_source_vw":
            source_view,

        "project_financial_source_vw":
            source_view,

        # Sample field
        '"proj_name"':
            f'"{sample_field}"',

        "'proj_name'":
            f"'{sample_field}'",

        # Sample value
        '"Test Project"':
            f'"{sample_value}"',

        "'Test Project'":
            f"'{sample_value}'",

        # Sample ID values commonly used by template
        '"P-1001"':
            f'"{sample_key}"',

        "'P-1001'":
            f"'{sample_key}'",

        '"p-1001"':
            f'"{sample_key}"',

        "'p-1001'":
            f"'{sample_key}'",
    }


    # ----------------------------------------------------------
    # Key field replacement
    # ----------------------------------------------------------

    if key_column != "proj_id":

        replacements.update(
            {
                '"proj_id"':
                    f'"{key_column}"',

                "'proj_id'":
                    f"'{key_column}'",
            }
        )


    # ----------------------------------------------------------
    # Dedicated lookup function
    #
    # Project Financial template commonly contains:
    #
    # get_project_financial_by_id(...)
    #
    # After normal naming replacement it becomes:
    #
    # get_<module>_by_id(...)
    #
    # We replace that with the real repository function.
    # ----------------------------------------------------------

    if lookup_function:

        generated_lookup_name = (
            f"get_{module_name}_by_id"
        )

        replacements[
            generated_lookup_name
        ] = lookup_function


    # ----------------------------------------------------------
    # Dedicated lookup argument
    #
    # Project Financial uses:
    #
    # proj_id="..."
    #
    # PO Funding Detail actually accepts:
    #
    # project_id="..."
    # ----------------------------------------------------------

    if lookup_argument:

        replacements[
            "proj_id="
        ] = (
            f"{lookup_argument}="
        )


    return replacements


# ==============================================================
# APPLY REPLACEMENTS
# ==============================================================

def apply_replacements(
    content: str,
    replacements: Dict[str, str],
) -> str:

    # Longest keys first prevents a shorter replacement
    # from interfering with a more specific replacement.

    ordered = sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for old, new in ordered:

        content = content.replace(
            old,
            new,
        )

    return content


# ==============================================================
# GENERATE CONTENT
# ==============================================================

def transform_template(
    template_content: str,
    api_name: str,
    config: Dict[str, Any],
) -> str:

    # ----------------------------------------------------------
    # Standard replacements
    # ----------------------------------------------------------

    replacements = (
        build_standard_replacements(
            api_name,
            config,
        )
    )

    transformed = apply_replacements(
        template_content,
        replacements,
    )


    # ----------------------------------------------------------
    # API-specific overrides
    # ----------------------------------------------------------

    extra_replacements = config.get(
        "replacements",
        {},
    )

    transformed = apply_replacements(
        transformed,
        extra_replacements,
    )

    return transformed


# ==============================================================
# GENERATE ONE TEST FILE
# ==============================================================

def generate_test_file(
    test_type: str,
    api_name: str,
    config: Dict[str, Any],
    force: bool = False,
    dry_run: bool = False,
) -> str:

    module_name = config.get(
        "module_name",
        api_name,
    )

    source_file = TEMPLATES[
        test_type
    ]

    destination_file = (
        get_destination_file(
            test_type,
            module_name,
        )
    )


    # ----------------------------------------------------------
    # Existing file handling
    # ----------------------------------------------------------

    if (
        destination_file.exists()
        and not force
    ):

        print(
            f"SKIP   "
            f"[{test_type:<7}] "
            f"{destination_file.relative_to(ROOT)}"
        )

        return "skipped"


    # ----------------------------------------------------------
    # Dry run
    # ----------------------------------------------------------

    if dry_run:

        print(
            f"DRY    "
            f"[{test_type:<7}] "
            f"{destination_file.relative_to(ROOT)}"
        )

        return "generated"


    # ----------------------------------------------------------
    # Read master template
    # ----------------------------------------------------------

    template_content = (
        source_file.read_text(
            encoding="utf-8",
        )
    )


    # ----------------------------------------------------------
    # Transform
    # ----------------------------------------------------------

    generated_content = (
        transform_template(
            template_content,
            api_name,
            config,
        )
    )


    # ----------------------------------------------------------
    # Write destination
    # ----------------------------------------------------------

    destination_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination_file.write_text(
        generated_content,
        encoding="utf-8",
    )


    action = (
        "OVERWRITE"
        if force
        else "CREATE"
    )

    print(
        f"{action:<9}"
        f"[{test_type:<7}] "
        f"{destination_file.relative_to(ROOT)}"
    )

    return "generated"


# ==============================================================
# GENERATE API
# ==============================================================

def generate_api(
    api_name: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:

    if api_name not in APIS:

        print()
        print(
            f"ERROR: Unknown API: "
            f"{api_name}"
        )

        print()
        print(
            "Configured APIs:"
        )

        for name in APIS:

            print(
                f"  {name}"
            )

        sys.exit(1)


    if not validate_templates():

        sys.exit(1)


    config = APIS[
        api_name
    ]

    print()
    print(
        "=" * 72
    )

    print(
        f"Generating tests for API: "
        f"{api_name}"
    )

    print(
        f"Key column: "
        f"{config.get('key_column')}"
    )

    if config.get(
        "lookup_function"
    ):

        print(
            f"Lookup function: "
            f"{config.get('lookup_function')}"
        )

    if config.get(
        "lookup_argument"
    ):

        print(
            f"Lookup argument: "
            f"{config.get('lookup_argument')}"
        )

    print(
        "=" * 72
    )


    generated = 0
    skipped = 0


    for test_type in (
        "db",
        "model",
        "service",
        "handler",
    ):

        result = generate_test_file(
            test_type=test_type,
            api_name=api_name,
            config=config,
            force=force,
            dry_run=dry_run,
        )

        if result == "generated":

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


# ==============================================================
# LIST CONFIGURED APIS
# ==============================================================

def list_apis() -> None:

    print()
    print(
        "Configured APIs"
    )

    print(
        "=" * 72
    )

    if not APIS:

        print(
            "No APIs configured."
        )

        return


    for name, config in APIS.items():

        key_column = (
            config.get(
                "key_column",
                "",
            )
        )

        lookup_function = (
            config.get(
                "lookup_function",
                "",
            )
        )

        print(
            f"{name:<30} "
            f"key={key_column:<20} "
            f"lookup={lookup_function}"
        )


# ==============================================================
# ARGUMENT PARSER
# ==============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests from "
            "Project Financial templates."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help=(
            "API name defined in "
            "api_test_config.py"
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "List configured APIs."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing generated "
            "test files."
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

    return parser


# ==============================================================
# MAIN
# ==============================================================

def main() -> None:

    parser = build_parser()

    args = parser.parse_args()


    if args.list:

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
            "po_funding_detail --dry-run"
        )

        return


    generate_api(
        args.api,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":

    main()
