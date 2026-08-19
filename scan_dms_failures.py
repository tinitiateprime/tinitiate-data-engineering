# ============================================================
# generate_api_tests.py
#
# Generic API unit-test generator.
#
# PURPOSE
# ------------------------------------------------------------
# Uses the working Project Financial unit tests as templates
# and generates:
#
#   1. Repository tests
#   2. Domain/model tests
#   3. Service tests
#   4. Handler tests
#
# API-specific behavior is controlled ONLY by:
#
#       api_test_config.py
#
# Normally, adding another API should require NO changes here.
#
#
# EXAMPLES
# ------------------------------------------------------------
#
# List configured APIs:
#
#   py generate_api_tests.py --list
#
# Dry run:
#
#   py generate_api_tests.py po_funding_detail --dry-run
#
# Generate:
#
#   py generate_api_tests.py po_funding_detail
#
# Regenerate/overwrite:
#
#   py generate_api_tests.py po_funding_detail --force
#
# Generate only one type:
#
#   py generate_api_tests.py po_funding_detail --type service
#
# ============================================================


from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================
# CONFIG
# ============================================================

from api_test_config import (
    APIS,
    TEMPLATE_API,
    TEMPLATE_FILES,
    DESTINATION_DIRS,
    TEST_TYPES,
    validate_config,
)


# ============================================================
# CONSTANTS
# ============================================================

LINE = "=" * 80


# ============================================================
# BASIC HELPERS
# ============================================================


def snake_to_pascal(value: str) -> str:
    """
    Convert:

        po_funding_detail

    to:

        PoFundingDetail
    """

    return "".join(
        word.capitalize()
        for word in value.split("_")
        if word
    )


def snake_to_kebab(value: str) -> str:
    """
    Convert:

        po_funding_detail

    to:

        po-funding-detail
    """

    return value.replace("_", "-")


def unique_preserve_order(values: List[str]) -> List[str]:
    """
    Remove duplicates without changing order.
    """

    seen = set()
    output = []

    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)

    return output


def normalize_newlines(text: str) -> str:
    """
    Normalize line endings.
    """

    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path: Path) -> str:
    """
    Read UTF-8 source file.
    """

    return normalize_newlines(
        path.read_text(encoding="utf-8")
    )


def write_text(
    path: Path,
    content: str,
    dry_run: bool = False,
) -> None:
    """
    Write generated source code.
    """

    if dry_run:
        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content.rstrip() + "\n",
        encoding="utf-8",
    )


# ============================================================
# CONFIG VALIDATION
# ============================================================


def validate_generator_config() -> None:
    """
    Validate global configuration before generation.
    """

    validate_config()

    errors = []

    for test_type in TEST_TYPES:

        if test_type not in TEMPLATE_FILES:
            errors.append(
                f"Missing TEMPLATE_FILES['{test_type}']"
            )

        if test_type not in DESTINATION_DIRS:
            errors.append(
                f"Missing DESTINATION_DIRS['{test_type}']"
            )

    for test_type, template_path in TEMPLATE_FILES.items():

        if not template_path.exists():
            errors.append(
                f"Template does not exist: "
                f"{test_type}: {template_path}"
            )

    if errors:

        print("ERROR: Generator configuration invalid.")
        print()

        for error in errors:
            print(f" - {error}")

        raise SystemExit(1)


# ============================================================
# API CONFIG
# ============================================================


def get_api(api_name: str) -> Dict:
    """
    Return one API configuration.
    """

    if api_name not in APIS:

        print()
        print(f"ERROR: Unknown API: {api_name}")
        print()

        if APIS:
            print("Configured APIs:")

            for name in APIS:
                print(f"  - {name}")

        raise SystemExit(1)

    return APIS[api_name]


# ============================================================
# NAMING
# ============================================================


def destination_filename(
    test_type: str,
    api_config: Dict,
) -> str:
    """
    Determine generated test filename.
    """

    module_name = api_config["module_name"]

    if test_type == "db":
        return f"test_{module_name}_repo.py"

    if test_type == "model":
        return f"test_{module_name}.py"

    if test_type == "service":
        return f"test_{module_name}_service.py"

    if test_type == "handler":
        return f"test_{module_name}.py"

    raise ValueError(
        f"Unsupported test type: {test_type}"
    )


