"""
generate_api_tests.py

Generic unit-test generator for the MT-DM API project.

The generator uses the existing project_financial tests as templates and
creates tests for APIs defined in api_test_config.py.

Examples
--------
List configured APIs:

    py generate_api_tests.py --list

Dry run:

    py generate_api_tests.py po_funding_detail --dry-run

Generate:

    py generate_api_tests.py po_funding_detail

Overwrite existing generated tests:

    py generate_api_tests.py po_funding_detail --force

Generate only one test type:

    py generate_api_tests.py po_funding_detail --test-type service --force

Valid test types:
    db
    model
    service
    handler
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# CONFIG IMPORTS
# ============================================================

try:
    from api_test_config import (
        APIS,
        TEMPLATE_FILES,
        DESTINATION_DIRS,
        TEST_TYPES,
    )
except ImportError as exc:
    print()
    print("ERROR: Unable to import api_test_config.py")
    print()
    print(exc)
    print()
    print(
        "Expected api_test_config.py to contain:"
    )
    print(
        "  APIS"
    )
    print(
        "  TEMPLATE_FILES"
    )
    print(
        "  DESTINATION_DIRS"
    )
    print(
        "  TEST_TYPES"
    )
    print()
    sys.exit(1)


# ============================================================
# GENERAL HELPERS
# ============================================================

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
    po_funding_detail -> PO Funding Detail-like title.

    We do not force acronym capitalization here because
    API-specific display names may be supplied in config.
    """
    return " ".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def normalize_path(value: Any) -> Path:
    """
    Convert config path value into pathlib.Path.
    """
    if isinstance(value, Path):
        return value

    return Path(str(value))


