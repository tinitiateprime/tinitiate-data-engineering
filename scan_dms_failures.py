# api_test_config.py

"""
Configuration used by generate_api_tests.py.

Normally this is the ONLY file you need to update when adding
another API.

Required:
    api_name
    key_column

Recommended:
    sample_key
    sample_field
    sample_value

Optional overrides are available when an API naming convention
is different from the standard generated API pattern.
"""


APIS = {

    # ==========================================================
    # FIRST API - TEST THIS ONE FIRST
    # ==========================================================
    "gl_details": {

        # Primary/key column used to retrieve one record
        # IMPORTANT: change this to the actual GL Details key.
        "key_column": "id",

        # Fake value used only by unit tests
        "sample_key": "1001",

        # Normal field used for filters / assertions
        # Change to a real GL Details column if needed.
        "sample_field": "description",

        "sample_value": "Test GL Detail",

        # ------------------------------------------------------
        # OPTIONAL SETTINGS
        # ------------------------------------------------------
        #
        # These values normally do not need to be changed.
        #
        # They are here so that if one API has unusual naming,
        # you fix only THIS config file, not the generator.
        #

        # Python module name
        "module_name": "gl_details",

        # URL style name
        "route_name": "gl-details",

        # Name used where the project_financial template
        # originally uses the plural project_financials.
        "plural_name": "gl_details",

        # Source view used in mocked SQL.
        # This does NOT query the database.
        # It is only a unit-test mock string.
        "source_view": "gl_details_source_vw",

        # Optional explicit replacement map.
        #
        # Leave empty initially.
        # If generated function names differ from the real API,
        # we can override them here WITHOUT modifying generator.
        "replacements": {
            # Example:
            #
            # "get_gl_details_details": "get_gl_details",
            # "search_gl_details": "search_gl_details",
        },
    },

}


----------------------------------------------------------


# generate_api_tests.py

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from api_test_config import APIS


# ==============================================================
# PROJECT LOCATIONS
# ==============================================================

ROOT = Path(__file__).resolve().parent

MAIN_FUNCTION = ROOT / "main-function"

TEST_ROOT = MAIN_FUNCTION / "tests" / "unit"


# ==============================================================
# MASTER TEST TEMPLATES
#
# We are using the existing project_financial tests because
# those tests already follow the repository's approved pattern.
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

DESTINATIONS = {

    "db":
        TEST_ROOT / "db",

    "model":
        TEST_ROOT / "domain" / "models",

    "service":
        TEST_ROOT / "domain" / "services",

    "handler":
        TEST_ROOT / "v1",
}


# ==============================================================
# UTILITY FUNCTIONS
# ==============================================================

def snake_to_pascal(value: str) -> str:
    """
    gl_details -> GlDetails
    project_status_detail -> ProjectStatusDetail
    """
    return "".join(
        word.capitalize()
        for word in value.split("_")
    )


def snake_to_title(value: str) -> str:
    """
    gl_details -> Gl Details
    """
    return " ".join(
        word.capitalize()
        for word in value.split("_")
    )


def snake_to_kebab(value: str) -> str:
    """
    gl_details -> gl-details
    """
    return value.replace("_", "-")


def validate_templates() -> None:
    """
    Make sure all four working project_financial test files exist.
    """

    missing = []

    for layer, template in TEMPLATES.items():
        if not template.exists():
            missing.append(
                f"{layer}: {template}"
            )

    if missing:

        print("\nERROR: Missing template files:\n")

        for item in missing:
            print(f"  {item}")

        print(
            "\nThe generator requires the existing "
            "project_financial tests."
        )

        sys.exit(1)


def get_output_file(
    layer: str,
    api_name: str,
) -> Path:
    """
    Determine generated test filename.
    """

    if layer == "db":

        filename = (
            f"test_{api_name}_repo.py"
        )

    elif layer == "service":

        filename = (
            f"test_{api_name}_service.py"
        )

    else:

        filename = (
            f"test_{api_name}.py"
        )

    return DESTINATIONS[layer] / filename


# ==============================================================
# CONFIG NORMALIZATION
# ==============================================================

def normalize_config(
    api_name: str,
    config: dict,
) -> dict:

    result = dict(config)

    result.setdefault(
        "module_name",
        api_name,
    )

    result.setdefault(
        "plural_name",
        api_name,
    )

    result.setdefault(
        "route_name",
        snake_to_kebab(api_name),
    )

    result.setdefault(
        "source_view",
        f"{api_name}_source_vw",
    )

    result.setdefault(
        "sample_key",
        "1001",
    )

    result.setdefault(
        "sample_field",
        "name",
    )

    result.setdefault(
        "sample_value",
        "Test Record",
    )

    result.setdefault(
        "replacements",
        {},
    )

    if not result.get("key_column"):

        raise ValueError(
            f"{api_name}: key_column is required"
        )

    return result