def destination_path(
    test_type: str,
    api_config: Dict,
) -> Path:
    """
    Determine output path.
    """

    return (
        DESTINATION_DIRS[test_type]
        / destination_filename(
            test_type,
            api_config,
        )
    )


# ============================================================
# AUTOMATIC REPLACEMENTS
# ============================================================


def build_automatic_replacements(
    api_config: Dict,
) -> Dict[str, str]:
    """
    Build generic Project Financial -> target API mappings.

    Explicit config replacements are applied afterward.
    """

    source_module = TEMPLATE_API.get(
        "module_name",
        "project_financial",
    )

    target_module = api_config["module_name"]

    source_pascal = snake_to_pascal(
        source_module
    )

    target_pascal = snake_to_pascal(
        target_module
    )

    source_plural = TEMPLATE_API.get(
        "plural_name",
        "project_financials",
    )

    target_plural = api_config.get(
        "plural_name",
        target_module,
    )

    source_route = TEMPLATE_API.get(
        "route_name",
        "project-financials",
    )

    target_route = api_config.get(
        "route_name",
        snake_to_kebab(target_module),
    )

    source_view = TEMPLATE_API.get(
        "source_view",
        "project_financial_vw",
    )

    target_view = api_config.get(
        "source_view",
        f"{target_module}_vw",
    )

    source_key = TEMPLATE_API.get(
        "key_column",
        "project_id",
    )

    target_key = api_config.get(
        "key_column",
        source_key,
    )

    replacements = {

        # ----------------------------------------------------
        # PascalCase model/class names
        # ----------------------------------------------------

        f"{source_pascal}SearchServiceResponse":
            api_config.get(
                "search_response_model",
                f"{target_pascal}SearchServiceResponse",
            ),

        f"{source_pascal}Response":
            api_config.get(
                "response_model",
                f"{target_pascal}Response",
            ),

        source_pascal:
            target_pascal,


        # ----------------------------------------------------
        # Repository modules
        # ----------------------------------------------------

        f"{source_module}_repo":
            api_config.get(
                "repo_module",
                f"{target_module}_repo",
            ),


        # ----------------------------------------------------
        # Service modules
        # ----------------------------------------------------

        f"{source_module}_service":
            api_config.get(
                "service_module",
                f"{target_module}_service",
            ),


        # ----------------------------------------------------
        # Python module
        # ----------------------------------------------------

        source_module:
            target_module,


        # ----------------------------------------------------
        # Plural Python name
        # ----------------------------------------------------

        source_plural:
            target_plural,


        # ----------------------------------------------------
        # Routes
        # ----------------------------------------------------

        source_route:
            target_route,


        # ----------------------------------------------------
        # DB view
        # ----------------------------------------------------

        source_view:
            target_view,


        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------

        source_key:
            target_key,
    }

    return replacements


def build_function_replacements(
    api_config: Dict,
) -> Dict[str, str]:
    """
    Build function-level replacements.
    """

    replacements = {}

    pairs = [

        (
            TEMPLATE_API.get(
                "repo_search_function"
            ),
            api_config.get(
                "repo_search_function"
            ),
        ),

        (
            TEMPLATE_API.get(
                "repo_key_function"
            ),
            api_config.get(
                "repo_key_function"
            ),
        ),

        (
            TEMPLATE_API.get(
                "service_search_function"
            ),
            api_config.get(
                "service_search_function"
            ),
        ),

        (
            TEMPLATE_API.get(
                "service_key_function"
            ),
            api_config.get(
                "service_key_function"
            ),
        ),

        (
            TEMPLATE_API.get(
                "handler_search_function"
            ),
            api_config.get(
                "handler_search_function"
            ),
        ),

        (
            TEMPLATE_API.get(
                "handler_key_function"
            ),
            api_config.get(
                "handler_key_function"
            ),
        ),
    ]

    for source, target in pairs:

        if source and target:
            replacements[source] = target

    return replacements


