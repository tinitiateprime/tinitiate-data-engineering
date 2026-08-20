# ============================================================
# api_test_config.py
# Central configuration for API unit-test generation.
# ============================================================

from pathlib import Path

API_ROOT = Path(__file__).resolve().parent
MAIN_FUNCTION_ROOT = API_ROOT / "main-function"
TEST_ROOT = MAIN_FUNCTION_ROOT / "tests" / "unit"
SOURCE_ROOT = MAIN_FUNCTION_ROOT / "mt-dm-lambda-src"

TEMPLATE_FILES = {
    "db": TEST_ROOT / "db" / "test_project_financial_repo.py",
    "model": TEST_ROOT / "domain" / "models" / "test_project_financial.py",
    "service": TEST_ROOT / "domain" / "services" / "test_project_financial_service.py",
    "handler": TEST_ROOT / "v1" / "test_project_financial.py",
}

DESTINATION_DIRS = {
    "db": TEST_ROOT / "db",
    "model": TEST_ROOT / "domain" / "models",
    "service": TEST_ROOT / "domain" / "services",
    "handler": TEST_ROOT / "v1",
}

TEST_TYPES = ("db", "model", "service", "handler")

TEMPLATE_API = {
    "module_name": "project_financial",
    "route_name": "project-financial",
    "singular_name": "project_financial",
    "plural_name": "project_financials",
    "source_schema": "gold",
    "source_view": "project_financial_vw",
    "key_column": "project_id",
    "key_argument": "project_id",
    "sample_key": "P-1001",
    "sample_field": "vendor_name",
    "sample_value": "Test Vendor",
    "repo_module": "project_financial_repo",
    "repo_search_function": "get_project_financial",
    "repo_key_function": "get_project_financial_by_project_id",
    "service_module": "project_financial_service",
    "service_search_function": "search_project_financial",
    "service_key_function": "get_project_financial_by_project",
    "handler_module": "project_financial",
    "handler_search_function": "search_project_financials",
    "handler_key_function": "get_project_financial_details",
    "response_model": "ProjectFinancialResponse",
    "search_response_model": "ProjectFinancialSearchServiceResponse",
    "default_page_size": 100,
    "default_sort_field": "order_date",
    "default_sort_order": "desc",
}

APIS = {

    "agent": {
        "module_name": "agent",
        "route_name": "agent",
        "singular_name": "agent",
        "plural_name": "agent",

        # Agent work-location search is scoped by a REQUIRED contract_id.
        "key_column": "contract_id",
        "key_argument": "contract_id",
        "sample_key": "C-1001",
        "search_requires_key": True,
        "handler_path_parameter": "contract_id",

        "sample_field": "project_name",
        "sample_value": "Test Project",

        "repo_module": "agent_repo",
        "repo_search_function": "get_work_locations_by_contract_id",
        "repo_key_function": None,

        "service_module": "agent_service",
        "service_search_function": "agent_get_contract_locations",
        "service_key_function": None,

        "handler_module": "agent",
        "handler_search_function": "get_agent_contract_locations_v1",
        "handler_key_function": None,
        "handler_details_function": None,

        "response_model": "AgentContractLocationResponse",
        "search_response_model": "AgentContractServiceResponse",
        "response_key_field": "contract_id",
        "response_assert_fields": ["contract_id"],

        "default_page_size": 100,
        "default_sort_field": "contract_id",
        "default_sort_order": "asc",

        "supports_search": True,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,
        "supports_filters": True,
        "supports_sort": True,
        "supports_pagination": True,
        "supports_columns": True,
        "lookup_supports_filters": False,

        # Repository accepts PaginationModel; service/handler accept limit/cursor.
        "repo_pagination_mode": "page",
        "service_pagination_mode": "limit_cursor",
        "uses_pagination_model": False,

        # These lists are the ONLY place where API-specific function shapes live.
        "repo_search_parameters": [
            "contract_id",
            "filters",
            "page",
            "columns",
            "sort",
        ],

        "service_search_parameters": [
            "contract_id",
            "filters",
            "limit",
            "cursor",
            "columns",
            "sort",
        ],

        "handler_service_parameters": [
            "contract_id",
            "filters",
            "limit",
            "cursor",
            "columns",
        ],

        # Optional API-specific text substitutions. Keep empty unless a future
        # API truly needs a naming/value override.
        "replacements": {},
    },

    "po_funding_detail": {
        "module_name": "po_funding_detail",
        "route_name": "po-funding-detail",
        "singular_name": "po_funding_detail",
        "plural_name": "po_funding_detail",

        "source_schema": "gold",
        "source_view": "po_funding_detail_source_vw",

        # Search API only. The current repository/service implementation does
        # NOT expose a separate get_po_funding_detail_by_* lookup function.
        "key_column": "proj_id",
        "key_argument": "proj_id",
        "sample_key": "P-1001",

        # PoFundingDetailResponse does not expose proj_id.
        # Use po_id for generated response-model assertions while retaining
        # proj_id for repository/search filtering.
        "response_key_field": "po_id",

        # Generated response assertions must only use real response-model fields.
        # po_id is the stable field we validate for this API.
        "response_assert_fields": ["po_id"],

        "sample_field": "proj_name",
        "sample_value": "Test Project",

        "repo_module": "po_funding_detail_repo",
        "repo_search_function": "get_po_funding_detail",
        "repo_key_function": None,

        "service_module": "po_funding_detail_service",
        "service_search_function": "search_po_funding_detail",
        "service_key_function": None,

        "handler_module": "po_funding_detail",
        "handler_search_function": "search_po_funding_detail_v1",
        "handler_key_function": None,
        "handler_details_function": None,

        "response_model": "PoFundingDetailResponse",
        "search_response_model": "PoFundingDetailSearchServiceResponse",

        "default_page_size": 100,
        "default_sort_field": "proj_id",
        "default_sort_order": "asc",

        "supports_search": True,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,
        "supports_filters": True,
        "supports_sort": True,
        "supports_pagination": True,
        "supports_columns": True,
        "uses_pagination_model": True,
        "lookup_supports_filters": False,

        "search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [],
        "repo_key_parameters": [],

        "api_names": [
            "project_financials",
            "project_financial",
            "project-financials",
            "project-financial",
            "po_funding_detail",
            "po-funding-detail",
        ],

        "sample_filter_data": {
            "vendor_name": "proj_name",
            "customer_name": "proj_name",
            "cust_name": "proj_name",
            "Test Vendor": "Test Project",
            "Test Customer": "Test Project",
        },
    },
}