def get_config_value(
    api_config: Dict[str, Any],
    name: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve one API config value.
    """
    value = api_config.get(name)

    if value is None:
        return default

    return value


def clean_blank_lines(source: str) -> str:
    """
    Avoid huge blocks of empty lines after substitutions.
    """
    source = re.sub(
        r"\n[ \t]+\n",
        "\n\n",
        source,
    )

    source = re.sub(
        r"\n{4,}",
        "\n\n\n",
        source,
    )

    return source


# ============================================================
# API CONFIG
# ============================================================

def prepare_api_config(
    api_name: str,
    raw_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a normalized API configuration.

    Everything that changes from one API to another should
    come from api_test_config.py.
    """

    config = dict(raw_config)

    module_name = get_config_value(
        config,
        "module_name",
        api_name,
    )

    plural_name = get_config_value(
        config,
        "plural_name",
        module_name,
    )

    route_name = get_config_value(
        config,
        "route_name",
        module_name.replace("_", "-"),
    )

    pascal_name = get_config_value(
        config,
        "pascal_name",
        snake_to_pascal(module_name),
    )

    display_name = get_config_value(
        config,
        "display_name",
        snake_to_title(module_name),
    )

    key_column = get_config_value(
        config,
        "key_column",
        "project_id",
    )

    key_param = get_config_value(
        config,
        "key_param",
        key_column,
    )

    key_value = str(
        get_config_value(
            config,
            "sample_key",
            "P-1001",
        )
    )

    source_view = get_config_value(
        config,
        "source_view",
        module_name,
    )

    lookup_function = get_config_value(
        config,
        "lookup_function",
        f"get_{module_name}_by_{key_param}",
    )

    search_function = get_config_value(
        config,
        "search_function",
        f"search_{plural_name}",
    )

    details_function = get_config_value(
        config,
        "details_function",
        lookup_function,
    )

    handler_search_function = get_config_value(
        config,
        "handler_search_function",
        f"search_{plural_name}_v1",
    )

    handler_details_function = get_config_value(
        config,
        "handler_details_function",
        f"get_{module_name}_details",
    )

    config.update(
        {
            "api_name": api_name,
            "module_name": module_name,
            "plural_name": plural_name,
            "route_name": route_name,
            "pascal_name": pascal_name,
            "display_name": display_name,
            "key_column": key_column,
            "key_param": key_param,
            "sample_key": key_value,
            "source_view": source_view,
            "lookup_function": lookup_function,
            "search_function": search_function,
            "details_function": details_function,
            "handler_search_function": (
                handler_search_function
            ),
            "handler_details_function": (
                handler_details_function
            ),
        }
    )

    return config


# ============================================================
# TEMPLATE REPLACEMENTS
# ============================================================

def build_standard_replacements(
    api_config: Dict[str, Any],
) -> Dict[str, str]:
    """
    Standard Project Financial -> target API replacements.

    Important:
    longest strings are replaced first later.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]
    pascal_name = api_config["pascal_name"]
    route_name = api_config["route_name"]
    source_view = api_config["source_view"]

    replacements: Dict[str, str] = {
        # ----------------------------------------------------
        # PascalCase
        # ----------------------------------------------------
        "ProjectFinancials": (
            pascal_name + "s"
        ),
        "ProjectFinancial": (
            pascal_name
        ),

        # ----------------------------------------------------
        # snake_case plural
        # ----------------------------------------------------
        "project_financials": (
            plural_name
        ),

        # ----------------------------------------------------
        # snake_case singular
        # ----------------------------------------------------
        "project_financial": (
            module_name
        ),

        # ----------------------------------------------------
        # kebab-case route
        # ----------------------------------------------------
        "project-financials": (
            route_name
        ),
        "project-financial": (
            route_name
        ),

        # ----------------------------------------------------
        # uppercase
        # ----------------------------------------------------
        "PROJECT_FINANCIALS": (
            plural_name.upper()
        ),
        "PROJECT_FINANCIAL": (
            module_name.upper()
        ),

        # ----------------------------------------------------
        # title / readable names
        # ----------------------------------------------------
        "Project Financials": (
            api_config["display_name"]
        ),
        "Project Financial": (
            api_config["display_name"]
        ),

        # ----------------------------------------------------
        # source
        # ----------------------------------------------------
        "project_financial_vw": (
            source_view
        ),
    }

    return replacements


def apply_replacements(
    source: str,
    replacements: Dict[str, Any],
) -> str:
    """
    Apply string replacements.

    Longest keys are replaced first to prevent:
        project_financial
    from changing part of:
        project_financials
    too early.
    """

    normalized: Dict[str, str] = {}

    for old, new in replacements.items():
        if old is None:
            continue

        if new is None:
            continue

        normalized[str(old)] = str(new)

    for old in sorted(
        normalized.keys(),
        key=len,
        reverse=True,
    ):
        source = source.replace(
            old,
            normalized[old],
        )

    return source


# ============================================================
# FUNCTION-NAME REPLACEMENTS
# ============================================================

def fix_lookup_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize generated lookup function names.

    Example:
        po_funding_detail

    Expected repository:
        get_po_funding_detail_by_project_id

    rather than:
        get_po_funding_detail(...)
    """

    module_name = api_config["module_name"]
    lookup_function = api_config["lookup_function"]
    key_param = api_config["key_param"]

    generic_candidates = [
        f"get_{module_name}_by_project_id",
        f"get_{module_name}_by_proj_id",
        f"get_{module_name}_by_{key_param}",
    ]

    for candidate in generic_candidates:
        source = source.replace(
            candidate,
            lookup_function,
        )

    return source


def fix_search_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize search-function names from config.
    """

    plural_name = api_config["plural_name"]
    search_function = api_config["search_function"]

    candidates = [
        f"search_{plural_name}",
        f"search_{api_config['module_name']}",
    ]

    for candidate in candidates:
        source = source.replace(
            candidate,
            search_function,
        )

    return source


# ============================================================
# KEY COLUMN / PARAMETER
# ============================================================

def fix_key_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Replace project_financial template key references with
    the API-specific key.

    IMPORTANT:
    We intentionally work only on known parameter names rather
    than globally replacing every project_id occurrence.
    """

    key_param = api_config["key_param"]
    key_column = api_config["key_column"]
    sample_key = api_config["sample_key"]

    replacements = {
        # common test values
        '"P-1001"': f'"{sample_key}"',
        "'P-1001'": f"'{sample_key}'",

        # field names
        '"project_id"': f'"{key_column}"',
        "'project_id'": f"'{key_column}'",

        # variables
        "expected_project_id": (
            f"expected_{key_param}"
        ),
    }

    source = apply_replacements(
        source,
        replacements,
    )

    return source


# ============================================================
# NONE-FILTER FIX
# ============================================================

def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    Service behavior:

        current_filters = (
            FiltersEnvelope(filters=filters)
            if isinstance(filters, dict)
            else filters
        )

    Therefore:

        filters=None

    stays None.

    Remove template assertions expecting None to become a
    FiltersEnvelope.
    """

    pattern = r"""
        ^[ \t]*
        assert[ \t]+
        isinstance
        \(
            [ \t]*
            kwargs
            \[
                ["']filters["']
            \]
            [ \t]*,
            [ \t]*
            FiltersEnvelope
            [ \t]*
        \)
        [ \t]*$
    """

    source = re.sub(
        pattern,
        "",
        source,
        flags=re.MULTILINE | re.VERBOSE,
    )

    return clean_blank_lines(source)


# ============================================================
# REMOVE UNSUPPORTED KEYWORD ARGUMENT
# ============================================================

def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove a keyword argument from calls to a function.

    This parser intentionally does not use one giant regex.
    It walks matching function calls and handles nested
    parentheses.

    Example:

        get_x(
            project_id="P-1001",
            filters=None,
            page=page,
        )

    can have filters removed without damaging the call.
    """

    if not function_name:
        return source

    function_pattern = re.compile(
        rf"\b{re.escape(function_name)}\s*\("
    )

    matches = list(
        function_pattern.finditer(source)
    )

    if not matches:
        return source

    output = source

    # reverse order so previous offsets remain valid
    for match in reversed(matches):

        open_paren = output.find(
            "(",
            match.start(),
        )

        if open_paren < 0:
            continue

        depth = 0
        end_paren: Optional[int] = None

        in_single = False
        in_double = False
        escaped = False

        for index in range(
            open_paren,
            len(output),
        ):

            char = output[index]

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if (
                char == "'"
                and not in_double
            ):
                in_single = not in_single
                continue

            if (
                char == '"'
                and not in_single
            ):
                in_double = not in_double
                continue

            if in_single or in_double:
                continue

            if char == "(":
                depth += 1

            elif char == ")":
                depth -= 1

                if depth == 0:
                    end_paren = index
                    break

        if end_paren is None:
            continue

        call_start = match.start()

        call_text = output[
            call_start:
            end_paren + 1
        ]

        line_pattern = rf"""
            ^[ \t]*
            {re.escape(argument_name)}
            [ \t]*=
            [^\n]*
            \n?
        """

        cleaned = re.sub(
            line_pattern,
            "",
            call_text,
            flags=re.MULTILINE | re.VERBOSE,
        )

        output = (
            output[:call_start]
            + cleaned
            + output[end_paren + 1:]
        )

    return output


# ============================================================
# MOCK ASSERTIONS
# ============================================================

def normalize_repository_mock_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    The service creates default PaginationModel and SortModel
    before calling the repository.

    Therefore generated tests should not expect:

        page=None
        sort=None

    when the actual service sends instantiated objects.

    Use ANY for those defaults in mock assertions.
    """

    source = re.sub(
        r"\bpage\s*=\s*None",
        "page=ANY",
        source,
    )

    source = re.sub(
        r"\bsort\s*=\s*None",
        "sort=ANY",
        source,
    )

    # If the service does not pass filters to the by-key repo,
    # remove filters expectation for that lookup.
    if not api_config.get(
        "lookup_supports_filters",
        False,
    ):
        source = remove_keyword_argument_from_calls(
            source,
            (
                "mock_"
                + api_config["module_name"]
                + "_repo."
                + api_config["lookup_function"]
                + ".assert_called_once_with"
            ),
            "filters",
        )

    return source


# ============================================================
# PAGINATION ARGUMENT NORMALIZATION
# ============================================================

def remove_old_limit_cursor_arguments(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Current APIs use PaginationModel(page=...) rather than
    standalone:
        limit=
        cursor=

    Remove legacy standalone args from service calls when
    configured.
    """

    if not api_config.get(
        "uses_pagination_model",
        True,
    ):
        return source

    candidates = [
        api_config["lookup_function"],
        api_config["search_function"],
        api_config.get(
            "service_lookup_function",
            "",
        ),
    ]

    for function_name in candidates:
        if not function_name:
            continue

        source = remove_keyword_argument_from_calls(
            source,
            function_name,
            "limit",
        )

        source = remove_keyword_argument_from_calls(
            source,
            function_name,
            "cursor",
        )

    return source


# ============================================================
# HANDLER POST-PROCESSING
# ============================================================

def fix_handler_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Handler names are explicitly config driven.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config[
        "handler_search_function"
    ]

    details_target = api_config[
        "handler_details_function"
    ]

    search_candidates = [
        f"search_{module_name}_v1",
        f"search_{plural_name}_v1",
        f"search_{module_name}",
        f"search_{plural_name}",
    ]

    for candidate in search_candidates:
        source = source.replace(
            candidate,
            search_target,
        )

    detail_candidates = [
        f"get_{module_name}_details",
        f"get_{plural_name}_details",
    ]

    for candidate in detail_candidates:
        source = source.replace(
            candidate,
            details_target,
        )

    return source


def remove_nonexistent_handler_tests(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Optional config support.

    Example:

        "generate_search_handler_tests": False

    allows an API that has no search handler to avoid generating
    invalid tests.

    Default is True.
    """

    if api_config.get(
        "generate_search_handler_tests",
        True,
    ):
        return source

    search_name = api_config[
        "handler_search_function"
    ]

    # Remove functions whose body references this missing
    # search handler.
    pattern = rf"""
        ^def[ \t]+test_[^\n]+
        \n
        (?:
            (?!^def[ \t]+test_).*\n
        )*
        (?:
            .*{re.escape(search_name)}.*
        )
        (?:
            (?!^def[ \t]+test_).*\n
        )*
    """

    try:
        source = re.sub(
            pattern,
            "",
            source,
            flags=re.MULTILINE | re.VERBOSE,
        )
    except re.error:
        # Never allow optional cleanup to crash generator.
        pass

    return source


# ============================================================
# IMPORT NORMALIZATION
# ============================================================

def ensure_any_import(
    source: str,
) -> str:
    """
    Add ANY when generated service tests use ANY.
    """

    if "ANY" not in source:
        return source

    if re.search(
        r"from\s+unittest\.mock\s+import[^\n]*\bANY\b",
        source,
    ):
        return source

    match = re.search(
        r"from\s+unittest\.mock\s+import\s+([^\n]+)",
        source,
    )

    if match:
        current = match.group(1)

        replacement = (
            "from unittest.mock import "
            + current.rstrip()
            + ", ANY"
        )

        source = (
            source[:match.start()]
            + replacement
            + source[match.end():]
        )

        return source

    return (
        "from unittest.mock import ANY\n"
        + source
    )


# ============================================================
# CUSTOM CONFIG REPLACEMENTS
# ============================================================

def apply_custom_replacements(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Apply API-specific overrides only after normal generic
    replacements.

    This lets future APIs add special differences without
    changing generator code.
    """

    replacements = api_config.get(
        "replacements",
        {},
    )

    if not replacements:
        return source

    return apply_replacements(
        source,
        replacements,
    )


# ============================================================
# TEST-TYPE POST PROCESSING
# ============================================================

def post_process_db(
    source: str,
    api_config: Dict[str, Any],
) -> str:

    source = fix_lookup_function_names(
        source,
        api_config,
    )

    source = fix_key_parameter(
        source,
        api_config,
    )

    source = remove_old_limit_cursor_arguments(
        source,
        api_config,
    )

    return clean_blank_lines(source)


def post_process_model(
    source: str,
    api_config: Dict[str, Any],
) -> str:

    source = fix_key_parameter(
        source,
        api_config,
    )

    return clean_blank_lines(source)


def post_process_service(
    source: str,
    api_config: Dict[str, Any],
) -> str:

    source = fix_lookup_function_names(
        source,
        api_config,
    )

    source = fix_search_function_names(
        source,
        api_config,
    )

    source = fix_key_parameter(
        source,
        api_config,
    )

    source = fix_none_filter_expectations(
        source,
    )

    source = remove_old_limit_cursor_arguments(
        source,
        api_config,
    )

    source = normalize_repository_mock_assertions(
        source,
        api_config,
    )

    source = ensure_any_import(
        source,
    )

    return clean_blank_lines(source)


def post_process_handler(
    source: str,
    api_config: Dict[str, Any],
) -> str:

    source = fix_key_parameter(
        source,
        api_config,
    )

    source = fix_handler_function_names(
        source,
        api_config,
    )

    source = remove_nonexistent_handler_tests(
        source,
        api_config,
    )

    return clean_blank_lines(source)


# ============================================================
# MAIN TEMPLATE RENDER
# ============================================================

def render_test(
    test_type: str,
    template_source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Render one test file.
    """

    source = template_source

    # --------------------------------------------------------
    # 1. Generic name replacements
    # --------------------------------------------------------

    source = apply_replacements(
        source,
        build_standard_replacements(
            api_config
        ),
    )

    # --------------------------------------------------------
    # 2. API-specific overrides from config
    # --------------------------------------------------------

    source = apply_custom_replacements(
        source,
        api_config,
    )

    # --------------------------------------------------------
    # 3. Test-type-specific normalization
    # --------------------------------------------------------

    if test_type == "db":
        source = post_process_db(
            source,
            api_config,
        )

    elif test_type == "model":
        source = post_process_model(
            source,
            api_config,
        )

    elif test_type == "service":
        source = post_process_service(
            source,
            api_config,
        )

    elif test_type == "handler":
        source = post_process_handler(
            source,
            api_config,
        )

    else:
        raise ValueError(
            f"Unknown test type: {test_type}"
        )

    return source


# ============================================================
# TEMPLATE VALIDATION
# ============================================================

def validate_templates(
    selected_type: Optional[str] = None,
) -> bool:
    """
    Verify required Project Financial template files exist.
    """

    missing = []

    types_to_check = (
        [selected_type]
        if selected_type
        else TEST_TYPES
    )

    for test_type in types_to_check:

        if test_type not in TEMPLATE_FILES:
            missing.append(
                (
                    test_type,
                    "<not configured>",
                )
            )
            continue

        path = normalize_path(
            TEMPLATE_FILES[test_type]
        )

        if not path.exists():
            missing.append(
                (
                    test_type,
                    str(path),
                )
            )

    if not missing:
        return True

    print()
    print("ERROR: Missing template files:")
    print()

    for test_type, path in missing:
        print(
            f"  {test_type:8} {path}"
        )

    print()
    print(
        "The generator requires the existing "
        "project_financial tests."
    )
    print()

    return False


# ============================================================
# DESTINATION
# ============================================================

def destination_file(
    test_type: str,
    api_config: Dict[str, Any],
) -> Path:
    """
    Return generated test destination.
    """

    module_name = api_config["module_name"]

    root = normalize_path(
        DESTINATION_DIRS[test_type]
    )

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
            f"Invalid test type: {test_type}"
        )

    return root / filename


# ============================================================
# GENERATE ONE TEST
# ============================================================

def generate_one(
    test_type: str,
    api_config: Dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> bool:
    """
    Generate one test file.

    Returns True when generated/planned.
    Returns False when skipped.
    """

    template_path = normalize_path(
        TEMPLATE_FILES[test_type]
    )

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
        return False

    try:
        template_source = (
            template_path.read_text(
                encoding="utf-8"
            )
        )
    except UnicodeDecodeError:
        template_source = (
            template_path.read_text(
                encoding="utf-8-sig"
            )
        )

    generated_source = render_test(
        test_type,
        template_source,
        api_config,
    )

    if dry_run:
        print(
            f"DRY    [{test_type:<7}] "
            f"{destination}"
        )
        return True

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        generated_source,
        encoding="utf-8",
    )

    print(
        f"CREATE [{test_type:<7}] "
        f"{destination}"
    )

    return True


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
    """
    Generate configured tests for one API.
    """

    if api_name not in APIS:
        print()
        print(
            f"ERROR: API '{api_name}' "
            "is not configured."
        )
        print()
        print("Run:")
        print()
        print(
            "  py generate_api_tests.py --list"
        )
        print()
        return

    api_config = prepare_api_config(
        api_name,
        APIS[api_name],
    )

    if not validate_templates(
        selected_type
    ):
        return

    print()
    print(
        "=" * 78
    )
    print(
        f"Generating tests for API: "
        f"{api_name}"
    )
    print(
        f"Key column: "
        f"{api_config['key_column']}"
    )
    print(
        f"Lookup function: "
        f"{api_config['lookup_function']}"
    )
    print(
        "=" * 78
    )

    generated = 0
    skipped = 0

    types_to_generate = (
        [selected_type]
        if selected_type
        else TEST_TYPES
    )

    for test_type in types_to_generate:

        result = generate_one(
            test_type,
            api_config,
            force=force,
            dry_run=dry_run,
        )

        if result:
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
# LIST
# ============================================================

def list_apis() -> None:
    """
    Print all configured APIs.
    """

    print()
    print("Configured APIs")
    print(
        "=" * 78
    )

    if not APIS:
        print(
            "No APIs configured."
        )
        print()
        return

    for api_name in sorted(
        APIS.keys()
    ):

        config = prepare_api_config(
            api_name,
            APIS[api_name],
        )

        print(
            f"{api_name:<30} "
            f"key={config['key_column']:<20} "
            f"lookup={config['lookup_function']}"
        )

    print()


# ============================================================
# ARGUMENTS
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests from the "
            "Project Financial template tests."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help=(
            "Configured API name, for example "
            "po_funding_detail"
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
            "Overwrite existing generated files."
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
        "--test-type",
        choices=list(TEST_TYPES),
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

    if args.list:
        list_apis()
        return

    if not args.api:
        parser.print_help()
        print()
        print("Examples:")
        print()
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
        print(
            "  py generate_api_tests.py "
            "po_funding_detail "
            "--test-type service --force"
        )
        return

    generate_api(
        args.api,
        force=args.force,
        dry_run=args.dry_run,
        selected_type=args.test_type,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