def get_all_replacements(
    api_config: Dict,
) -> Dict[str, str]:
    """
    Combine automatic + function + explicit replacements.

    Explicit replacements win.
    """

    replacements = {}

    replacements.update(
        build_automatic_replacements(
            api_config
        )
    )

    replacements.update(
        build_function_replacements(
            api_config
        )
    )

    replacements.update(
        api_config.get(
            "replacements",
            {},
        )
    )

    return replacements


# ============================================================
# SAFE TEXT REPLACEMENT
# ============================================================


def apply_replacements(
    text: str,
    replacements: Dict[str, str],
) -> str:
    """
    Apply longest replacements first.

    This prevents:

        project_financial

    from being replaced before:

        get_project_financial_by_project_id
    """

    ordered = sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for source, target in ordered:

        if not source:
            continue

        if target is None:
            continue

        text = text.replace(
            source,
            str(target),
        )

    return text


# ============================================================
# AST TEST-FUNCTION UTILITIES
# ============================================================


def get_function_ranges(
    source: str,
) -> List[Tuple[str, int, int]]:
    """
    Return:

        [
            (function_name, start_line, end_line),
            ...
        ]

    for top-level test functions.

    Lines are zero-based indexes.
    """

    try:
        tree = ast.parse(source)

    except SyntaxError:
        return []

    result = []

    for node in tree.body:

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if not node.name.startswith(
            "test_"
        ):
            continue

        start = node.lineno - 1

        end = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        result.append(
            (
                node.name,
                start,
                end,
            )
        )

    return result


def remove_test_functions_containing(
    source: str,
    markers: List[str],
) -> str:
    """
    Remove test functions whose function body/name
    contains one of the supplied strings.
    """

    if not markers:
        return source

    lines = source.splitlines()

    ranges = get_function_ranges(
        source
    )

    remove_lines = set()

    for function_name, start, end in ranges:

        function_text = "\n".join(
            lines[start:end]
        )

        if any(
            marker
            and marker in function_text
            for marker in markers
        ):

            for index in range(
                start,
                end,
            ):
                remove_lines.add(index)

    output = []

    for index, line in enumerate(lines):

        if index not in remove_lines:
            output.append(line)

    return "\n".join(output)


# ============================================================
# UNSUPPORTED HANDLER TEST REMOVAL
# ============================================================


def clean_handler_tests(
    source: str,
    api_config: Dict,
) -> str:
    """
    Remove details/key handler tests when the API does not
    expose a separate details handler.

    This directly addresses the earlier failure:

        module v1.handlers.po_funding_detail
        has no attribute get_po_funding_detail_details
    """

    supports_key = api_config.get(
        "supports_handler_key_lookup",
        True,
    )

    if supports_key:
        return source

    markers = []

    template_handler_key = TEMPLATE_API.get(
        "handler_key_function"
    )

    generated_handler_key = api_config.get(
        "handler_key_function"
    )

    if template_handler_key:
        markers.append(
            template_handler_key
        )

    if generated_handler_key:
        markers.append(
            generated_handler_key
        )

    # Generic markers because templates may already have
    # gone through replacements.
    markers.extend(
        [
            "_details_handler",
            "_handler_exists",
            "details_handler_exists",
        ]
    )

    return remove_test_functions_containing(
        source,
        markers,
    )


# ============================================================
# REMOVE INVALID DIRECT ARGUMENTS
# ============================================================