def get_api_config(api_name: str) -> dict:
    if api_name not in APIS:
        available = ", ".join(sorted(APIS))
        raise KeyError(
            f"Unknown API '{api_name}'. Available APIs: {available}"
        )
    return APIS[api_name]


def get_template_file(test_type: str) -> Path:
    if test_type not in TEMPLATE_FILES:
        raise KeyError(f"Unknown test type: {test_type}")
    return TEMPLATE_FILES[test_type]


def get_destination_dir(test_type: str) -> Path:
    if test_type not in DESTINATION_DIRS:
        raise KeyError(f"Unknown test type: {test_type}")
    return DESTINATION_DIRS[test_type]


def validate_config() -> None:
    required_api_fields = [
        "module_name",
        "key_column",
        "sample_key",
        "repo_search_function",
        "service_search_function",
        "handler_search_function",
        "response_model",
        "search_response_model",
    ]

    errors = []
    for api_name, config in APIS.items():
        for field in required_api_fields:
            if field not in config:
                errors.append(f"{api_name}: missing '{field}'")

        if config.get("supports_key_lookup"):
            if not config.get("repo_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True but repo_key_function is missing"
                )
            if not config.get("service_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True but service_key_function is missing"
                )

        if config.get("supports_handler_key_lookup"):
            if not (
                config.get("handler_details_function")
                or config.get("handler_key_function")
            ):
                errors.append(
                    f"{api_name}: supports_handler_key_lookup=True but handler function is missing"
                )

        for mode_field in ("repo_pagination_mode", "service_pagination_mode"):
            mode = config.get(mode_field)
            if mode is not None and mode not in {"page", "limit_cursor"}:
                errors.append(
                    f"{api_name}: {mode_field} must be 'page' or 'limit_cursor'"
                )

        if config.get("search_requires_key"):
            key_argument = config.get("key_argument") or config.get("key_column")
            if not key_argument:
                errors.append(
                    f"{api_name}: search_requires_key=True but key argument is missing"
                )

    if errors:
        raise ValueError(
            "Invalid api_test_config.py:\n" + "\n".join(errors)
        )


if __name__ == "__main__":
    validate_config()

    print()
    print("=" * 80)
    print("API TEST CONFIGURATION")
    print("=" * 80)
    print(f"API_ROOT:           {API_ROOT}")
    print(f"MAIN_FUNCTION_ROOT: {MAIN_FUNCTION_ROOT}")
    print(f"TEST_ROOT:          {TEST_ROOT}")
    print(f"SOURCE_ROOT:        {SOURCE_ROOT}")
    print()

    print("Template files")
    print("-" * 80)
    for test_type, path in TEMPLATE_FILES.items():
        print(f"{test_type:<10} {path} exists={path.exists()}")

    print()
    print("Configured APIs")
    print("-" * 80)
    for api_name, config in APIS.items():
        print(
            f"{api_name:<25} "
            f"search={config['repo_search_function']:<30} "
            f"key_lookup={config.get('supports_key_lookup', False)}"
        )

    print()
    print("Configuration OK")


====================================================================================================

Generator

