"""
generate_api_tests.py

Generic unit-test generator for the MT-DM API project.

The generator uses the existing Project Financial tests as templates and
creates DB/repository, model, service, and handler tests for APIs defined in
api_test_config.py.

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

    py generate_api_tests.py po_funding_detail --test-type handler --force
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

try:
    from api_test_config import (
        APIS,
        DESTINATION_DIRS,
        TEMPLATE_FILES,
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
    """po_funding_detail -> PoFundingDetail"""
    return "".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def snake_to_title(value: str) -> str:
    """po_funding_detail -> Po Funding Detail"""
    return " ".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def normalize_path(value: Any) -> Path:
    """Convert a configured path to pathlib.Path."""
    if isinstance(value, Path):
        return value
    return Path(str(value))


def get_config_value(
    api_config: Dict[str, Any],
    name: str,
    default: Any = None,
) -> Any:
    """Safely retrieve one API configuration value."""
    value = api_config.get(name)
    return default if value is None else value


def first_config_value(
    api_config: Dict[str, Any],
    *names: str,
    default: Any = None,
) -> Any:
    """Return the first non-None configured value from a list of names."""
    for name in names:
        if name in api_config and api_config[name] is not None:
            return api_config[name]
    return default


def clean_blank_lines(source: str) -> str:
    """Avoid very large runs of blank lines after substitutions."""
    source = re.sub(r"\n[ \t]+\n", "\n\n", source)
    source = re.sub(r"\n{4,}", "\n\n\n", source)
    return source


def unique_nonempty(values: Iterable[Optional[str]]) -> list[str]:
    """Return unique non-empty strings while preserving order."""
    output: list[str] = []
    seen: set[str] = set()

    for value in values:
        if not value:
            continue

        text = str(value)

        if text in seen:
            continue

        seen.add(text)
        output.append(text)

    return output


# =============================================================================
# API CONFIG
# =============================================================================


def prepare_api_config(
    api_name: str,
    raw_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a normalized API configuration.

    api_test_config.py can use the explicit keys already present in your
    project, while this function derives safe defaults for missing values.
    """

    config = dict(raw_config)

    module_name = first_config_value(
        config,
        "module_name",
        default=api_name,
    )

    plural_name = first_config_value(
        config,
        "plural_name",
        default=module_name,
    )

    route_name = first_config_value(
        config,
        "route_name",
        default=module_name.replace("_", "-"),
    )

    pascal_name = first_config_value(
        config,
        "pascal_name",
        default=snake_to_pascal(module_name),
    )

    display_name = first_config_value(
        config,
        "display_name",
        default=snake_to_title(module_name),
    )

    key_column = first_config_value(
        config,
        "key_column",
        "key_field",
        default="project_id",
    )

    key_param = first_config_value(
        config,
        "key_param",
        "key_argument",
        default=key_column,
    )

    sample_key = str(
        first_config_value(
            config,
            "sample_key",
            default="P-1001",
        )
    )

    source_view = first_config_value(
        config,
        "source_view",
        "view_name",
        default=f"{module_name}_vw",
    )

    repo_search_function = first_config_value(
        config,
        "repo_search_function",
        "search_repo_function",
        default=f"get_{module_name}",
    )

    repo_key_function = first_config_value(
        config,
        "repo_key_function",
        "lookup_function",
        "repo_lookup_function",
        default=f"get_{module_name}_by_{key_param}",
    )

    service_search_function = first_config_value(
        config,
        "service_search_function",
        "search_function",
        default=f"search_{plural_name}",
    )

    service_key_function = first_config_value(
        config,
        "service_key_function",
        "details_function",
        "service_lookup_function",
        default=f"get_{module_name}_by_{key_param}",
    )

    # IMPORTANT:
    # This is already the final handler function name.  Never append "_v1"
    # to an explicitly configured function name.
    handler_search_function = first_config_value(
        config,
        "handler_search_function",
        default=f"search_{plural_name}_v1",
    )

    handler_details_function = first_config_value(
        config,
        "handler_details_function",
        "handler_key_function",
        default=None,
    )

    response_model = first_config_value(
        config,
        "response_model",
        default=f"{pascal_name}Response",
    )

    search_response_model = first_config_value(
        config,
        "search_response_model",
        default=f"{pascal_name}SearchServiceResponse",
    )

    supports_search = bool(
        first_config_value(
            config,
            "supports_search",
            default=True,
        )
    )

    supports_key_lookup = bool(
        first_config_value(
            config,
            "supports_key_lookup",
            default=True,
        )
    )

    supports_filters = bool(
        first_config_value(
            config,
            "supports_filters",
            default=True,
        )
    )

    supports_sort = bool(
        first_config_value(
            config,
            "supports_sort",
            default=True,
        )
    )

    supports_pagination = bool(
        first_config_value(
            config,
            "supports_pagination",
            default=True,
        )
    )

    supports_columns = bool(
        first_config_value(
            config,
            "supports_columns",
            default=True,
        )
    )

    supports_handler_key_lookup = bool(
        first_config_value(
            config,
            "supports_handler_key_lookup",
            default=bool(handler_details_function),
        )
    )

    uses_pagination_model = bool(
        first_config_value(
            config,
            "uses_pagination_model",
            default=True,
        )
    )

    lookup_supports_filters = bool(
        first_config_value(
            config,
            "lookup_supports_filters",
            default=False,
        )
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
            "repo_search_function": repo_search_function,
            "repo_key_function": repo_key_function,
            "service_search_function": service_search_function,
            "service_key_function": service_key_function,
            "handler_search_function": handler_search_function,
            "handler_details_function": handler_details_function,
            "response_model": response_model,
            "search_response_model": search_response_model,
            "supports_search": supports_search,
            "supports_key_lookup": supports_key_lookup,
            "supports_filters": supports_filters,
            "supports_sort": supports_sort,
            "supports_pagination": supports_pagination,
            "supports_columns": supports_columns,
            "supports_handler_key_lookup": supports_handler_key_lookup,
            "uses_pagination_model": uses_pagination_model,
            "lookup_supports_filters": lookup_supports_filters,
        }
    )

    return config