# ==============================================================
# TEMPLATE TRANSFORMATION
# ==============================================================

def transform_template(
    original: str,
    api_name: str,
    config: dict,
) -> str:

    config = normalize_config(
        api_name,
        config,
    )

    module_name = config["module_name"]

    plural_name = config["plural_name"]

    route_name = config["route_name"]

    source_view = config["source_view"]

    key_column = config["key_column"]

    sample_key = str(
        config["sample_key"]
    )

    sample_field = config[
        "sample_field"
    ]

    sample_value = str(
        config["sample_value"]
    )

    pascal_name = snake_to_pascal(
        module_name
    )

    title_name = snake_to_title(
        module_name
    )

    upper_name = module_name.upper()

    content = original


    # ==========================================================
    # VERY IMPORTANT:
    #
    # Replace the most specific strings FIRST.
    # Otherwise project_financial inside
    # project_financials would be replaced prematurely.
    # ==========================================================


    replacements = [

        # ------------------------------------------------------
        # Source View
        # ------------------------------------------------------

        (
            "project_financials_source_vw",
            source_view,
        ),

        (
            "project_financial_source_vw",
            source_view,
        ),


        # ------------------------------------------------------
        # Constants / Data
        # ------------------------------------------------------

        (
            "PROJECT_FINANCIAL_DATA",
            f"{upper_name}_DATA",
        ),

        (
            "PROJECT_FINANCIALS",
            upper_name,
        ),

        (
            "PROJECT_FINANCIAL",
            upper_name,
        ),


        # ------------------------------------------------------
        # Pascal Case
        # ------------------------------------------------------

        (
            "ProjectFinancials",
            pascal_name,
        ),

        (
            "ProjectFinancial",
            pascal_name,
        ),


        # ------------------------------------------------------
        # Route Names
        # ------------------------------------------------------

        (
            "project-financials",
            route_name,
        ),

        (
            "project-financial",
            route_name,
        ),


        # ------------------------------------------------------
        # Python plural name first
        # ------------------------------------------------------

        (
            "project_financials",
            plural_name,
        ),


        # ------------------------------------------------------
        # Python singular/module name
        # ------------------------------------------------------

        (
            "project_financial",
            module_name,
        ),


        # ------------------------------------------------------
        # Friendly labels
        # ------------------------------------------------------

        (
            "Project Financials",
            title_name,
        ),

        (
            "Project Financial",
            title_name,
        ),

        (
            "project financials",
            title_name.lower(),
        ),

        (
            "project financial",
            title_name.lower(),
        ),


        # ------------------------------------------------------
        # Project Financial key field
        # ------------------------------------------------------

        (
            '"proj_id"',
            f'"{key_column}"',
        ),

        (
            "'proj_id'",
            f"'{key_column}'",
        ),


        # ------------------------------------------------------
        # Sample normal field
        # ------------------------------------------------------

        (
            '"proj_name"',
            f'"{sample_field}"',
        ),

        (
            "'proj_name'",
            f"'{sample_field}'",
        ),


        # ------------------------------------------------------
        # Sample key values
        # ------------------------------------------------------

        (
            '"P-1001"',
            f'"{sample_key}"',
        ),

        (
            "'P-1001'",
            f"'{sample_key}'",
        ),

        (
            '"P-1002"',
            f'"{sample_key}-2"',
        ),

        (
            "'P-1002'",
            f"'{sample_key}-2'",
        ),

        (
            '"P-1003"',
            f'"{sample_key}-3"',
        ),

        (
            "'P-1003'",
            f"'{sample_key}-3'",
        ),


        # ------------------------------------------------------
        # Sample display values
        # ------------------------------------------------------

        (
            '"Test Project"',
            f'"{sample_value}"',
        ),

        (
            "'Test Project'",
            f"'{sample_value}'",
        ),
    ]


    for old, new in replacements:

        content = content.replace(
            old,
            new,
        )


    # ==========================================================
    # API SPECIFIC OVERRIDES
    #
    # This is how we avoid modifying this generator later.
    #
    # Put special replacements into api_test_config.py.
    # ==============================================================

    custom_replacements = config.get(
        "replacements",
        {},
    )

    for old, new in custom_replacements.items():

        content = content.replace(
            old,
            new,
        )

    return content