def remove_keyword_argument_from_calls(
    source: str,
    function_name: str,
    argument_name: str,
) -> str:
    """
    Remove a named keyword argument from calls to a function.

    Example:

        get_po_funding_detail_by_project(
            project_id="P-1001",
            filters=None,
        )

    becomes:

        get_po_funding_detail_by_project(
            project_id="P-1001",
        )

    This is intentionally text-based because we want to
    preserve the original test formatting.
    """

    if not function_name:
        return source

    pattern = re.compile(
        rf"""
        (
            \b{re.escape(function_name)}
            \s*
            \(
        )
        """,
        re.VERBOSE,
    )

    positions = list(
        pattern.finditer(source)
    )

    if not positions:
        return source

    output = source

    # Process backwards so indexes remain valid.
    for match in reversed(positions):

        open_paren = output.find(
            "(",
            match.start(),
        )

        if open_paren < 0:
            continue

        depth = 0
        end_paren = None

        for index in range(
            open_paren,
            len(output),
        ):

            char = output[index]

            if char == "(":
                depth += 1

            elif char == ")":
                depth -= 1

                if depth == 0:
                    end_paren = index
                    break

        if end_paren is None:
            continue

        call_text = output[
            match.start():
            end_paren + 1
        ]

        keyword_pattern = re.compile(
            rf"""
            (?mx)
            ^
            (?P<indent>\s*)
            {re.escape(argument_name)}
            \s*=\s*
            .*
            ,?
            \s*$
            """,
            re.VERBOSE,
        )

        cleaned = keyword_pattern.sub(
            "",
            call_text,
        )

        output = (
            output[:match.start()]
            + cleaned
            + output[end_paren + 1:]
        )

    return output


# ============================================================
# SERVICE KEY LOOKUP SIGNATURE CLEANUP
# ============================================================


def clean_service_key_calls(
    source: str,
    api_config: Dict,
) -> str:
    """
    Ensure generated tests only call the service key lookup
    using parameters actually supported by that service.

    Example for PO Funding Detail:

        allowed:
            project_id
            page
            sort
            columns

        NOT allowed:
            filters
            limit
            cursor
    """

    function_name = api_config.get(
        "service_key_function"
    )

    allowed = set(
        api_config.get(
            "service_key_parameters",
            [],
        )
    )

    if not function_name:
        return source

    possible_arguments = [
        "filters",
        "page",
        "sort",
        "columns",
        "limit",
        "cursor",
        "offset",
    ]

    for argument in possible_arguments:

        if argument not in allowed:

            source = (
                remove_keyword_argument_from_calls(
                    source,
                    function_name,
                    argument,
                )
            )

    return source


# ============================================================
# REPOSITORY KEY LOOKUP CLEANUP
# ============================================================


def clean_repo_key_calls(
    source: str,
    api_config: Dict,
) -> str:
    """
    Ensure generated repository tests only use supported
    key lookup parameters.
    """

    function_name = api_config.get(
        "repo_key_function"
    )

    allowed = set(
        api_config.get(
            "repo_key_parameters",
            [],
        )
    )

    if not function_name:
        return source

    possible_arguments = [
        "filters",
        "page",
        "sort",
        "columns",
        "limit",
        "cursor",
        "offset",
    ]

    for argument in possible_arguments:

        if argument not in allowed:

            source = (
                remove_keyword_argument_from_calls(
                    source,
                    function_name,
                    argument,
                )
            )

    return source


# ============================================================
# DEFAULT PAGINATION / SORT ASSERTION FIXES
# ============================================================


def fix_default_page_assertions(
    source: str,
    api_config: Dict,
) -> str:
    """
    Generated service tests must match what the service
    REALLY sends to the repository.

    Service behavior:

        current_page =
            page or PaginationModel(
                limit=settings.DEFAULT_PAGE_SIZE
            )

    Therefore a test must NOT expect page=None when calling
    the service without a page.
    """

    default_limit = api_config.get(
        "default_page_size",
        100,
    )

    # Only change common mock expectation syntax.
    source = re.sub(
        r"\bpage\s*=\s*None\s*,",
        (
            "page=PaginationModel("
            f"limit={default_limit}"
            "),"
        ),
        source,
    )

    return source


def fix_default_sort_assertions(
    source: str,
    api_config: Dict,
) -> str:
    """
    Service behavior:

        current_sort =
            sort or SortModel(
                field="order_date",
                order="desc"
            )

    Therefore tests should expect that default object rather
    than sort=None.
    """

    field = api_config.get(
        "default_sort_field",
        "order_date",
    )

    order = api_config.get(
        "default_sort_order",
        "desc",
    )

    source = re.sub(
        r"\bsort\s*=\s*None\s*,",
        (
            "sort=SortModel("
            f'field="{field}", '
            f'order="{order}"'
            "),"
        ),
        source,
    )

    return source