# =============================================================================
# TEMPLATE REPLACEMENTS
# =============================================================================


def build_standard_replacements(
    api_config: Dict[str, Any],
) -> Dict[str, str]:
    """
    Standard Project Financial -> target API replacements.

    Longer strings are applied first in apply_replacements().
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

        # kebab-case
        "project-financials": route_name,
        "project-financial": route_name,

        # uppercase
        "PROJECT_FINANCIALS": plural_name.upper(),
        "PROJECT_FINANCIAL": module_name.upper(),

        # display/readable
        "Project Financials": display_name + "s",
        "Project Financial": display_name,

        # source
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
    does not alter part of:
        project_financials
    before the plural replacement is evaluated.
    """

    normalized: Dict[str, str] = {}

    for old, new in replacements.items():
        if old is None or new is None:
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
# FUNCTION NAME REPLACEMENTS
# =============================================================================


def replace_candidates(
    source: str,
    candidates: Iterable[Optional[str]],
    target: Optional[str],
) -> str:
    """Replace candidate names with the target, longest first."""
    if not target:
        return source

    candidate_names = unique_nonempty(candidates)

    for candidate in sorted(
        candidate_names,
        key=len,
        reverse=True,
    ):
        if candidate == target:
            continue

        source = source.replace(
            candidate,
            target,
        )

    return source


def fix_repo_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """Normalize repository function names from the template."""

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config["repo_search_function"]
    key_target = api_config["repo_key_function"]

    source = replace_candidates(
        source,
        [
            "get_project_financial",
            "get_project_financials",
            f"get_{module_name}",
            f"get_{plural_name}",
        ],
        search_target,
    )

    source = replace_candidates(
        source,
        [
            "get_project_financial_by_project_id",
            "get_project_financials_by_project_id",
            f"get_{module_name}_by_project_id",
            f"get_{plural_name}_by_project_id",
            f"get_{module_name}_by_{api_config['key_param']}",
            f"get_{plural_name}_by_{api_config['key_param']}",
        ],
        key_target,
    )

    return source