====================================================================================================



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
        SOURCE_ROOT,
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

    # Field to use when validating a returned response model in generated
    # tests. This can differ from the repository/filter key column.
    #
    # Example: po_funding_detail filters by proj_id, while its Pydantic
    # response model exposes po_id/project_id rather than proj_id.
    response_key_field = first_config_value(
        config,
        "response_key_field",
        default=key_column,
    )

    repo_search_function = first_config_value(
        config,
        "repo_search_function",
        "search_repo_function",
        default=f"get_{module_name}",
    )

    # Key/detail lookup names must NOT be invented unless the API explicitly
    # supports a separate lookup operation.  The old generator always derived
    # get_<api>_by_<key>, which created tests for functions that did not exist.
    configured_repo_key_function = first_config_value(
        config,
        "repo_key_function",
        "lookup_function",
        "repo_lookup_function",
        default=None,
    )

    service_search_function = first_config_value(
        config,
        "service_search_function",
        "search_function",
        default=f"search_{plural_name}",
    )

    configured_service_key_function = first_config_value(
        config,
        "service_key_function",
        "details_function",
        "service_lookup_function",
        default=None,
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

    # Safe default: only generate key/detail lookup tests when the config
    # explicitly declares a lookup function (or explicitly sets the flag).
    # This prevents accidental generation of nonexistent functions such as
    # get_po_funding_detail_by_id.
    inferred_key_lookup = bool(
        configured_repo_key_function
        or configured_service_key_function
        or handler_details_function
    )

    supports_key_lookup = bool(
        first_config_value(
            config,
            "supports_key_lookup",
            default=inferred_key_lookup,
        )
    )

    if supports_key_lookup:
        repo_key_function = (
            configured_repo_key_function
            or f"get_{module_name}_by_{key_param}"
        )
        service_key_function = (
            configured_service_key_function
            or f"get_{module_name}_by_{key_param}"
        )
    else:
        repo_key_function = None
        service_key_function = None

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

    # -----------------------------------------------------------------
    # Declarative function-shape configuration.
    #
    # The generator should not need API-specific edits.  New APIs describe
    # their actual function signatures here and the post-processors adapt
    # template calls accordingly.
    # -----------------------------------------------------------------
    repo_search_parameters = list(
        first_config_value(
            config,
            "repo_search_parameters",
            "search_parameters",
            default=["filters", "sort", "page", "columns"],
        )
    )

    service_search_parameters = list(
        first_config_value(
            config,
            "service_search_parameters",
            default=["filters", "sort", "page", "columns"],
        )
    )

    handler_service_parameters = list(
        first_config_value(
            config,
            "handler_service_parameters",
            default=service_search_parameters,
        )
    )

    repo_pagination_mode = str(
        first_config_value(
            config,
            "repo_pagination_mode",
            default="page" if uses_pagination_model else "limit_cursor",
        )
    )

    service_pagination_mode = str(
        first_config_value(
            config,
            "service_pagination_mode",
            default="page" if uses_pagination_model else "limit_cursor",
        )
    )

    search_requires_key = bool(
        first_config_value(
            config,
            "search_requires_key",
            default=key_param in repo_search_parameters
            or key_param in service_search_parameters,
        )
    )

    handler_path_parameter = first_config_value(
        config,
        "handler_path_parameter",
        default=key_param if search_requires_key else None,
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
            "response_key_field": response_key_field,
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
            "repo_search_parameters": repo_search_parameters,
            "service_search_parameters": service_search_parameters,
            "handler_service_parameters": handler_service_parameters,
            "repo_pagination_mode": repo_pagination_mode,
            "service_pagination_mode": service_pagination_mode,
            "search_requires_key": search_requires_key,
            "handler_path_parameter": handler_path_parameter,
        }
    )

    return config


# =============================================================================
# SOURCE-CODE RECONCILIATION
# =============================================================================


