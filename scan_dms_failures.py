"""
generate_api_tests.py

Generic API unit-test generator for the MT-DM API project.

The generator uses the existing Project Financial tests as templates
and creates tests for APIs defined in api_test_config.py.

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
    print("Expected api_test_config.py to contain:")
    print("  APIS")
    print("  TEMPLATE_FILES")
    print("  DESTINATION_DIRS")
    print("  TEST_TYPES")
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
    po_funding_detail -> Po Funding Detail
    """
    return " ".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def normalize_path(value: Any) -> Path:
    """
    Convert a config path value into pathlib.Path.
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
# API CONFIG NORMALIZATION
# ============================================================

def prepare_api_config(
    api_name: str,
    raw_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build normalized API configuration.

    Anything that differs between APIs should preferably
    live in api_test_config.py.
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
        get_config_value(
            config,
            "key_argument",
            key_column,
        ),
    )

    sample_key = str(
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
        get_config_value(
            config,
            "repo_key_function",
            f"get_{module_name}_by_{key_param}",
        ),
    )

    search_function = get_config_value(
        config,
        "search_function",
        get_config_value(
            config,
            "repo_search_function",
            f"search_{plural_name}",
        ),
    )

    service_search_function = get_config_value(
        config,
        "service_search_function",
        search_function,
    )

    service_key_function = get_config_value(
        config,
        "service_key_function",
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
        get_config_value(
            config,
            "handler_key_function",
            None,
        ),
    )

    response_model = get_config_value(
        config,
        "response_model",
        f"{pascal_name}Response",
    )

    search_response_model = get_config_value(
        config,
        "search_response_model",
        f"{pascal_name}SearchServiceResponse",
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
            "sample_key": sample_key,
            "source_view": source_view,
            "lookup_function": lookup_function,
            "search_function": search_function,
            "service_search_function": service_search_function,
            "service_key_function": service_key_function,
            "handler_search_function": handler_search_function,
            "handler_details_function": handler_details_function,
            "response_model": response_model,
            "search_response_model": search_response_model,
        }
    )

    return config


# ============================================================
# STANDARD TEMPLATE REPLACEMENTS
# ============================================================

def build_standard_replacements(
    api_config: Dict[str, Any],
) -> Dict[str, str]:
    """
    Convert Project Financial template naming into
    target API naming.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]
    pascal_name = api_config["pascal_name"]
    route_name = api_config["route_name"]
    display_name = api_config["display_name"]
    source_view = api_config["source_view"]

    replacements: Dict[str, str] = {
        # ----------------------------------------------------
        # PascalCase
        # ----------------------------------------------------
        "ProjectFinancials": pascal_name + "s",
        "ProjectFinancial": pascal_name,

        # ----------------------------------------------------
        # snake_case
        # ----------------------------------------------------
        "project_financials": plural_name,
        "project_financial": module_name,

        # ----------------------------------------------------
        # kebab-case
        # ----------------------------------------------------
        "project-financials": route_name,
        "project-financial": route_name,

        # ----------------------------------------------------
        # uppercase
        # ----------------------------------------------------
        "PROJECT_FINANCIALS": plural_name.upper(),
        "PROJECT_FINANCIAL": module_name.upper(),

        # ----------------------------------------------------
        # readable display
        # ----------------------------------------------------
        "Project Financials": display_name + "s",
        "Project Financial": display_name,

        # ----------------------------------------------------
        # source view
        # ----------------------------------------------------
        "project_financial_vw": source_view,
    }

    return replacements


def apply_replacements(
    source: str,
    replacements: Dict[str, Any],
) -> str:
    """
    Apply string replacements.

    Longest keys are replaced first so that:

        project_financial

    does not accidentally change part of:

        project_financials
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
# FUNCTION NAME FIXES
# ============================================================

def fix_lookup_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize generated repository/service lookup function names.
    """

    module_name = api_config["module_name"]
    key_param = api_config["key_param"]
    lookup_function = api_config["lookup_function"]

    candidates = [
        f"get_{module_name}_by_project_id",
        f"get_{module_name}_by_proj_id",
        f"get_{module_name}_by_{key_param}",
    ]

    for candidate in candidates:
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
    Normalize search function names from config.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    repo_search_function = api_config["search_function"]
    service_search_function = api_config[
        "service_search_function"
    ]

    generic_candidates = [
        f"search_{plural_name}",
        f"search_{module_name}",
    ]

    for candidate in generic_candidates:
        source = source.replace(
            candidate,
            service_search_function,
        )

    # Explicit Project Financial template names
    source = source.replace(
        "search_project_financials",
        service_search_function,
    )

    source = source.replace(
        "get_project_financial",
        repo_search_function,
    )

    return source


# ============================================================
# KEY COLUMN / PARAMETER NORMALIZATION
# ============================================================

