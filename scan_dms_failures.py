"""
generate_api_tests.py

Generic API unit-test generator.

The generator uses the existing Project Financial tests as templates
and creates tests for APIs configured in api_test_config.py.

IMPORTANT
---------
Service and handler functions are intentionally kept separate.

Example:

    Service function:
        search_po_funding_detail

    Handler function:
        search_po_funding_detail_v1

Handler tests PATCH the service function and CALL the handler function.

Examples
--------

List configured APIs:

    py generate_api_tests.py --list

Dry run:

    py generate_api_tests.py po_funding_detail --dry-run

Generate all tests:

    py generate_api_tests.py po_funding_detail

Overwrite existing generated tests:

    py generate_api_tests.py po_funding_detail --force

Generate only handler test:

    py generate_api_tests.py po_funding_detail --test-type handler --force

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


# =============================================================================
# CONFIG IMPORTS
# =============================================================================

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
    Convert config path value to pathlib.Path.
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
    Safely retrieve one API configuration value.
    """

    value = api_config.get(name)

    if value is None:
        return default

    return value


def clean_blank_lines(source: str) -> str:
    """
    Prevent extremely large groups of blank lines.
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


# =============================================================================
# PREPARE CONFIG
# =============================================================================

def prepare_api_config(
    api_name: str,
    raw_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize API configuration.

    Very important:

    service_search_function
        is the function imported/used by the handler.

    handler_search_function
        is the Lambda/API handler itself.

    These MUST NOT be treated as the same function.
    """

    config = dict(raw_config)

    # -------------------------------------------------------------------------
    # Basic naming
    # -------------------------------------------------------------------------

    module_name = get_config_value(
        config,
        "module_name",
        api_name,
    )

    singular_name = get_config_value(
        config,
        "singular_name",
        module_name,
    )

    plural_name = get_config_value(
        config,
        "plural_name",
        singular_name,
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

    # -------------------------------------------------------------------------
    # Key
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Source
    # -------------------------------------------------------------------------

    source_view = get_config_value(
        config,
        "source_view",
        f"{module_name}_vw",
    )

    source_schema = get_config_value(
        config,
        "source_schema",
        "gold",
    )

    # -------------------------------------------------------------------------
    # Repository functions
    # -------------------------------------------------------------------------

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
        f"get_{module_name}_by_{key_param}",
    )

    # -------------------------------------------------------------------------
    # SERVICE FUNCTIONS
    # -------------------------------------------------------------------------

    service_search_function = get_config_value(
        config,
        "service_search_function",
        get_config_value(
            config,
            "search_function",
            f"search_{module_name}",
        ),
    )

    service_key_function = get_config_value(
        config,
        "service_key_function",
        f"get_{module_name}_by_{key_param}",
    )

    # -------------------------------------------------------------------------
    # HANDLER FUNCTIONS
    #
    # DO NOT collapse these into service function names.
    # -------------------------------------------------------------------------

    handler_search_function = get_config_value(
        config,
        "handler_search_function",
        f"search_{module_name}_v1",
    )

    handler_key_function = get_config_value(
        config,
        "handler_key_function",
        None,
    )

    # -------------------------------------------------------------------------
    # Models
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Defaults
    # -------------------------------------------------------------------------

    default_page_size = get_config_value(
        config,
        "default_page_size",
        100,
    )

    default_sort_field = get_config_value(
        config,
        "default_sort_field",
        "order_date",
    )

    default_sort_order = get_config_value(
        config,
        "default_sort_order",
        "desc",
    )

    # -------------------------------------------------------------------------
    # Capabilities
    # -------------------------------------------------------------------------

    supports_search = get_config_value(
        config,
        "supports_search",
        True,
    )

    supports_key_lookup = get_config_value(
        config,
        "supports_key_lookup",
        True,
    )

    supports_filters = get_config_value(
        config,
        "supports_filters",
        True,
    )

    supports_sort = get_config_value(
        config,
        "supports_sort",
        True,
    )

    supports_pagination = get_config_value(
        config,
        "supports_pagination",
        True,
    )

    supports_columns = get_config_value(
        config,
        "supports_columns",
        True,
    )

    supports_handler_key_lookup = get_config_value(
        config,
        "supports_handler_key_lookup",
        bool(handler_key_function),
    )

    generate_search_handler_tests = get_config_value(
        config,
        "generate_search_handler_tests",
        True,
    )

    uses_pagination_model = get_config_value(
        config,
        "uses_pagination_model",
        True,
    )

    lookup_supports_filters = get_config_value(
        config,
        "lookup_supports_filters",
        False,
    )

    # -------------------------------------------------------------------------
    # Update normalized configuration
    # -------------------------------------------------------------------------

    config.update(
        {
            "api_name": api_name,
            "module_name": module_name,
            "singular_name": singular_name,
            "plural_name": plural_name,
            "route_name": route_name,
            "pascal_name": pascal_name,
            "display_name": display_name,

            "key_column": key_column,
            "key_param": key_param,
            "sample_key": sample_key,

            "source_schema": source_schema,
            "source_view": source_view,

            "repo_search_function": repo_search_function,
            "repo_key_function": repo_key_function,

            "service_search_function": service_search_function,
            "service_key_function": service_key_function,

            "handler_search_function": handler_search_function,
            "handler_key_function": handler_key_function,

            "response_model": response_model,
            "search_response_model": search_response_model,

            "default_page_size": default_page_size,
            "default_sort_field": default_sort_field,
            "default_sort_order": default_sort_order,

            "supports_search": supports_search,
            "supports_key_lookup": supports_key_lookup,
            "supports_filters": supports_filters,
            "supports_sort": supports_sort,
            "supports_pagination": supports_pagination,
            "supports_columns": supports_columns,
            "supports_handler_key_lookup": supports_handler_key_lookup,

            "generate_search_handler_tests":
                generate_search_handler_tests,

            "uses_pagination_model": uses_pagination_model,
            "lookup_supports_filters": lookup_supports_filters,
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
    Standard Project Financial -> target API substitutions.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]
    route_name = api_config["route_name"]
    pascal_name = api_config["pascal_name"]
    display_name = api_config["display_name"]
    source_view = api_config["source_view"]

    replacements: Dict[str, str] = {
        # ---------------------------------------------------------------------
        # PascalCase
        # ---------------------------------------------------------------------

        "ProjectFinancials":
            pascal_name + "s",

        "ProjectFinancial":
            pascal_name,

        # ---------------------------------------------------------------------
        # snake_case plural
        # ---------------------------------------------------------------------

        "project_financials":
            plural_name,

        # ---------------------------------------------------------------------
        # snake_case singular
        # ---------------------------------------------------------------------

        "project_financial":
            module_name,

        # ---------------------------------------------------------------------
        # kebab-case
        # ---------------------------------------------------------------------

        "project-financials":
            route_name,

        "project-financial":
            route_name,

        # ---------------------------------------------------------------------
        # uppercase
        # ---------------------------------------------------------------------

        "PROJECT_FINANCIALS":
            plural_name.upper(),

        "PROJECT_FINANCIAL":
            module_name.upper(),

        # ---------------------------------------------------------------------
        # readable name
        # ---------------------------------------------------------------------

        "Project Financials":
            display_name,

        "Project Financial":
            display_name,

        # ---------------------------------------------------------------------
        # view
        # ---------------------------------------------------------------------

        "project_financial_vw":
            source_view,
    }

    return replacements


def apply_replacements(
    source: str,
    replacements: Dict[str, Any],
) -> str:
    """
    Apply replacements longest keys first.
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


# =============================================================================
# FUNCTION NAME NORMALIZATION
# =============================================================================

def fix_lookup_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize repository/key lookup function names.
    """

    module_name = api_config["module_name"]
    lookup_function = api_config["repo_key_function"]
    key_param = api_config["key_param"]

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
    Normalize SERVICE search function names.

    This function is only for service/repository-related generated code.

    Do NOT use this as the final handler-name correction.
    """

    plural_name = api_config["plural_name"]
    module_name = api_config["module_name"]
    service_search = api_config["service_search_function"]

    candidates = [
        f"search_{plural_name}",
        f"search_{module_name}",
    ]

    for candidate in candidates:
        source = source.replace(
            candidate,
            service_search,
        )

    return source


def fix_handler_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize handler function calls.

    Handler call:
        search_po_funding_detail_v1

    Service:
        search_po_funding_detail

    These are deliberately kept separate.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config[
        "handler_search_function"
    ]

    details_target = api_config.get(
        "handler_key_function"
    )

    # -------------------------------------------------------------------------
    # Handler search candidates
    # -------------------------------------------------------------------------

    search_candidates = [
        f"search_{module_name}_v1",
        f"search_{plural_name}_v1",
        f"search_{module_name}",
        f"search_{plural_name}",
    ]

    # Replace longer forms first
    search_candidates = sorted(
        set(search_candidates),
        key=len,
        reverse=True,
    )

    for candidate in search_candidates:

        # Do not accidentally replace the actual service patch string here.
        source = re.sub(
            rf"\b{re.escape(candidate)}\s*\(",
            f"{search_target}(",
            source,
        )

    # -------------------------------------------------------------------------
    # Details handler
    # -------------------------------------------------------------------------

    if details_target:

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


# =============================================================================
# KEY PARAMETER
# =============================================================================

def fix_key_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Replace template Project Financial key references.
    """

    key_param = api_config["key_param"]
    key_column = api_config["key_column"]
    sample_key = api_config["sample_key"]

    replacements = {
        '"P-1001"':
            f'"{sample_key}"',

        "'P-1001'":
            f"'{sample_key}'",

        '"project_id"':
            f'"{key_column}"',

        "'project_id'":
            f"'{key_column}'",

        "expected_project_id":
            f"expected_{key_param}",
    }

    return apply_replacements(
        source,
        replacements,
    )


# =============================================================================
# NONE FILTER FIX
# =============================================================================

def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    Current service logic can leave filters=None.

    Remove old template assertions that insist filters must be
    converted to FiltersEnvelope.
    """

    pattern = r"""
        ^[ \t]*
        assert[ \t]+
        isinstance
        \(
            [ \t]*
            kwargs
            \[
                [ \t]*
                ["']filters["']
                [ \t]*
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
# FUNCTION CALL ARGUMENT REMOVAL
# =============================================================================

def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove keyword argument from calls to a specific function.

    Supports nested parentheses better than a single regex.
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
            call_start:end_paren + 1
        ]

        # ---------------------------------------------------------------------
        # Remove argument_name=<value>,
        # one line or basic multi-line expression.
        # ---------------------------------------------------------------------

        argument_pattern = rf"""
            ^[ \t]*
            {re.escape(argument_name)}
            [ \t]*=
            [^\n]*
            \n?
        """

        cleaned = re.sub(
            argument_pattern,
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
# PAGINATION NORMALIZATION
# =============================================================================

def remove_old_limit_cursor_arguments(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Modern service functions use PaginationModel rather than standalone
    limit/cursor arguments.
    """

    if not api_config.get(
        "uses_pagination_model",
        True,
    ):
        return source

    candidates = [
        api_config.get("repo_search_function"),
        api_config.get("repo_key_function"),
        api_config.get("service_search_function"),
        api_config.get("service_key_function"),
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


# =============================================================================
# MOCK ASSERTION NORMALIZATION
# =============================================================================

def normalize_repository_mock_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Services create default PaginationModel / SortModel instances.

    Generated tests should not incorrectly require page=None/sort=None.

    ANY is safer for those automatically created model objects.
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

        repo_function = api_config.get(
            "repo_key_function"
        )

        if repo_function:

            source = remove_keyword_argument_from_calls(
                source,
                repo_function,
                "filters",
            )

    return source


# =============================================================================
# ANY IMPORT
# =============================================================================

def ensure_any_import(
    source: str,
) -> str:
    """
    Add ANY when generated tests use unittest.mock.ANY.
    """

    if "ANY" not in source:
        return source

    # Already imported
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


# =============================================================================
# HANDLER PATCH FIX
# =============================================================================

def repair_handler_service_patch(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Critical handler-test correction.

    Example:

    WRONG
    -----

    @patch.object(
        po_funding_detail,
        "search_po_funding_detail_v1",
    )
    def test_x(mock_handler):
        response = po_funding_detail.search_po_funding_detail_v1(...)

    This patches the handler itself, so calling the handler returns MagicMock.


    CORRECT
    -------

    @patch.object(
        po_funding_detail,
        "search_po_funding_detail",
    )
    def test_x(mock_search_service):
        response = po_funding_detail.search_po_funding_detail_v1(...)

    The real handler executes while its dependency is mocked.
    """

    module_name = api_config["module_name"]

    handler_function = api_config.get(
        "handler_search_function"
    )

    service_function = api_config.get(
        "service_search_function"
    )

    if not handler_function:
        return source

    if not service_function:
        return source

    # -------------------------------------------------------------------------
    # Multi-line @patch.object(
    # -------------------------------------------------------------------------

    pattern = rf"""
        (
            @patch\.object
            \(
            [ \t\r\n]*
            {re.escape(module_name)}
            [ \t\r\n]*,
            [ \t\r\n]*
            ["']
        )
        {re.escape(handler_function)}
        (
            ["']
            [ \t\r\n]*
            ,?
            [ \t\r\n]*
            \)
        )
    """

    source = re.sub(
        pattern,
        lambda match: (
            match.group(1)
            + service_function
            + match.group(2)
        ),
        source,
        flags=re.MULTILINE | re.VERBOSE,
    )

    # -------------------------------------------------------------------------
    # Direct decorator variant:
    #
    # @patch.object(po_funding_detail, "search_po_funding_detail_v1")
    # -------------------------------------------------------------------------

    compact_pattern = (
        rf'@patch\.object\(\s*'
        rf'{re.escape(module_name)}\s*,\s*'
        rf'(["\'])'
        rf'{re.escape(handler_function)}'
        rf'\1\s*\)'
    )

    compact_replacement = (
        f'@patch.object('
        f'{module_name}, '
        f'"{service_function}")'
    )

    source = re.sub(
        compact_pattern,
        compact_replacement,
        source,
    )

    return source


# =============================================================================
# HANDLER PATCH ARGUMENT NAME
# =============================================================================

def fix_handler_patch_mock_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Rename misleading handler mock variable to service mock variable.

    Example:

        mock_search_handler

    becomes:

        mock_search_service

    This is cosmetic but makes generated tests much clearer.
    """

    replacements = {
        "mock_search_handler":
            "mock_search_service",

        "mock_handler":
            "mock_search_service",
    }

    return apply_replacements(
        source,
        replacements,
    )


# =============================================================================
# REMOVE NONEXISTENT HANDLER TESTS
# =============================================================================

def remove_nonexistent_handler_tests(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Remove unsupported handler tests.

    Example:
        API has search handler only and no GET/details endpoint.
    """

    # -------------------------------------------------------------------------
    # Remove search tests when disabled
    # -------------------------------------------------------------------------

    if not api_config.get(
        "generate_search_handler_tests",
        True,
    ):

        search_name = api_config.get(
            "handler_search_function"
        )

        if search_name:

            pattern = rf"""
                ^def[ \t]+test_[^\n]+
                \n
                (?:
                    (?!^def[ \t]+test_)
                    .*\n?
                )*
                (?=
                    ^def[ \t]+test_
                    |
                    \Z
                )
            """

            blocks = re.findall(
                pattern,
                source,
                flags=re.MULTILINE | re.VERBOSE,
            )

            for block in blocks:

                if search_name in block:
                    source = source.replace(
                        block,
                        "",
                    )

    # -------------------------------------------------------------------------
    # Remove details tests when no details handler exists
    # -------------------------------------------------------------------------

    if not api_config.get(
        "supports_handler_key_lookup",
        False,
    ):

        # Remove tests whose names explicitly reference details handler
        pattern = r"""
            ^def[ \t]+
            test_[^\n]*
            details
            [^\n]*
            \n
            (?:
                (?!^def[ \t]+test_)
                .*\n?
            )*
            (?=
                ^def[ \t]+test_
                |
                \Z
            )
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
    """
    Apply API-specific explicit replacements after standard substitutions.
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


# =============================================================================
# POST PROCESS: DB
# =============================================================================

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


# =============================================================================
# POST PROCESS: MODEL
# =============================================================================

def post_process_model(
    source: str,
    api_config: Dict[str, Any],
) -> str:

    source = fix_key_parameter(
        source,
        api_config,
    )

    return clean_blank_lines(source)


# =============================================================================
# POST PROCESS: SERVICE
# =============================================================================

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


# =============================================================================
# POST PROCESS: HANDLER
# =============================================================================

def post_process_handler(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Handler processing order matters.

    1. Generic replacements already happened.
    2. Correct key data.
    3. Normalize handler CALL names.
    4. Make sure handler patch points to SERVICE, not handler.
    5. Remove tests for handlers that do not exist.
    """

    source = fix_key_parameter(
        source,
        api_config,
    )

    # Real function that should be CALLED by tests
    source = fix_handler_function_names(
        source,
        api_config,
    )

    # Function that should be PATCHED by tests
    source = repair_handler_service_patch(
        source,
        api_config,
    )

    source = fix_handler_patch_mock_names(
        source,
        api_config,
    )

    source = remove_nonexistent_handler_tests(
        source,
        api_config,
    )

    return clean_blank_lines(source)


# =============================================================================
# RENDER
# =============================================================================

def render_test(
    test_type: str,
    template_source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Render one generated test.
    """

    source = template_source

    # -------------------------------------------------------------------------
    # 1. Standard template naming substitutions
    # -------------------------------------------------------------------------

    source = apply_replacements(
        source,
        build_standard_replacements(
            api_config
        ),
    )

    # -------------------------------------------------------------------------
    # 2. API-specific substitutions
    # -------------------------------------------------------------------------

    source = apply_custom_replacements(
        source,
        api_config,
    )

    # -------------------------------------------------------------------------
    # 3. Type-specific corrections
    # -------------------------------------------------------------------------

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


# =============================================================================
# TEMPLATE VALIDATION
# =============================================================================

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
            f"  {test_type:<8} {path}"
        )

    print()
    print(
        "The generator requires the existing "
        "Project Financial tests."
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
    """
    Return generated test destination path.
    """

    module_name = api_config[
        "module_name"
    ]

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

    # -------------------------------------------------------------------------
    # Existing file
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Read template
    # -------------------------------------------------------------------------

    try:

        template_source = (
            template_path.read_text(
                encoding="utf-8",
            )
        )

    except UnicodeDecodeError:

        template_source = (
            template_path.read_text(
                encoding="utf-8-sig",
            )
        )

    # -------------------------------------------------------------------------
    # Generate source
    # -------------------------------------------------------------------------

    generated_source = render_test(
        test_type,
        template_source,
        api_config,
    )

    # -------------------------------------------------------------------------
    # Dry run
    # -------------------------------------------------------------------------

    if dry_run:

        print(
            f"DRY    [{test_type:<7}] "
            f"{destination}"
        )

        return True

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

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
    print("=" * 78)
    print(
        f"Generating tests for API: {api_name}"
    )

    print(
        "Service search: "
        f"{api_config['service_search_function']}"
    )

    print(
        "Handler search: "
        f"{api_config['handler_search_function']}"
    )

    print(
        "Key column: "
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
    """
    Display configured APIs.
    """

    print()
    print("Configured APIs")
    print("=" * 100)

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
            f"service={config['service_search_function']:<35} "
            f"handler={config['handler_search_function']}"
        )

    print()


# =============================================================================
# ARGUMENTS
# =============================================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests from "
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


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