def _python_function_names(path: Path) -> set[str]:
    """Return top-level sync/async function names from a Python source file."""
    if not path.exists():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (SyntaxError, OSError):
        return set()

    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def reconcile_config_with_source(api_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconcile configuration with the REAL implementation before generating tests.

    This is intentionally authoritative: a stale api_test_config.py must never
    make the generator create tests for functions that do not exist.
    """
    config = dict(api_config)
    module_name = config["module_name"]

    repo_file = SOURCE_ROOT / "db" / "repositories" / f"{module_name}_repo.py"
    service_file = SOURCE_ROOT / "domain" / "services" / f"{module_name}_service.py"
    handler_file = SOURCE_ROOT / "v1" / "handlers" / f"{module_name}.py"

    repo_functions = _python_function_names(repo_file)
    service_functions = _python_function_names(service_file)
    handler_functions = _python_function_names(handler_file)

    # Search functions: prefer configured name, but repair common _v1 mismatch.
    repo_search = config.get("repo_search_function")
    if repo_functions and repo_search not in repo_functions:
        fallback = f"get_{module_name}"
        if fallback in repo_functions:
            config["repo_search_function"] = fallback

    service_search = config.get("service_search_function")
    if service_functions and service_search not in service_functions:
        fallback = f"search_{module_name}"
        if fallback in service_functions:
            config["service_search_function"] = fallback

    handler_search = config.get("handler_search_function")
    if handler_functions and handler_search not in handler_functions:
        candidates = unique_nonempty([
            f"{handler_search}_v1" if handler_search else None,
            f"search_{module_name}_v1",
            f"search_{module_name}",
        ])
        for candidate in candidates:
            if candidate in handler_functions:
                config["handler_search_function"] = candidate
                break

    # Key/detail functions: NEVER invent them. If either repo or service lookup
    # does not exist, disable lookup tests for the entire generated stack.
    repo_key = config.get("repo_key_function")
    service_key = config.get("service_key_function")

    repo_key_exists = bool(repo_key and repo_key in repo_functions) if repo_functions else False
    service_key_exists = bool(service_key and service_key in service_functions) if service_functions else False

    if not (repo_key_exists and service_key_exists):
        config["supports_key_lookup"] = False
        config["repo_key_function"] = None
        config["service_key_function"] = None
    else:
        config["supports_key_lookup"] = True

    handler_details = config.get("handler_details_function")
    if not handler_details:
        handler_details = config.get("handler_key_function")

    if handler_functions and handler_details in handler_functions:
        config["handler_details_function"] = handler_details
        config["supports_handler_key_lookup"] = True
    else:
        config["handler_details_function"] = None
        config["supports_handler_key_lookup"] = False

    print("Source reconciliation:")
    print(f"  repo file:     {repo_file}")
    print(f"  service file:  {service_file}")
    print(f"  handler file:  {handler_file}")
    print(f"  repo search:   {config.get('repo_search_function')}")
    print(f"  service search:{config.get('service_search_function')}")
    print(f"  handler search:{config.get('handler_search_function')}")
    print(f"  key lookup:    {config.get('supports_key_lookup')}")
    print(f"  handler lookup:{config.get('supports_handler_key_lookup')}")
    print()

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
# RESPONSE MODEL FIELD NORMALIZATION
# =============================================================================


def fix_response_model_key_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Keep repository/filter keys separate from response-model keys.

    Some APIs filter by one field but expose a different field in the Pydantic
    response model.  For example po_funding_detail uses proj_id as its search
    key, while PoFundingDetailResponse exposes po_id/project_id.

    Only test fixture assignments and returned-model assertions are changed;
    repository filters and API key-column behavior are left untouched.
    """

    key_column = str(api_config["key_column"])
    response_key_field = str(
        api_config.get("response_key_field") or key_column
    )

    if response_key_field == key_column:
        return source

    # Example:
    # sample_po_funding_detail_dict["proj_id"] = expected_proj_id
    # becomes:
    # sample_po_funding_detail_dict["po_id"] = expected_proj_id
    source = re.sub(
        rf'(?P<prefix>\bsample_[A-Za-z0-9_]+_dict\s*\[\s*["\'])'
        rf'{re.escape(key_column)}'
        rf'(?P<suffix>["\']\s*\]\s*=\s*expected_[A-Za-z0-9_]+)',
        lambda match: (
            match.group("prefix")
            + response_key_field
            + match.group("suffix")
        ),
        source,
    )

    # Returned Pydantic model assertion only.
    source = re.sub(
        rf'(\bresult\.items\[0\]\.){re.escape(key_column)}\b',
        rf'\1{response_key_field}',
        source,
    )

    return source


def normalize_no_filter_test_expectations(
    source: str,
) -> str:
    """
    Match the actual service behavior for filters=None.

    The service converts dict filters to FiltersEnvelope, but deliberately
    keeps None as None. Generated *_no_filters tests must therefore assert
    that the repository receives filters=None rather than an empty envelope.
    """

    blocks = iter_test_function_blocks(source)
    replacements: list[tuple[int, int, str]] = []

    for start, end, test_name, block in blocks:
        if not test_name.endswith("_no_filters"):
            continue

        updated = block

        updated = re.sub(
            r'(?m)^[ \t]*assert\s+isinstance\(\s*kwargs\["filters"\]\s*,\s*'
            r'FiltersEnvelope\s*\)\s*$',
            '    assert kwargs["filters"] is None',
            updated,
        )

        updated = re.sub(
            r'(?m)^[ \t]*assert\s+kwargs\["filters"\]\.filters\s*==\s*\{\}\s*$',
            '',
            updated,
        )

        updated = clean_blank_lines(updated)

        if updated != block:
            replacements.append((start, end, updated))

    for start, end, updated in reversed(replacements):
        source = source[:start] + updated + source[end:]

    return clean_blank_lines(source)



# =============================================================================
# RESPONSE MODEL ASSERTION SAFETY
# =============================================================================


def _response_model_field_names(
    api_config: Dict[str, Any],
) -> set[str]:
    """
    Read the real Pydantic response model and return its declared field names.

    This keeps generated tests aligned with the actual target API model instead
    of blindly retaining Project Financial template assertions such as
    result.items[0].proj_name when the target response model has no proj_name.
    """

    module_name = api_config["module_name"]
    response_model = api_config.get("response_model")

    if not response_model:
        return set()

    model_file = (
        SOURCE_ROOT
        / "domain"
        / "models"
        / f"{module_name}.py"
    )

    if not model_file.exists():
        return set()

    try:
        source_text = model_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source_text = model_file.read_text(encoding="utf-8-sig")

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return set()

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        if node.name != response_model:
            continue

        fields: set[str] = set()

        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    fields.add(item.target.id)

        return fields

    return set()


def remove_invalid_response_model_assertions(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Remove generated assertions against attributes that do not exist on the
    real response model.

    Example removed for po_funding_detail:
        assert result.items[0].proj_name == "Test Project"

    PoFundingDetailResponse has po_id/project_id/vendor_name/etc., but no
    proj_name.  The valid po_id assertion remains in place.
    """

    fields = _response_model_field_names(api_config)

    if not fields:
        return source

    pattern = re.compile(
        r'(?m)^(?P<indent>[ \t]*)assert[ \t]+'
        r'result\.items\[0\]\.(?P<field>[A-Za-z_][A-Za-z0-9_]*)'
        r'(?P<rest>[ \t]*==[^\n]*)$'
    )

    def repl(match: re.Match) -> str:
        field = match.group("field")

        if field in fields:
            return match.group(0)

        return ""

    source = pattern.sub(repl, source)

    return clean_blank_lines(source)



# =============================================================================
# CONFIG-DRIVEN RESPONSE ASSERTION PRUNING
# =============================================================================


def prune_response_assertions_by_config(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Keep only explicitly allowed response-model field assertions when
    response_assert_fields is configured.

    This is deterministic and does not depend on locating the target source
    tree at generation time. It is useful when the generator and application
    repo live in different folders.
    """

    configured = api_config.get("response_assert_fields")
    if not configured:
        return source

    allowed = {str(name) for name in configured if name}

    pattern = re.compile(
        r'(?m)^(?P<indent>[ \t]*)assert[ \t]+'
        r'result\.items\[0\]\.(?P<field>[A-Za-z_][A-Za-z0-9_]*)'
        r'(?P<rest>[ \t]*==[^\n]*)$'
    )

    def repl(match: re.Match) -> str:
        if match.group("field") in allowed:
            return match.group(0)
        return ""

    return clean_blank_lines(pattern.sub(repl, source))


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
# CONFIG-DRIVEN FUNCTION CALL NORMALIZATION
# =============================================================================


def _function_call_spans(
    source: str,
    function_name: str,
) -> list[tuple[int, int]]:
    """Return spans for direct calls to function_name(...), in reverse order."""
    if not function_name:
        return []

    pattern = re.compile(
        rf"\b{re.escape(function_name)}\s*\("
    )

    spans: list[tuple[int, int]] = []

    for match in pattern.finditer(source):
        open_paren = source.find("(", match.start())
        if open_paren < 0:
            continue

        close_paren = find_matching_close_paren(source, open_paren)
        if close_paren is None:
            continue

        spans.append((match.start(), close_paren + 1))

    return list(reversed(spans))


def _call_has_keyword(call_text: str, argument_name: str) -> bool:
    return bool(
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(argument_name)}\s*=",
            call_text,
        )
    )