def fix_key_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Replace Project Financial template key references with
    API-specific key information.
    """

    key_param = api_config["key_param"]
    key_column = api_config["key_column"]
    sample_key = api_config["sample_key"]

    replacements = {
        # common template values
        '"P-1001"': f'"{sample_key}"',
        "'P-1001'": f"'{sample_key}'",

        # field names
        '"project_id"': f'"{key_column}"',
        "'project_id'": f"'{key_column}'",

        # direct Python parameter
        "project_id=": f"{key_param}=",

        # expected variable
        "expected_project_id": f"expected_{key_param}",
    }

    return apply_replacements(
        source,
        replacements,
    )


# ============================================================
# NONE FILTER FIX
# ============================================================

def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    Some service implementations keep filters=None instead of
    converting it to FiltersEnvelope.

    Remove assertions inherited from template tests that require
    None to become FiltersEnvelope.
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
# FUNCTION CALL PARSER
# ============================================================

def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove a keyword argument from calls to one function.

    Handles multiline calls and nested parentheses more safely
    than one large regex.
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

    # Reverse order keeps previous offsets valid.
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

        # Match a complete keyword argument line.
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
# REPOSITORY MOCK ASSERTIONS
# ============================================================

def normalize_repository_mock_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Service code commonly creates default PaginationModel and
    SortModel objects before calling repository functions.

    Generated tests should therefore avoid expecting page=None
    or sort=None when actual objects are passed.
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
# PAGINATION NORMALIZATION
# ============================================================

def remove_old_limit_cursor_arguments(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Current APIs use PaginationModel(page=...) instead of
    standalone limit/cursor arguments.

    Remove legacy standalone args when configured.
    """

    if not api_config.get(
        "uses_pagination_model",
        True,
    ):
        return source

    candidates = [
        api_config.get("lookup_function"),
        api_config.get("search_function"),
        api_config.get("service_key_function"),
        api_config.get("service_search_function"),
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
# HANDLER NORMALIZATION
# ============================================================

def fix_handler_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Handler names are config-driven.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config[
        "handler_search_function"
    ]

    details_target = api_config.get(
        "handler_details_function"
    )

    search_candidates = [
        f"search_{module_name}_v1",
        f"search_{plural_name}_v1",
        f"search_{module_name}",
        f"search_{plural_name}",
        "search_project_financials_v1",
        "search_project_financial_v1",
    ]

    for candidate in search_candidates:
        source = source.replace(
            candidate,
            search_target,
        )

    if details_target:
        detail_candidates = [
            f"get_{module_name}_details",
            f"get_{plural_name}_details",
            "get_project_financial_details",
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
    Remove template tests for handler functions that do not exist.
    """

    # Search handler not supported.
    if not api_config.get(
        "supports_search",
        True,
    ):
        search_name = api_config.get(
            "handler_search_function"
        )

        if search_name:
            source = remove_test_functions_containing(
                source,
                search_name,
            )

    # No separate details handler.
    if not api_config.get(
        "supports_handler_key_lookup",
        False,
    ):
        details_name = api_config.get(
            "handler_details_function"
        )

        if details_name:
            source = remove_test_functions_containing(
                source,
                details_name,
            )

        # Also remove remaining Project Financial template
        # details tests.
        source = remove_test_functions_containing(
            source,
            "get_project_financial_details",
        )

    return clean_blank_lines(source)


def remove_test_functions_containing(
    source: str,
    text: str,
) -> str:
    """
    Remove complete top-level test functions whose body contains text.

    This is safer than attempting one massive regex over the entire
    module.
    """

    if not text:
        return source

    lines = source.splitlines(keepends=True)

    blocks = []
    start: Optional[int] = None

    for index, line in enumerate(lines):
        if re.match(
            r"^def\s+test_",
            line,
        ):
            if start is not None:
                blocks.append(
                    (start, index)
                )

            start = index

    if start is not None:
        blocks.append(
            (start, len(lines))
        )

    remove_ranges = []

    for block_start, block_end in blocks:
        block_text = "".join(
            lines[block_start:block_end]
        )

        if text in block_text:
            remove_ranges.append(
                (block_start, block_end)
            )

    if not remove_ranges:
        return source

    remove_indexes = set()

    for block_start, block_end in remove_ranges:
        remove_indexes.update(
            range(
                block_start,
                block_end,
            )
        )

    output = "".join(
        line
        for index, line in enumerate(lines)
        if index not in remove_indexes
    )

    return output


# ============================================================
# ANY IMPORT
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
# API-SPECIFIC OVERRIDES
# ============================================================

def apply_custom_replacements(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Apply API-specific overrides after generic substitutions.

    This allows future APIs to handle unusual differences without
    modifying the generator.
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
# TEST TYPE POST PROCESSING
# ============================================================

def post_process_db(
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
    # 1. Generic Project Financial -> target API replacements
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

    return clean_blank_lines(source)


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
    print(
        "ERROR: Missing Project Financial template files:"
    )
    print()

    for test_type, path in missing:
        print(
            f"  {test_type:8} {path}"
        )

    print()
    print(
        "The generator requires the existing "
        "Project Financial tests."
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
            "    py generate_api_tests.py --list"
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
    print("=" * 78)

    print(
        "Generating tests for API: "
        f"{api_name}"
    )

    print(
        "Key column: "
        f"{api_config['key_column']}"
    )

    print(
        "Lookup function: "
        f"{api_config['lookup_function']}"
    )

    print("=" * 78)

    generated = 0
    skipped = 0

    types_to_generate = (
        [selected_type]
        if selected_type
        else TEST_TYPES
    )

    for test_type in types_to_generate:

        # Optional per-API capabilities.
        capability_key = (
            f"generate_{test_type}_tests"
        )

        if api_config.get(
            capability_key,
            True,
        ) is False:

            print(
                f"SKIP   [{test_type:<7}] "
                "disabled by config"
            )

            skipped += 1
            continue

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
    print("=" * 78)

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
            "    py generate_api_tests.py --list"
        )

        print(
            "    py generate_api_tests.py "
            "po_funding_detail --dry-run"
        )

        print(
            "    py generate_api_tests.py "
            "po_funding_detail --force"
        )

        print(
            "    py generate_api_tests.py "
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