# ============================================================
# IMPORT FIXES
# ============================================================


def ensure_import(
    source: str,
    import_line: str,
    symbol: str,
) -> str:
    """
    Add an import only if the generated test references the
    symbol and does not already import it.
    """

    if symbol not in source:
        return source

    if import_line in source:
        return source

    lines = source.splitlines()

    insert_at = 0

    # Keep module docstring first.
    if lines:

        if lines[0].startswith(
            ('"""', "'''")
        ):

            quote = lines[0][:3]

            if lines[0].count(quote) >= 2:
                insert_at = 1

            else:

                for index in range(
                    1,
                    len(lines),
                ):

                    if quote in lines[index]:
                        insert_at = index + 1
                        break

    # Insert after __future__ imports if present.
    for index, line in enumerate(lines):

        if line.startswith(
            "from __future__"
        ):
            insert_at = index + 1

    lines.insert(
        insert_at,
        import_line,
    )

    return "\n".join(lines)


def ensure_common_test_imports(
    source: str,
) -> str:
    """
    Add imports required by generated/default assertions.
    """

    source = ensure_import(
        source,
        "from core.filters import FiltersEnvelope, SortModel",
        "SortModel",
    )

    source = ensure_import(
        source,
        "from core.pagination import PaginationModel",
        "PaginationModel",
    )

    return source


# ============================================================
# SEARCH FILTER NORMALIZATION TEST FIX
# ============================================================


def fix_none_filter_expectations(
    source: str,
) -> str:
    """
    The actual service code shown by the user does:

        current_filters = (
            FiltersEnvelope(filters=filters)
            if isinstance(filters, dict)
            else filters
        )

    Therefore:

        filters=None

    remains:

        None

    It is NOT converted into FiltersEnvelope.

    Earlier generated tests incorrectly asserted that None
    becomes FiltersEnvelope.

    Remove that incorrect assertion.
    """

    source = re.sub(
        r"""
        (?mx)
        ^\s*
        assert\s+
        isinstance
        \(
            kwargs
            \[
                ["']filters["']
            \]
            \s*,
            \s*FiltersEnvelope
        \)
        \s*$
        """,
        "",
        source,
    )

    return source


# ============================================================
# ROUTE REPLACEMENTS
# ============================================================


def replace_api_routes(
    source: str,
    api_config: Dict,
) -> str:
    """
    Replace Project Financial routes in handler tests.
    """

    route = api_config.get(
        "route_name",
        snake_to_kebab(
            api_config["module_name"]
        ),
    )

    route = route.strip("/")

    route_variants = [
        "/v1/project-financials",
        "/v1/project-financial",
        "/project-financials",
        "/project-financial",
    ]

    target = f"/v1/{route}"

    for old in route_variants:
        source = source.replace(
            old,
            target,
        )

    return source


# ============================================================
# HANDLER FUNCTION VERIFICATION
# ============================================================


def clean_handler_function_names(
    source: str,
    api_config: Dict,
) -> str:
    """
    Ensure handler tests use the configured search handler.
    """

    target = api_config.get(
        "handler_search_function"
    )

    if not target:
        return source

    common_old_names = [

        "search_project_financials_v1",
        "search_project_financial_v1",

        # Earlier broken PO generation:
        "search_po_funding_details_v1",
        "search_po_funding_details",
    ]

    for old in common_old_names:

        source = source.replace(
            old,
            target,
        )

    return source


# ============================================================
# SAMPLE KEY / FIELD / VALUE
# ============================================================


def replace_sample_values(
    source: str,
    api_config: Dict,
) -> str:
    """
    Replace common Project Financial fixture values.
    """

    sample_key = str(
        api_config.get(
            "sample_key",
            "P-1001",
        )
    )

    sample_field = api_config.get(
        "sample_field"
    )

    sample_value = api_config.get(
        "sample_value"
    )

    replacements = {

        "P-1001":
            sample_key,

        "Test Customer":
            str(
                sample_value
                or "Test Value"
            ),
    }

    if sample_field:

        replacements[
            "cust_name"
        ] = sample_field

        replacements[
            "customer_name"
        ] = sample_field

    return apply_replacements(
        source,
        replacements,
    )