def add_keyword_argument_to_calls(
    source: str,
    function_name: str,
    argument_name: str,
    argument_expression: str,
) -> str:
    """
    Add one keyword argument to calls when it is missing.

    This is intentionally generic so required keys such as contract_id,
    project_id, employee_id, etc. come from config rather than generator code.
    """
    if not function_name or not argument_name:
        return source

    output = source

    for start, end in _function_call_spans(output, function_name):
        call_text = output[start:end]

        if _call_has_keyword(call_text, argument_name):
            continue

        open_rel = call_text.find("(")
        close_rel = call_text.rfind(")")

        if open_rel < 0 or close_rel <= open_rel:
            continue

        inner = call_text[open_rel + 1:close_rel]

        if "\n" in inner:
            # Match indentation of existing arguments where possible.
            lines = inner.splitlines()
            indent = "    "
            for line in lines:
                if line.strip():
                    indent = re.match(r"[ \t]*", line).group(0)
                    break

            addition = (
                "\n"
                + indent
                + f"{argument_name}={argument_expression},"
            )
            new_inner = addition + inner
        else:
            stripped = inner.strip()
            if stripped:
                new_inner = (
                    f"{argument_name}={argument_expression}, "
                    + inner
                )
            else:
                new_inner = (
                    f"{argument_name}={argument_expression}"
                )

        new_call = (
            call_text[:open_rel + 1]
            + new_inner
            + call_text[close_rel:]
        )

        output = output[:start] + new_call + output[end:]

    return output


def normalize_function_call_parameters(
    source: str,
    function_name: str,
    allowed_parameters: Iterable[str],
    *,
    required_key: Optional[str] = None,
    sample_key: Optional[str] = None,
) -> str:
    """
    Remove unsupported common API keyword arguments and add a required key.

    The function-specific allowed list comes entirely from api_test_config.py.
    """
    if not function_name:
        return source

    allowed = {str(item) for item in allowed_parameters if item}

    common_parameters = {
        "filters",
        "sort",
        "page",
        "columns",
        "limit",
        "cursor",
    }

    for argument_name in sorted(common_parameters - allowed):
        source = remove_keyword_argument_from_calls(
            source,
            function_name,
            argument_name,
        )

    if required_key and required_key in allowed:
        source = add_keyword_argument_to_calls(
            source,
            function_name,
            required_key,
            repr(str(sample_key or "TEST-KEY")),
        )

    return source


def normalize_pagination_style(
    source: str,
    function_name: str,
    mode: str,
) -> str:
    """
    Convert template search calls between:
        page=PaginationModel(limit=10)
    and:
        limit=10, cursor=None

    based only on config.
    """
    if not function_name:
        return source

    normalized_mode = str(mode or "page").lower()

    if normalized_mode == "page":
        source = remove_keyword_argument_from_calls(
            source, function_name, "limit"
        )
        source = remove_keyword_argument_from_calls(
            source, function_name, "cursor"
        )
        return source

    if normalized_mode != "limit_cursor":
        return source

    # Extract simple PaginationModel(limit=N[, cursor=...]) calls.
    pattern = re.compile(
        r"page\s*=\s*PaginationModel\s*\(\s*"
        r"limit\s*=\s*(?P<limit>[^,\)\n]+)"
        r"(?:\s*,\s*cursor\s*=\s*(?P<cursor>[^,\)\n]+))?"
        r"\s*\)\s*,?"
    )

    def replace_page(match: re.Match) -> str:
        limit_expr = match.group("limit").strip()
        cursor_expr = (
            match.group("cursor").strip()
            if match.group("cursor")
            else "None"
        )
        return (
            f"limit={limit_expr},\n"
            f"        cursor={cursor_expr},"
        )

    spans = _function_call_spans(source, function_name)
    output = source

    for start, end in spans:
        call_text = output[start:end]
        new_call = pattern.sub(replace_page, call_text)

        if new_call == call_text:
            # If there was no page argument at all, add reasonable defaults
            # only when the call does not already have limit/cursor.
            if not _call_has_keyword(call_text, "limit"):
                open_rel = call_text.find("(")
                close_rel = call_text.rfind(")")
                inner = call_text[open_rel + 1:close_rel]
                if "\n" in inner:
                    lines = inner.splitlines()
                    indent = "    "
                    for line in lines:
                        if line.strip():
                            indent = re.match(r"[ \t]*", line).group(0)
                            break
                    addition = (
                        "\n"
                        + indent
                        + "limit=10,\n"
                        + indent
                        + "cursor=None,"
                    )
                    new_call = (
                        call_text[:open_rel + 1]
                        + addition
                        + inner
                        + call_text[close_rel:]
                    )

        output = output[:start] + new_call + output[end:]

    return output