def fix_service_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """Normalize service function names from config."""

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config["service_search_function"]
    key_target = api_config["service_key_function"]

    source = replace_candidates(
        source,
        [
            "search_project_financials",
            "search_project_financial",
            f"search_{plural_name}",
            f"search_{module_name}",
        ],
        search_target,
    )

    source = replace_candidates(
        source,
        [
            "get_project_financial_by_project",
            "get_project_financial_by_project_id",
            f"get_{module_name}_by_project",
            f"get_{plural_name}_by_project",
            f"get_{module_name}_by_{api_config['key_param']}",
            f"get_{plural_name}_by_{api_config['key_param']}",
        ],
        key_target,
    )

    return source


def collapse_repeated_v1(
    source: str,
    target: str,
) -> str:
    """
    Collapse accidental suffix duplication such as:

        search_po_funding_detail_v1_v1
        search_po_funding_detail_v1_v1_v1

    to exactly the configured target.
    """

    if not target:
        return source

    base = re.sub(
        r"(?:_v1)+$",
        "",
        target,
    )

    if target.endswith("_v1"):
        source = re.sub(
            rf"\b{re.escape(base)}(?:_v1)+\b",
            target,
            source,
        )

    return source


def fix_handler_function_names(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize handler function names using exact configured names.

    IMPORTANT:
    handler_search_function is treated as the final function name.
    We never append "_v1" to it.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    search_target = api_config.get(
        "handler_search_function"
    )

    details_target = api_config.get(
        "handler_details_function"
    )

    if search_target:
        search_candidates = [
            # Project Financial template names
            "search_project_financials_v1",
            "search_project_financial_v1",
            "search_project_financials",
            "search_project_financial",

            # Generic names after the initial string substitutions
            f"search_{plural_name}_v1",
            f"search_{module_name}_v1",
            f"search_{plural_name}",
            f"search_{module_name}",

            # Previously generated bad names
            f"search_{plural_name}_v1_v1",
            f"search_{module_name}_v1_v1",
            f"search_{plural_name}_v1_v1_v1",
            f"search_{module_name}_v1_v1_v1",
        ]

        source = replace_candidates(
            source,
            search_candidates,
            search_target,
        )

        source = collapse_repeated_v1(
            source,
            search_target,
        )

    if details_target:
        details_candidates = [
            "get_project_financial_details",
            "get_project_financial_detail",
            f"get_{module_name}_details",
            f"get_{plural_name}_details",
            f"get_{module_name}_detail",
            f"get_{plural_name}_detail",
        ]

        source = replace_candidates(
            source,
            details_candidates,
            details_target,
        )

    return source


# =============================================================================
# HANDLER SERVICE PATCH REPAIR
# =============================================================================


def _replace_patch_object_attribute(
    source: str,
    module_name: str,
    old_attribute: Optional[str],
    new_attribute: Optional[str],
) -> str:
    """
    Replace only the attribute string inside @patch.object(module, "...").

    This intentionally does NOT replace normal function calls. Handler tests
    must call the real handler while mocking the service dependency used by
    that handler.
    """

    if (
        not module_name
        or not old_attribute
        or not new_attribute
        or old_attribute == new_attribute
    ):
        return source

    pattern = re.compile(
        rf"""
        (?P<prefix>
            @patch\.object
            \(
            \s*
            {re.escape(module_name)}
            \s*
            ,
            \s*
        )
        (?P<quote>["'])
        {re.escape(old_attribute)}
        (?P=quote)
        """,
        flags=re.MULTILINE | re.VERBOSE,
    )

    return pattern.sub(
        lambda match: (
            match.group("prefix")
            + match.group("quote")
            + str(new_attribute)
            + match.group("quote")
        ),
        source,
    )


def repair_handler_service_patches(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Ensure handler tests patch SERVICE functions, never the handler itself.

    Example:

        @patch.object(
            po_funding_detail,
            "search_po_funding_detail",
        )
        def test_search_po_funding_detail_v1_success(...):
            response = po_funding_detail.search_po_funding_detail_v1(...)

    The old generator could normalize both names to
    search_po_funding_detail_v1. That makes the handler call return a MagicMock
    instead of executing the real handler.
    """

    module_name = api_config["module_name"]

    handler_search = api_config.get(
        "handler_search_function"
    )
    service_search = api_config.get(
        "service_search_function"
    )

    source = _replace_patch_object_attribute(
        source,
        module_name,
        handler_search,
        service_search,
    )

    handler_details = api_config.get(
        "handler_details_function"
    )
    service_details = api_config.get(
        "service_key_function"
    )

    source = _replace_patch_object_attribute(
        source,
        module_name,
        handler_details,
        service_details,
    )

    return source


def validate_generated_python(
    source: str,
    *,
    test_type: str,
    destination: Optional[Path] = None,
) -> None:
    """
    Validate generated Python before writing it to disk.

    This prevents the generator from overwriting a working test file with
    malformed output.
    """

    try:
        ast.parse(source)
    except SyntaxError as exc:
        lines = source.splitlines()
        line_no = exc.lineno or 0

        start = max(1, line_no - 3)
        end = min(len(lines), line_no + 3)

        location = (
            f" for {destination}"
            if destination is not None
            else ""
        )

        details = [
            "",
            f"ERROR: Generated {test_type} test is invalid Python{location}.",
            (
                f"SyntaxError at line {line_no}, "
                f"column {exc.offset or 0}: {exc.msg}"
            ),
            "",
            "Generated source near the error:",
        ]

        for number in range(start, end + 1):
            pointer = ">>" if number == line_no else "  "
            details.append(
                f"{pointer} {number:4}: {lines[number - 1]}"
            )

        details.append("")

        raise ValueError(
            "\n".join(details)
        ) from exc


# =============================================================================
# KEY COLUMN / PARAMETER
# =============================================================================


def fix_key_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Replace the Project Financial template's key references with the
    API-specific key.
    """

    key_param = api_config["key_param"]
    key_column = api_config["key_column"]
    sample_key = api_config["sample_key"]

    replacements = {
        # Common test values
        '"P-1001"': f'"{sample_key}"',
        "'P-1001'": f"'{sample_key}'",

        # Field names
        '"project_id"': f'"{key_column}"',
        "'project_id'": f"'{key_column}'",

        # Variables
        "expected_project_id": f"expected_{key_param}",
    }

    source = apply_replacements(
        source,
        replacements,
    )

    # Replace parameter-token occurrences conservatively.
    if key_param != "project_id":
        source = re.sub(
            r"\bproject_id\b",
            key_param,
            source,
        )

    return source


# =============================================================================
# NONE FILTER FIX
# =============================================================================


def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    Remove template assertions that require filters=None to be converted
    to a FiltersEnvelope when the target service intentionally keeps None.
    """

    pattern = r"""
        ^[ \t]*
        assert[ \t]+
        isinstance
        \(
            [ \t]*
            kwargs
            \[
                [ \t]*["']filters["'][ \t]*
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
# REMOVE UNSUPPORTED KEYWORD ARGUMENT
# =============================================================================


def find_matching_close_paren(
    text: str,
    open_paren: int,
) -> Optional[int]:
    """
    Find the closing parenthesis matching text[open_paren].

    String literals and escaped quotes are respected.
    """

    depth = 0
    in_single = False
    in_double = False
    escaped = False

    for index in range(
        open_paren,
        len(text),
    ):
        char = text[index]

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
                return index

    return None


def remove_keyword_argument_from_call_text(
    call_text: str,
    argument_name: str,
) -> str:
    """Remove one keyword argument from a function-call text block."""

    # Multiline argument, including optional trailing comma.
    multiline_pattern = rf"""
        ^(?P<indent>[ \t]*)
        {re.escape(argument_name)}
        [ \t]*=
        (?P<value>
            [^\n]*
        )
        ,?
        [ \t]*\n
    """

    cleaned = re.sub(
        multiline_pattern,
        "",
        call_text,
        flags=re.MULTILINE | re.VERBOSE,
    )

    # Also handle a simple one-line keyword argument.
    cleaned = re.sub(
        rf"(?<!\w){re.escape(argument_name)}\s*=\s*[^,\)]+,\s*",
        "",
        cleaned,
    )

    cleaned = re.sub(
        rf",\s*{re.escape(argument_name)}\s*=\s*[^,\)]+",
        "",
        cleaned,
    )

    return cleaned


def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove a keyword argument from calls to a specific function.

    This walks matching function calls and handles nested parentheses rather
    than trying to match an entire call with one huge regex.
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

    # Reverse order keeps prior offsets valid.
    for match in reversed(matches):
        open_paren = output.find(
            "(",
            match.start(),
        )

        if open_paren < 0:
            continue

        end_paren = find_matching_close_paren(
            output,
            open_paren,
        )

        if end_paren is None:
            continue

        call_start = match.start()
        call_text = output[
            call_start:
            end_paren + 1
        ]

        cleaned = remove_keyword_argument_from_call_text(
            call_text,
            argument_name,
        )

        output = (
            output[:call_start]
            + cleaned
            + output[end_paren + 1:]
        )

    return output


# =============================================================================
# REPOSITORY MOCK ASSERTIONS
# =============================================================================


def normalize_repository_mock_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Normalize mock expectations to match the real service behavior.

    The service may instantiate PaginationModel/SortModel before calling the
    repository, so generated tests should not require page=None/sort=None.
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
        lookup_candidates = unique_nonempty(
            [
                api_config.get("repo_key_function"),
                api_config.get("service_key_function"),
            ]
        )

        for function_name in lookup_candidates:
            source = remove_keyword_argument_from_calls(
                source,
                function_name,
                "filters",
            )

    return source


# =============================================================================
# PAGINATION ARGUMENT NORMALIZATION
# =============================================================================


def remove_old_limit_cursor_arguments(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Current APIs use PaginationModel(page=...) rather than standalone
    limit/cursor arguments. Remove legacy standalone args when configured.
    """

    if not api_config.get(
        "uses_pagination_model",
        True,
    ):
        return source

    candidates = unique_nonempty(
        [
            api_config.get("repo_key_function"),
            api_config.get("repo_search_function"),
            api_config.get("service_key_function"),
            api_config.get("service_search_function"),
        ]
    )

    for function_name in candidates:
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
# TEST FUNCTION REMOVAL HELPERS
# =============================================================================


def iter_test_function_blocks(
    source: str,
) -> list[tuple[int, int, str, str]]:
    """
    Return:
        (start_offset, end_offset, test_name, full_block)
    for top-level pytest test functions.
    """

    function_pattern = re.compile(
        r"(?m)^def\s+(test_[A-Za-z0-9_]+)\s*\("
    )

    matches = list(
        function_pattern.finditer(source)
    )

    blocks: list[tuple[int, int, str, str]] = []

    for index, match in enumerate(matches):
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(source)

        blocks.append(
            (
                start,
                end,
                match.group(1),
                source[start:end],
            )
        )

    return blocks


def remove_test_functions_containing(
    source: str,
    text: str,
) -> str:
    """Remove complete top-level tests whose body/name contains text."""

    if not text:
        return source

    blocks = iter_test_function_blocks(
        source
    )

    to_remove: list[tuple[int, int]] = []

    for start, end, _name, block in blocks:
        if text in block:
            to_remove.append(
                (start, end)
            )

    for start, end in reversed(to_remove):
        source = (
            source[:start]
            + source[end:]
        )

    return clean_blank_lines(source)


def remove_test_functions_matching_name(
    source: str,
    patterns: list[str],
) -> str:
    """
    Remove complete top-level tests when the test function name matches one
    of the supplied regular expressions.
    """

    blocks = iter_test_function_blocks(
        source
    )

    to_remove: list[tuple[int, int]] = []

    for start, end, test_name, _block in blocks:
        if any(
            re.fullmatch(
                pattern,
                test_name,
            )
            for pattern in patterns
        ):
            to_remove.append(
                (start, end)
            )

    for start, end in reversed(to_remove):
        source = (
            source[:start]
            + source[end:]
        )

    return clean_blank_lines(source)


def remove_nonexistent_handler_tests(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Remove handler tests for functions/endpoints the target API does not
    actually implement.
    """

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]

    if not api_config.get(
        "supports_search",
        True,
    ):
        search_names = unique_nonempty(
            [
                api_config.get("handler_search_function"),
                "search_project_financials_v1",
                "search_project_financial_v1",
                f"search_{module_name}_v1",
                f"search_{plural_name}_v1",
            ]
        )

        for search_name in search_names:
            source = remove_test_functions_containing(
                source,
                search_name,
            )

    if not api_config.get(
        "supports_handler_key_lookup",
        False,
    ):
        detail_names = unique_nonempty(
            [
                api_config.get("handler_details_function"),
                "get_project_financial_details",
                "get_project_financial_detail",
                f"get_{module_name}_details",
                f"get_{plural_name}_details",
                f"get_{module_name}_detail",
                f"get_{plural_name}_detail",
            ]
        )

        for detail_name in detail_names:
            source = remove_test_functions_containing(
                source,
                detail_name,
            )

        source = remove_test_functions_matching_name(
            source,
            [
                rf"test_get_{re.escape(module_name)}_details_.*",
                rf"test_get_{re.escape(plural_name)}_details_.*",
                rf"test_get_{re.escape(module_name)}_detail_.*",
                rf"test_get_{re.escape(plural_name)}_detail_.*",
            ],
        )

    return clean_blank_lines(source)


# =============================================================================
# IMPORT NORMALIZATION
# =============================================================================


def ensure_any_import(
    source: str,
) -> str:
    """Add ANY when generated service tests use unittest.mock.ANY."""

    if "ANY" not in source:
        return source

    # Already imported on a unittest.mock import line.
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
        current = match.group(1).strip()

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


# =============================================================================
# CUSTOM CONFIG REPLACEMENTS
# =============================================================================


def apply_custom_replacements(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Apply API-specific overrides only after normal generic replacements.

    This allows future APIs to add special differences without modifying
    generator logic.
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
# TEST-TYPE POST PROCESSING
# =============================================================================


def post_process_db(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """Post-process repository/DB tests."""

    source = fix_repo_function_names(
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
    """Post-process domain model tests."""

    source = fix_key_parameter(
        source,
        api_config,
    )

    return clean_blank_lines(source)


def post_process_service(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """Post-process service tests."""

    source = fix_repo_function_names(
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
    """Post-process Lambda handler tests."""

    source = fix_key_parameter(
        source,
        api_config,
    )

    source = fix_handler_function_names(
        source,
        api_config,
    )

    # The handler test must patch the service dependency while still calling
    # the real handler function.
    source = repair_handler_service_patches(
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
    """Render one test file."""

    source = template_source

    # 1. Generic Project Financial -> target replacements.
    source = apply_replacements(
        source,
        build_standard_replacements(
            api_config
        ),
    )

    # 2. API-specific override replacements.
    source = apply_custom_replacements(
        source,
        api_config,
    )

    # 3. Test-type-specific normalization.
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
    """Verify required Project Financial template files exist."""

    missing: list[tuple[str, str]] = []

    types_to_check = (
        [selected_type]
        if selected_type
        else list(TEST_TYPES)
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
    """Return generated test destination."""

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

    validate_generated_python(
        generated_source,
        test_type=test_type,
        destination=destination,
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
    """Generate configured tests for one API."""

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
        "Generating tests for API: "
        f"{api_name}"
    )
    print(
        "Key column: "
        f"{api_config['key_column']}"
    )
    print(
        "Handler search: "
        f"{api_config['handler_search_function']}"
    )
    print(
        "Handler details: "
        f"{api_config.get('handler_details_function')}"
    )
    print("=" * 78)

    generated = 0
    skipped = 0

    types_to_generate = (
        [selected_type]
        if selected_type
        else list(TEST_TYPES)
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
    """Print all configured APIs."""

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
            f"handler={config['handler_search_function']}"
        )

    print()


# =============================================================================
# ARGUMENTS
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""

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


# =============================================================================
# ENTRY POINT
# =============================================================================


if __name__ == "__main__":
    main()