# ============================================================
# REMOVE DOUBLE / BROKEN REPLACEMENTS
# ============================================================


def cleanup_generated_names(
    source: str,
    api_config: Dict,
) -> str:
    """
    Handle common artifacts from template replacement.
    """

    module = api_config["module_name"]

    source = source.replace(
        f"{module}s",
        api_config.get(
            "plural_name",
            module,
        ),
    )

    # Avoid accidental:
    #
    # po_funding_detail_detail
    #
    source = source.replace(
        "po_funding_detail_detail",
        "po_funding_detail",
    )

    source = source.replace(
        "PoFundingDetailDetail",
        "PoFundingDetail",
    )

    return source


# ============================================================
# TYPE-SPECIFIC POST PROCESSING
# ============================================================


def post_process_db(
    source: str,
    api_config: Dict,
) -> str:

    source = clean_repo_key_calls(
        source,
        api_config,
    )

    source = fix_default_page_assertions(
        source,
        api_config,
    )

    source = fix_default_sort_assertions(
        source,
        api_config,
    )

    source = ensure_common_test_imports(
        source
    )

    return source


def post_process_model(
    source: str,
    api_config: Dict,
) -> str:

    # Model tests generally do not need API call-signature
    # mutation. Keep template behavior.
    return source


def post_process_service(
    source: str,
    api_config: Dict,
) -> str:

    source = clean_service_key_calls(
        source,
        api_config,
    )

    source = fix_none_filter_expectations(
        source
    )

    source = fix_default_page_assertions(
        source,
        api_config,
    )

    source = fix_default_sort_assertions(
        source,
        api_config,
    )

    source = ensure_common_test_imports(
        source
    )

    return source


def post_process_handler(
    source: str,
    api_config: Dict,
) -> str:

    source = clean_handler_tests(
        source,
        api_config,
    )

    source = clean_handler_function_names(
        source,
        api_config,
    )

    source = replace_api_routes(
        source,
        api_config,
    )

    return source


# ============================================================
# MASTER RENDER
# ============================================================


def render_test(
    test_type: str,
    api_config: Dict,
) -> str:
    """
    Render one generated test file.
    """

    template_path = TEMPLATE_FILES[
        test_type
    ]

    source = read_text(
        template_path
    )

    # --------------------------------------------------------
    # 1. Automatic naming replacements
    # --------------------------------------------------------

    source = apply_replacements(
        source,
        get_all_replacements(
            api_config
        ),
    )

    # --------------------------------------------------------
    # 2. Fixture/sample replacements
    # --------------------------------------------------------

    source = replace_sample_values(
        source,
        api_config,
    )

    # --------------------------------------------------------
    # 3. Clean names
    # --------------------------------------------------------

    source = cleanup_generated_names(
        source,
        api_config,
    )

    # --------------------------------------------------------
    # 4. Type-specific behavior
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

    # --------------------------------------------------------
    # 5. Final import check
    # --------------------------------------------------------

    source = ensure_common_test_imports(
        source
    )

    # --------------------------------------------------------
    # 6. Normalize excessive blank lines
    # --------------------------------------------------------

    source = re.sub(
        r"\n{4,}",
        "\n\n\n",
        source,
    )

    return source.rstrip() + "\n"


# ============================================================
# PYTHON VALIDATION
# ============================================================


def validate_generated_python(
    source: str,
    destination: Path,
) -> None:
    """
    Make sure generated code is syntactically valid before
    writing it.
    """

    try:

        ast.parse(
            source,
            filename=str(destination),
        )

    except SyntaxError as exc:

        print()
        print("ERROR: Generated Python is invalid.")
        print(f"File: {destination}")
        print(
            f"Line: {exc.lineno}, "
            f"Column: {exc.offset}"
        )
        print(f"Message: {exc.msg}")
        print()

        if exc.text:
            print(exc.text.rstrip())

        raise SystemExit(1)


# ============================================================
# GENERATE ONE TEST TYPE
# ============================================================


