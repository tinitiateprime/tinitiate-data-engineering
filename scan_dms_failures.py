"""
generate_api_tests.py

Generic unit-test generator for the MT-DM API project.

This version keeps SERVICE function names separate from HANDLER function names.

Example for po_funding_detail:
    service_search_function = "search_po_funding_detail"
    handler_search_function = "search_po_funding_detail_v1"

That distinction is important:
    - handler tests PATCH the service function
    - handler tests CALL the handler function

Usage:
    py generate_api_tests.py --list
    py generate_api_tests.py po_funding_detail --dry-run
    py generate_api_tests.py po_funding_detail --force
    py generate_api_tests.py po_funding_detail --test-type handler --force
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

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
    print(exc)
    print()
    print("Expected api_test_config.py to contain:")
    print("  APIS")
    print("  TEMPLATE_FILES")
    print("  DESTINATION_DIRS")
    print("  TEST_TYPES")
    print()
    sys.exit(1)


# =============================================================================
# GENERAL HELPERS
# =============================================================================

def snake_to_pascal(value: str) -> str:
    return "".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def snake_to_title(value: str) -> str:
    return " ".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def normalize_path(value: Any) -> Path:
    if isinstance(value, Path):
        return value
    return Path(str(value))


def get_config_value(
    api_config: Dict[str, Any],
    name: str,
    default: Any = None,
) -> Any:
    value = api_config.get(name)
    return default if value is None else value


def clean_blank_lines(source: str) -> str:
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


def replace_longest_first(
    source: str,
    replacements: Dict[str, Any],
) -> str:
    normalized: Dict[str, str] = {}

    for old, new in replacements.items():
        if old is None or new is None:
            continue

        old_text = str(old)
        new_text = str(new)

        if not old_text:
            continue

        normalized[old_text] = new_text

    for old in sorted(
        normalized,
        key=len,
        reverse=True,
    ):
        source = source.replace(
            old,
            normalized[old],
        )

    return source


# =============================================================================
# API CONFIG NORMALIZATION
# =============================================================================

def prepare_api_config(
    api_name: str,
    raw_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize one API configuration.

    IMPORTANT:
    service_search_function and handler_search_function are intentionally
    separate values.
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
        get_config_value(
            config,
            "key_argument",
            "project_id",
        ),
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

    # Repository lookup/search functions
    repo_search_function = get_config_value(
        config,
        "repo_search_function",
        get_config_value(
            config,
            "lookup_function",
            f"get_{module_name}",
        ),
    )

    repo_key_function = get_config_value(
        config,
        "repo_key_function",
        get_config_value(
            config,
            "lookup_function",
            f"get_{module_name}_by_{key_param}",
        ),
    )

    # Service functions
    service_search_function = get_config_value(
        config,
        "service_search_function",
        get_config_value(
            config,
            "search_function",
            f"search_{plural_name}",
        ),
    )

    service_key_function = get_config_value(
        config,
        "service_key_function",
        get_config_value(
            config,
            "details_function",
            f"get_{module_name}_by_{key_param}",
        ),
    )

    # Handler functions
    handler_search_function = get_config_value(
        config,
        "handler_search_function",
        f"search_{plural_name}_v1",
    )

    handler_key_function = get_config_value(
        config,
        "handler_key_function",
        get_config_value(
            config,
            "handler_details_function",
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
            "key_argument": key_param,
            "sample_key": sample_key,
            "source_view": source_view,
            "repo_search_function": repo_search_function,
            "repo_key_function": repo_key_function,
            "lookup_function": repo_key_function,
            "service_search_function": service_search_function,
            "service_key_function": service_key_function,
            "search_function": service_search_function,
            "details_function": service_key_function,
            "handler_search_function": handler_search_function,
            "handler_key_function": handler_key_function,
            "handler_details_function": handler_key_function,
            "response_model": response_model,
            "search_response_model": search_response_model,
        }
    )

    return config


# =============================================================================
# STANDARD TEMPLATE REPLACEMENTS
# =============================================================================

def build_standard_replacements(
    api_config: Dict[str, Any],
) -> Dict[str, str]:
    """
    Replace Project Financial template names with target API names.

    Function-name replacement is intentionally NOT handled here because
    service and handler names must remain distinct.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]
    pascal_name = api_config["pascal_name"]
    route_name = api_config["route_name"]
    source_view = api_config["source_view"]
    display_name = api_config["display_name"]

    replacements: Dict[str, str] = {
        # PascalCase
        "ProjectFinancials": pascal_name + "s",
        "ProjectFinancial": pascal_name,

        # snake_case
        "project_financials": plural_name,
        "project_financial": module_name,

        # kebab-case routes
        "project-financials": route_name,
        "project-financial": route_name,

        # uppercase
        "PROJECT_FINANCIALS": plural_name.upper(),
        "PROJECT_FINANCIAL": module_name.upper(),

        # readable names
        "Project Financials": display_name,
        "Project Financial": display_name,

        # view
        "project_financial_vw": source_view,
        "project_financials_vw": source_view,
    }

    return replacements