def normalize_search_call_shapes(
    source: str,
    api_config: Dict[str, Any],
    *,
    test_type: str,
) -> str:
    """
    Apply declarative call-shape rules for repository/service tests.

    No API name is hard-coded here.
    """
    key_param = api_config["key_param"]
    sample_key = api_config["sample_key"]
    requires_key = api_config.get("search_requires_key", False)

    repo_function = api_config.get("repo_search_function")
    service_function = api_config.get("service_search_function")

    if test_type == "db":
        source = normalize_pagination_style(
            source,
            repo_function,
            api_config.get("repo_pagination_mode", "page"),
        )
        source = normalize_function_call_parameters(
            source,
            repo_function,
            api_config.get("repo_search_parameters", []),
            required_key=key_param if requires_key else None,
            sample_key=sample_key,
        )

    elif test_type in {"model", "service"}:
        source = normalize_pagination_style(
            source,
            service_function,
            api_config.get("service_pagination_mode", "page"),
        )
        source = normalize_function_call_parameters(
            source,
            service_function,
            api_config.get("service_search_parameters", []),
            required_key=key_param if requires_key else None,
            sample_key=sample_key,
        )

        # Service tests also exercise/assert the repository dependency.
        source = normalize_pagination_style(
            source,
            repo_function,
            api_config.get("repo_pagination_mode", "page"),
        )
        source = normalize_function_call_parameters(
            source,
            repo_function,
            api_config.get("repo_search_parameters", []),
            required_key=key_param if requires_key else None,
            sample_key=sample_key,
        )

    return source


def ensure_handler_path_parameter(
    source: str,
    api_config: Dict[str, Any],
) -> str:
    """
    Best-effort injection of the configured required path parameter into
    dictionary literals used by generated handler tests.

    The exact key/value still comes from config.
    """
    if not api_config.get("search_requires_key", False):
        return source

    key = api_config.get("handler_path_parameter")
    if not key:
        return source

    sample_key = str(api_config.get("sample_key", "TEST-KEY"))

    # Update existing pathParameters dictionaries.
    pattern = re.compile(
        r'("pathParameters"\s*:\s*)\{(?P<body>[^{}]*)\}'
    )

    def repl(match: re.Match) -> str:
        body = match.group("body")
        if re.search(rf'["\']{re.escape(str(key))}["\']\s*:', body):
            return match.group(0)

        content = body.strip()
        addition = f'"{key}": "{sample_key}"'
        if content:
            addition = addition + ", " + content

        return match.group(1) + "{" + addition + "}"

    updated = pattern.sub(repl, source)

    # If the template has no pathParameters at all, add it immediately after
    # obvious event dictionary openings where queryStringParameters exists.
    if updated == source and '"queryStringParameters"' in source:
        updated = re.sub(
            r'(\{\s*\n)(?P<indent>[ \t]*)("queryStringParameters")',
            lambda m: (
                m.group(1)
                + m.group("indent")
                + f'"pathParameters": {{"{key}": "{sample_key}"}},\n'
                + m.group("indent")
                + m.group(3)
            ),
            source,
        )

    return updated


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

    # New declarative pagination modes are authoritative.  This legacy helper
    # only runs when both layers are configured for page/PaginationModel style.
    if (
        api_config.get("repo_pagination_mode", "page") != "page"
        or api_config.get("service_pagination_mode", "page") != "page"
    ):
        return source

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
    Return complete top-level pytest test-function blocks INCLUDING decorators.

    AST is used here because a decorated test must be removed as one unit.
    Starting at the ``def`` line only leaves orphaned @patch decorators behind
    and creates invalid Python.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # The source entering this function should normally be valid.  If it is
        # not, fall back to a conservative line-based scan rather than making
        # the file worse.
        tree = None

    line_offsets = [0]
    for match in re.finditer(r"\n", source):
        line_offsets.append(match.end())

    def offset_for_line(line_no: int) -> int:
        if line_no <= 1:
            return 0
        index = min(line_no - 1, len(line_offsets) - 1)
        return line_offsets[index]

    blocks: list[tuple[int, int, str, str]] = []

    if tree is not None:
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue

            decorator_lines = [
                decorator.lineno
                for decorator in node.decorator_list
                if getattr(decorator, "lineno", None)
            ]
            start_line = min([node.lineno] + decorator_lines)

            end_line = getattr(node, "end_lineno", node.lineno)
            start_offset = offset_for_line(start_line)

            if end_line < len(line_offsets):
                end_offset = offset_for_line(end_line + 1)
            else:
                end_offset = len(source)

            blocks.append(
                (
                    start_offset,
                    end_offset,
                    node.name,
                    source[start_offset:end_offset],
                )
            )

        return blocks

    # Fallback for unexpected malformed input.
    function_pattern = re.compile(
        r"(?m)^def\s+(test_[A-Za-z0-9_]+)\s*\("
    )
    matches = list(function_pattern.finditer(source))

    for match in matches:
        start_offset = match.start()

        # Walk upward over contiguous top-level decorators.
        cursor = start_offset
        while cursor > 0:
            prev_end = cursor - 1
            if prev_end >= 0 and source[prev_end] == "\n":
                prev_end -= 1
            if prev_end < 0:
                break

            prev_start = source.rfind("\n", 0, prev_end + 1) + 1
            prev_line = source[prev_start:prev_end + 1].strip()

            if prev_line.startswith("@"):
                cursor = prev_start
                start_offset = prev_start
                continue
            break

        # Conservative end: next top-level test def or EOF.
        later = function_pattern.search(source, match.end())
        end_offset = later.start() if later else len(source)

        blocks.append(
            (
                start_offset,
                end_offset,
                match.group(1),
                source[start_offset:end_offset],
            )
        )

    return blocks