def generate_one(
    test_type: str,
    api_config: Dict,
    *,
    force: bool,
    dry_run: bool,
) -> Tuple[bool, bool]:
    """
    Generate one test file.

    Returns:

        generated, skipped
    """

    destination = destination_path(
        test_type,
        api_config,
    )

    if destination.exists() and not force:

        print(
            f"SKIP   "
            f"[{test_type:<7}] "
            f"{destination}"
        )

        return False, True

    source = render_test(
        test_type,
        api_config,
    )

    validate_generated_python(
        source,
        destination,
    )

    action = (
        "DRY"
        if dry_run
        else (
            "REPLACE"
            if destination.exists()
            else "CREATE"
        )
    )

    print(
        f"{action:<7}"
        f"[{test_type:<7}] "
        f"{destination}"
    )

    write_text(
        destination,
        source,
        dry_run=dry_run,
    )

    return True, False


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
    Generate all configured test files for one API.
    """

    api_config = get_api(
        api_name
    )

    key_column = api_config.get(
        "key_column"
    )

    lookup_function = api_config.get(
        "repo_key_function"
    )

    print()
    print(LINE)
    print(
        f"Generating tests for API: "
        f"{api_name}"
    )
    print(
        f"Key column: "
        f"{key_column}"
    )
    print(
        f"Lookup function: "
        f"{lookup_function}"
    )
    print(LINE)

    if selected_type:

        test_types = [
            selected_type
        ]

    else:

        test_types = list(
            TEST_TYPES
        )

    generated = 0
    skipped = 0

    for test_type in test_types:

        was_generated, was_skipped = (
            generate_one(
                test_type,
                api_config,
                force=force,
                dry_run=dry_run,
            )
        )

        if was_generated:
            generated += 1

        if was_skipped:
            skipped += 1

    print()
    print(f"Generated: {generated}")
    print(f"Skipped:   {skipped}")
    print()


# ============================================================
# LIST APIs
# ============================================================


def list_apis() -> None:
    """
    Display configured APIs.
    """

    print()
    print("Configured APIs")
    print(LINE)

    if not APIS:

        print("No APIs configured.")
        print()
        return

    for name, config in APIS.items():

        key = config.get(
            "key_column",
            "?"
        )

        lookup = config.get(
            "repo_key_function",
            "?"
        )

        print(
            f"{name:<30} "
            f"key={key:<20} "
            f"lookup={lookup}"
        )

    print()


# ============================================================
# SHOW PATHS
# ============================================================


def show_paths() -> None:

    print()
    print("Template files")
    print(LINE)

    for test_type in TEST_TYPES:

        path = TEMPLATE_FILES[
            test_type
        ]

        print(
            f"{test_type:<10}"
            f"{path} "
            f"exists={path.exists()}"
        )

    print()
    print("Destination directories")
    print(LINE)

    for test_type in TEST_TYPES:

        print(
            f"{test_type:<10}"
            f"{DESTINATION_DIRS[test_type]}"
        )

    print()


# ============================================================
# CLI
# ============================================================


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests from the "
            "Project Financial working templates."
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
        "--paths",
        action="store_true",
        help="Show template and destination paths.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing generated test files."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show what would be generated without "
            "writing files."
        ),
    )

    parser.add_argument(
        "--type",
        choices=list(TEST_TYPES),
        dest="test_type",
        help=(
            "Generate only one test type: "
            "db, model, service, or handler."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    args = parse_args()

    # --------------------------------------------------------
    # Validate global configuration
    # --------------------------------------------------------

    validate_generator_config()

    # --------------------------------------------------------
    # List configured APIs
    # --------------------------------------------------------

    if args.list:

        list_apis()
        return

    # --------------------------------------------------------
    # Show paths
    # --------------------------------------------------------

    if args.paths:

        show_paths()
        return

    # --------------------------------------------------------
    # API name required for generation
    # --------------------------------------------------------

    if not args.api:

        print()
        print(
            "ERROR: Please provide an API name."
        )
        print()
        print("Example:")
        print(
            "  py generate_api_tests.py "
            "po_funding_detail"
        )
        print()
        print("Available APIs:")

        for name in APIS:
            print(f"  - {name}")

        print()

        raise SystemExit(1)

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

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