def apply_replacements(
    source: str,
    replacements: Dict[str, Any],
) -> str:
    return replace_longest_first(
        source,
        replacements,
    )


# =============================================================================
# FUNCTION NAME REPLACEMENTS
# =============================================================================

def fix_repository_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    repo_search = api_config["repo_search_function"]
    repo_key = api_config["repo_key_function"]

    replacements = {
        "get_project_financial_by_project_id": repo_key,
        "get_project_financial": repo_search,
    }

    return replace_longest_first(
        source,
        replacements,
    )


def fix_service_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    service_search = api_config["service_search_function"]
    service_key = api_config["service_key_function"]

    replacements = {
        "get_project_financial_by_project": service_key,
        "search_project_financials": service_search,
        "search_project_financial": service_search,
    }

    return replace_longest_first(
        source,
        replacements,
    )


def collapse_repeated_v1(
    source: str,
    expected_handler: Optional[str],
) -> str:
    if not expected_handler:
        return source

    base = re.sub(
        r"(?:_v1)+$",
        "",
        expected_handler,
    )

    if expected_handler.endswith("_v1"):
        source = re.sub(
            rf"\b{re.escape(base)}(?:_v1)+\b",
            expected_handler,
            source,
        )

    return source


def repair_handler_service_patch(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Critical fix.

    Handler tests must PATCH service_search_function, but CALL
    handler_search_function.

    Example:
        patch  search_po_funding_detail
        call   search_po_funding_detail_v1
    """

    module_name = api_config["module_name"]
    service_search = api_config["service_search_function"]
    handler_search = api_config["handler_search_function"]

    if (
        not service_search
        or not handler_search
        or service_search == handler_search
    ):
        return source

    # Repair:
    #
    # @patch.object(
    #     po_funding_detail,
    #     "search_po_funding_detail_v1",
    # )
    #
    # to:
    #
    # @patch.object(
    #     po_funding_detail,
    #     "search_po_funding_detail",
    # )
    patch_pattern = (
        r"(@patch\.object\(\s*"
        + re.escape(module_name)
        + r"\s*,\s*[\"'])"
        + re.escape(handler_search)
        + r"([\"']\s*,?\s*\))"
    )

    source = re.sub(
        patch_pattern,
        lambda m: (
            m.group(1)
            + service_search
            + m.group(2)
        ),
        source,
        flags=re.MULTILINE,
    )

    return source


def fix_handler_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize handler names WITHOUT turning service mocks into handler mocks.

    This is the most important difference from the old generator.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    handler_search = api_config["handler_search_function"]
    handler_key = api_config.get("handler_key_function")

    # First repair repeated suffixes such as _v1_v1.
    source = collapse_repeated_v1(
        source,
        handler_search,
    )

    # Replace only handler-style template names (those already ending in _v1).
    handler_search_candidates = [
        "search_project_financials_v1",
        "search_project_financial_v1",
        f"search_{plural_name}_v1",
        f"search_{module_name}_v1",
    ]

    for candidate in sorted(
        set(handler_search_candidates),
        key=len,
        reverse=True,
    ):
        if candidate != handler_search:
            source = source.replace(
                candidate,
                handler_search,
            )

    # Replace details handler only when configured.
    if handler_key:
        detail_candidates = [
            "get_project_financial_details",
            "get_project_financial_detail",
            f"get_{plural_name}_details",
            f"get_{module_name}_details",
            f"get_{plural_name}_detail",
            f"get_{module_name}_detail",
        ]

        for candidate in sorted(
            set(detail_candidates),
            key=len,
            reverse=True,
        ):
            if candidate != handler_key:
                source = source.replace(
                    candidate,
                    handler_key,
                )

    # Finally ensure handler mock decorators still patch the service.
    source = repair_handler_service_patch(
        source,
        api_config,
    )

    return source


# =============================================================================
# KEY / SAMPLE DATA REPLACEMENTS
# =============================================================================

def fix_key_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    key_param = api_config["key_param"]
    key_column = api_config["key_column"]
    sample_key = api_config["sample_key"]

    replacements = {
        '"P-1001"': f'"{sample_key}"',
        "'P-1001'": f"'{sample_key}'",

        '"project_id"': f'"{key_column}"',
        "'project_id'": f"'{key_column}'",

        "expected_project_id": f"expected_{key_param}",
    }

    return replace_longest_first(
        source,
        replacements,
    )


# =============================================================================
# NONE FILTER EXPECTATION FIX
# =============================================================================

def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    Remove template assertions that require filters=None to become
    FiltersEnvelope when the target service intentionally leaves None as None.
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


# =============================================================================
# SAFE KEYWORD ARGUMENT REMOVAL
# =============================================================================

def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove one named keyword argument from calls to function_name while
    respecting nested parentheses and quoted strings.
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

            if char == "'" and not in_double:
                in_single = not in_single
                continue

            if char == '"' and not in_single:
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

        # Handles a keyword on its own normal formatted line.
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


# =============================================================================
# PAGINATION / REPOSITORY MOCK NORMALIZATION
# =============================================================================

def remove_old_limit_cursor_arguments(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    if not api_config.get(
        "uses_pagination_model",
        True,
    ):
        return source

    candidates = [
        api_config.get("repo_key_function"),
        api_config.get("repo_search_function"),
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


def ensure_any_import(
    source: str,
) -> str:
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

        return (
            source[:match.start()]
            + replacement
            + source[match.end():]
        )

    return (
        "from unittest.mock import ANY\n"
        + source
    )


def normalize_repository_mock_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Current services may construct PaginationModel/SortModel internally, so
    generated tests should not require page=None or sort=None when those
    values are actual instantiated objects.
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
        repo_key = api_config.get(
            "repo_key_function",
            "",
        )

        mock_names = [
            f"mock_{repo_key}",
            f"mock_{api_config['module_name']}_repo.{repo_key}",
        ]

        # General removal from calls to the by-key repository function.
        if repo_key:
            source = remove_keyword_argument_from_calls(
                source,
                repo_key,
                "filters",
            )

    return source


# =============================================================================
# OPTIONAL HANDLER TEST REMOVAL
# =============================================================================

def remove_nonexistent_handler_tests(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Remove details-handler tests when the API does not expose a separate
    details handler.
    """

    handler_key = api_config.get(
        "handler_key_function"
    )

    supports_handler_key = api_config.get(
        "supports_handler_key_lookup",
        bool(handler_key),
    )

    if supports_handler_key and handler_key:
        return source

    # Remove functions that reference known details-handler template names.
    candidate_names = [
        "get_project_financial_details",
        "get_project_financial_detail",
    ]

    # Also remove tests that explicitly say details_handler.
    pattern = r"""
        ^def[ \t]+test_[^\n]*
        (?:
            details_handler
            |
            get_project_financial_details
            |
            get_project_financial_detail
        )
        [^\n]*\n
        (?:
            (?!^def[ \t]+test_)
            .*\n?
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
        pass

    return clean_blank_lines(source)


# =============================================================================
# CUSTOM CONFIG REPLACEMENTS
# =============================================================================

def apply_custom_replacements(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    replacements = api_config.get(
        "replacements",
        {},
    )

    if not replacements:
        return source

    return replace_longest_first(
        source,
        replacements,
    )


# =============================================================================
# TEST-TYPE POST PROCESSING
# =============================================================================

def post_process_db(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    source = fix_repository_function_names(
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
    source = fix_repository_function_names(
        source,
        api_config,
    )

    source = fix_service_function_names(
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
    """
    Handler processing order matters.

    Do standard API naming first, then explicitly repair the service mock
    target so @patch.object never patches the handler itself.
    """

    source = fix_service_function_names(
        source,
        api_config,
    )

    source = fix_key_parameter(
        source,
        api_config,
    )

    source = fix_handler_function_names(
        source,
        api_config,
    )

    # Do this a second time as a final safety guard.
    source = repair_handler_service_patch(
        source,
        api_config,
    )

    source = remove_nonexistent_handler_tests(
        source,
        api_config,
    )

    return clean_blank_lines(source)


# =============================================================================
# MAIN TEMPLATE RENDER
# =============================================================================

def render_test(
    test_type: str,
    template_source: str,
    api_config: Dict[str, Any],
) -> str:
    source = template_source

    # 1. Generic non-function naming replacements
    source = apply_replacements(
        source,
        build_standard_replacements(
            api_config,
        ),
    )

    # 2. API-specific overrides
    source = apply_custom_replacements(
        source,
        api_config,
    )

    # 3. Test-type-specific processing
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


# =============================================================================
# TEMPLATE VALIDATION
# =============================================================================

def validate_templates(
    selected_type: Optional[str] = None,
) -> bool:
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
        "Project Financial template tests."
    )
    print()

    return False


# =============================================================================
# DESTINATION
# =============================================================================

def destination_file(
    test_type: str,
    api_config: Dict[str, Any],
) -> Path:
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


# =============================================================================
# GENERATE ONE TEST
# =============================================================================

def generate_one(
    test_type: str,
    api_config: Dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> bool:
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
        template_source = template_path.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        template_source = template_path.read_text(
            encoding="utf-8-sig"
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


# =============================================================================
# GENERATE API
# =============================================================================

def generate_api(
    api_name: str,
    *,
    force: bool = False,
    dry_run: bool = False,
    selected_type: Optional[str] = None,
) -> None:
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
    print("=" * 78)
    print(
        f"Generating tests for API: "
        f"{api_name}"
    )
    print(
        f"Service search: "
        f"{api_config['service_search_function']}"
    )
    print(
        f"Handler search: "
        f"{api_config['handler_search_function']}"
    )
    print(
        f"Key column: "
        f"{api_config['key_column']}"
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


# =============================================================================
# LIST
# =============================================================================

def list_apis() -> None:
    print()
    print("Configured APIs")
    print("=" * 78)

    if not APIS:
        print("No APIs configured.")
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
            f"service={config['service_search_function']:<32} "
            f"handler={config['handler_search_function']}"
        )

    print()


# =============================================================================
# ARGUMENTS
# =============================================================================

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
        help="Overwrite existing generated files.",
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
        help="Generate only one test type.",
    )

    return parser


# =============================================================================
# MAIN
# =============================================================================

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
            "--test-type handler --force"
        )
        return

    generate_api(
        args.api,
        force=args.force,
        dry_run=args.dry_run,
        selected_type=args.test_type,
    )


if __name__ == "__main__":
    main()