def remove_orphan_patch_decorators(source: str) -> str:
    """
    Remove top-level @patch/@patch.object decorator groups that are not followed
    by a function definition.

    This is a final safety net after test removal.  It specifically prevents
    generated files from ending with orphan decorators such as:

        @patch("...")
        @patch("...")

    which is invalid Python.
    """
    lines = source.splitlines(keepends=True)
    output: list[str] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].lstrip()
        is_top_level = len(lines[index]) == len(stripped)

        if is_top_level and (
            stripped.startswith("@patch(")
            or stripped.startswith("@patch.object(")
        ):
            group_start = index
            cursor = index

            # Consume a decorator group.  Supports both one-line decorators and
            # simple multi-line decorator calls by tracking parentheses.
            while cursor < len(lines):
                current = lines[cursor]
                current_stripped = current.lstrip()
                current_top_level = len(current) == len(current_stripped)

                if not current_top_level or not (
                    current_stripped.startswith("@patch(")
                    or current_stripped.startswith("@patch.object(")
                ):
                    break

                depth = current.count("(") - current.count(")")
                cursor += 1

                while depth > 0 and cursor < len(lines):
                    depth += lines[cursor].count("(") - lines[cursor].count(")")
                    cursor += 1

            lookahead = cursor
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1

            if lookahead >= len(lines) or not re.match(
                r"^(?:async\s+)?def\s+test_[A-Za-z0-9_]+\s*\(",
                lines[lookahead],
            ):
                # Drop only the orphan decorators. Preserve blank lines so the
                # surrounding source remains readable.
                index = cursor
                continue

            # Valid decorator group: preserve it.
            output.extend(lines[group_start:cursor])
            index = cursor
            continue

        output.append(lines[index])
        index += 1

    return clean_blank_lines("".join(output))

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
# UNSUPPORTED LOOKUP CLEANUP
# =============================================================================


def remove_name_from_imports(source: str, name: str) -> str:
    """Remove one imported symbol from normal or parenthesized from-imports."""
    if not name:
        return source

    # Parenthesized imports: remove the symbol line/item.
    source = re.sub(
        rf"(?m)^[ \t]*{re.escape(name)}[ \t]*,?[ \t]*\n",
        "",
        source,
    )

    # One-line imports: from x import a, name, b
    pattern = re.compile(r"(?m)^(?P<prefix>from\s+[A-Za-z0-9_\.]+\s+import\s+)(?P<names>[^\n()]+)$")

    def repl(match):
        names = [item.strip() for item in match.group("names").split(",")]
        names = [item for item in names if item and item != name]
        if not names:
            return ""
        return match.group("prefix") + ", ".join(names)

    source = pattern.sub(repl, source)

    # If the removed symbol was the only item in a parenthesized import,
    # remove the now-empty import statement as well.
    source = re.sub(
        r"(?ms)^from\s+[A-Za-z0-9_\.]+\s+import\s*\(\s*\)\s*\n?",
        "",
        source,
    )

    return source


def remove_unsupported_lookup_tests(source: str, api_config: Dict[str, Any]) -> str:
    """Remove template lookup/details tests when the target API has no lookup endpoint."""
    if api_config.get("supports_key_lookup", True):
        return source

    module_name = api_config["module_name"]
    plural_name = api_config["plural_name"]
    key_param = api_config["key_param"]

    names = unique_nonempty([
        api_config.get("repo_key_function"),
        api_config.get("service_key_function"),
        api_config.get("handler_details_function"),
        f"get_{module_name}_by_{key_param}",
        f"get_{plural_name}_by_{key_param}",
        f"get_{module_name}_details",
        f"get_{plural_name}_details",
        f"get_{module_name}_detail",
        f"get_{plural_name}_detail",
    ])

    # Remove complete tests that exercise nonexistent lookup/details functions.
    for name in names:
        source = remove_test_functions_containing(source, name)
        source = remove_name_from_imports(source, name)

    # Catch lookup tests whose function names survived template substitutions.
    source = remove_test_functions_matching_name(
        source,
        [
            rf"test_.*{re.escape(module_name)}.*by_.*",
            rf"test_.*{re.escape(plural_name)}.*by_.*",
            rf"test_get_{re.escape(module_name)}_by_.*",
            rf"test_get_{re.escape(plural_name)}_by_.*",
            rf"test_get_{re.escape(module_name)}_details_.*",
            rf"test_get_{re.escape(plural_name)}_details_.*",
            rf"test_get_{re.escape(module_name)}_detail_.*",
            rf"test_get_{re.escape(plural_name)}_detail_.*",
        ],
    )

    # Remove orphaned patch decorators left immediately before the next test.
    source = re.sub(
        r"(?m)^(?:@patch(?:\.object)?\([^\n]*\)\n)+(?=\s*\n)",
        "",
        source,
    )

    source = remove_orphan_patch_decorators(source)

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
# HANDLER TEST MODEL-DUMP COMPATIBILITY
# =============================================================================