# ==============================================================
# GENERATE SINGLE API
# ==============================================================

def generate_api(
    api_name: str,
    force: bool = False,
    dry_run: bool = False,
) -> bool:

    if api_name not in APIS:

        print(
            f"\nERROR: '{api_name}' "
            "does not exist in api_test_config.py"
        )

        return False


    config = normalize_config(
        api_name,
        APIS[api_name],
    )


    print()
    print("=" * 72)

    print(
        f"Generating tests for API: "
        f"{api_name}"
    )

    print(
        f"Key column: "
        f"{config['key_column']}"
    )

    print("=" * 72)


    generated = 0
    skipped = 0


    for layer, template in TEMPLATES.items():

        output_file = get_output_file(
            layer,
            api_name,
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        # ------------------------------------------------------
        # Do not overwrite tests by default
        # ------------------------------------------------------

        if output_file.exists() and not force:

            print(
                f"SKIP  [{layer:7}] "
                f"{output_file.relative_to(ROOT)}"
            )

            skipped += 1

            continue


        template_content = (
            template.read_text(
                encoding="utf-8"
            )
        )


        generated_content = (
            transform_template(
                template_content,
                api_name,
                config,
            )
        )


        if dry_run:

            print(
                f"DRY   [{layer:7}] "
                f"{output_file.relative_to(ROOT)}"
            )

        else:

            output_file.write_text(
                generated_content,
                encoding="utf-8",
            )

            print(
                f"CREATE [{layer:7}] "
                f"{output_file.relative_to(ROOT)}"
            )


        generated += 1


    print()

    print(
        f"Generated: {generated}"
    )

    print(
        f"Skipped:   {skipped}"
    )

    return True


# ==============================================================
# LIST CONFIGURED APIS
# ==============================================================

def list_apis() -> None:

    print()
    print("Configured APIs")
    print("=" * 72)

    for name, raw_config in APIS.items():

        config = normalize_config(
            name,
            raw_config,
        )

        print(
            f"{name:30} "
            f"key={config['key_column']}"
        )


# ==============================================================
# GENERATE ALL
# ==============================================================

def generate_all(
    force: bool = False,
    dry_run: bool = False,
) -> None:

    for api_name in APIS:

        generate_api(
            api_name,
            force=force,
            dry_run=dry_run,
        )


# ==============================================================
# OPTIONAL CLEANUP
# ==============================================================

def clean_generated_api(
    api_name: str,
) -> None:
    """
    Delete the four generated test files for an API.

    Does NOT delete project_financial templates.
    """

    if api_name == "project_financial":

        print(
            "Refusing to delete "
            "project_financial template tests."
        )

        return


    print(
        f"\nCleaning generated tests "
        f"for {api_name}"
    )


    for layer in TEMPLATES:

        output_file = get_output_file(
            layer,
            api_name,
        )

        if output_file.exists():

            output_file.unlink()

            print(
                f"DELETE "
                f"{output_file.relative_to(ROOT)}"
            )


# ==============================================================
# COMMAND LINE
# ==============================================================

def main() -> None:

    parser = argparse.ArgumentParser(

        description=(
            "Generate DB, Model, Service and Handler "
            "unit tests from the working "
            "project_financial templates."
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

        "--all",

        action="store_true",

        help=(
            "Generate tests for all APIs "
            "defined in config."
        ),
    )


    parser.add_argument(

        "--list",

        action="store_true",

        help="List configured APIs.",
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
            "Show what will be generated "
            "without creating files."
        ),
    )


    parser.add_argument(

        "--clean",

        action="store_true",

        help=(
            "Delete generated files "
            "for the supplied API."
        ),
    )


    args = parser.parse_args()


    validate_templates()


    # ----------------------------------------------------------
    # LIST
    # ----------------------------------------------------------

    if args.list:

        list_apis()

        return


    # ----------------------------------------------------------
    # ALL
    # ----------------------------------------------------------

    if args.all:

        generate_all(
            force=args.force,
            dry_run=args.dry_run,
        )

        return


    # ----------------------------------------------------------
    # API REQUIRED BELOW THIS POINT
    # ----------------------------------------------------------

    if not args.api:

        parser.print_help()

        return


    # ----------------------------------------------------------
    # CLEAN
    # ----------------------------------------------------------

    if args.clean:

        clean_generated_api(
            args.api
        )

        return


    # ----------------------------------------------------------
    # GENERATE ONE API
    # ----------------------------------------------------------

    generate_api(

        args.api,

        force=args.force,

        dry_run=args.dry_run,
    )


if __name__ == "__main__":

    main()