def ensure_handler_mock_items_support_model_dump(
    source: str,
) -> str:
    """
    Make SimpleNamespace-based handler test items support model_dump().
    """

    if "SimpleNamespace" not in source:
        return source

    class_name = "_ModelDumpNamespace"

    if f"class {class_name}(" not in source:
        class_block = (
            "\n"
            "class _ModelDumpNamespace:\n"
            "    \"\"\"Lightweight test double with Pydantic-style model_dump().\"\"\"\n"
            "\n"
            "    def __init__(self, **kwargs):\n"
            "        for key, value in kwargs.items():\n"
            "            setattr(self, key, value)\n"
            "\n"
            "    def model_dump(self):\n"
            "        def convert(value):\n"
            "            if isinstance(value, _ModelDumpNamespace):\n"
            "                return {\n"
            "                    key: convert(item)\n"
            "                    for key, item in vars(value).items()\n"
            "                }\n"
            "\n"
            "            if isinstance(value, list):\n"
            "                return [convert(item) for item in value]\n"
            "\n"
            "            if isinstance(value, tuple):\n"
            "                return tuple(convert(item) for item in value)\n"
            "\n"
            "            if isinstance(value, dict):\n"
            "                return {\n"
            "                    key: convert(item)\n"
            "                    for key, item in value.items()\n"
            "                }\n"
            "\n"
            "            return value\n"
            "\n"
            "        return {\n"
            "            key: convert(value)\n"
            "            for key, value in vars(self).items()\n"
            "        }\n"
            "\n"
        )

        lines = source.splitlines(keepends=True)
        insert_at = 0

        for idx, line in enumerate(lines):
            stripped = line.strip()

            if (
                stripped.startswith("from ")
                or stripped.startswith("import ")
                or stripped == ""
                or stripped.startswith("#")
            ):
                insert_at = idx + 1
                continue

            break

        lines.insert(insert_at, class_block)
        source = "".join(lines)

    source = source.replace(
        "SimpleNamespace(",
        f"{class_name}(",
    )

    return source


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

    source = normalize_search_call_shapes(
        source,
        api_config,
        test_type="db",
    )

    source = remove_old_limit_cursor_arguments(
        source,
        api_config,
    )

    source = remove_unsupported_lookup_tests(
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

    source = fix_response_model_key_assertions(
        source,
        api_config,
    )

    source = normalize_no_filter_test_expectations(
        source,
    )

    source = remove_invalid_response_model_assertions(
        source,
        api_config,
    )

    source = prune_response_assertions_by_config(
        source,
        api_config,
    )

    source = normalize_search_call_shapes(
        source,
        api_config,
        test_type="model",
    )

    source = remove_unsupported_lookup_tests(
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

    source = fix_response_model_key_assertions(
        source,
        api_config,
    )

    source = normalize_no_filter_test_expectations(
        source,
    )

    source = fix_none_filter_expectations(
        source,
    )

    source = remove_invalid_response_model_assertions(
        source,
        api_config,
    )

    source = prune_response_assertions_by_config(
        source,
        api_config,
    )

    source = normalize_search_call_shapes(
        source,
        api_config,
        test_type="service",
    )

    source = remove_old_limit_cursor_arguments(
        source,
        api_config,
    )

    source = normalize_repository_mock_assertions(
        source,
        api_config,
    )

    source = remove_unsupported_lookup_tests(
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

    source = ensure_handler_path_parameter(
        source,
        api_config,
    )

    source = remove_nonexistent_handler_tests(
        source,
        api_config,
    )

    source = remove_unsupported_lookup_tests(
        source,
        api_config,
    )

    source = ensure_handler_mock_items_support_model_dump(
        source,
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

    # Final hard guard for executable layers only.
    #
    # IMPORTANT:
    # Model tests can legitimately contain words such as "..._details" in
    # model/test names even when the API has no separate key/detail endpoint.
    # The previous guard scanned the entire generated model source and treated
    # those harmless names as unsupported endpoint functions, stopping
    # generation even though the Python was valid.
    #
    # Repository, service and handler tests are the layers where an unsupported
    # lookup function would actually be called, so enforce the guard there.
    if (
        test_type in {"db", "service", "handler"}
        and not api_config.get("supports_key_lookup", False)
    ):
        forbidden_patterns = [
            rf"\bget_{re.escape(api_config['module_name'])}_by_[A-Za-z0-9_]+\b",
            rf"\bget_{re.escape(api_config['plural_name'])}_by_[A-Za-z0-9_]+\b",
        ]

        # Detail-handler names are only an error in the handler layer.
        if test_type == "handler":
            forbidden_patterns.extend(
                [
                    rf"\bget_{re.escape(api_config['module_name'])}_details?\b",
                    rf"\bget_{re.escape(api_config['plural_name'])}_details?\b",
                ]
            )

        leftovers: list[str] = []
        for pattern in forbidden_patterns:
            leftovers.extend(
                re.findall(pattern, generated_source)
            )

        if leftovers:
            raise ValueError(
                "Generator safety check failed. Unsupported lookup/detail "
                f"symbols remain in {test_type}: {sorted(set(leftovers))}"
            )

    generated_source = remove_orphan_patch_decorators(
        generated_source
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

    api_config = reconcile_config_with_source(api_config)

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
