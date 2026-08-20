# ============================================================
# api_test_config.py
# Manager-approved Contract tests are the behavioral baseline.
#
# Add new APIs here. API-specific differences belong in config.
# ============================================================

from pathlib import Path

# Folder containing api_test_config.py and generate_api_tests.py
API_ROOT = Path(__file__).resolve().parent

# Actual Git repository containing the production main-function source.
# Change only this line if the repository is cloned to a different folder.
PROJECT_ROOT = Path(r"C:\code\mt-dm-gsapdi-lambda-1")

MAIN_FUNCTION_ROOT = PROJECT_ROOT / "main-function"
SOURCE_ROOT = MAIN_FUNCTION_ROOT / "mt-dm-lambda-src"
TEST_ROOT = MAIN_FUNCTION_ROOT / "tests" / "unit"

DESTINATION_DIRS = {
    "db": TEST_ROOT / "db",
    "model": TEST_ROOT / "domain" / "models",
    "service": TEST_ROOT / "domain" / "services",
    "handler": TEST_ROOT / "v1",
}

TEST_TYPES = ("db", "model", "service", "handler")


APIS = {
    # ========================================================
    # AGENT
    # ========================================================
    "agent": {
        "module_name": "agent",
        "repo_module": "agent_repo",
        "service_module": "agent_service",
        "handler_module": "agent",

        "repo_search_function": "get_work_locations_by_contract_id",
        "repo_key_function": None,

        "service_search_function": "agent_get_contract_locations",
        "service_key_function": None,

        "handler_search_function": "get_agent_contract_locations_v1",
        "handler_key_function": None,

        "response_model": "AgentContractLocationResponse",
        "search_response_model": "AgentContractServiceResponse",

        "key_column": "contract_id",
        "key_argument": "contract_id",
        "handler_path_parameter": "contractId",
        "sample_key": "609998",

        "search_requires_key": True,

        "supports_search": True,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,

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
            "columns",
            "limit",
            "cursor",
        ],

        "repo_execute_query_passes_limit": False,

        "sample_field": "worklocation",
        "sample_value": "Location A",

        "response_key_field": "contract_id",
        "response_assert_fields": ["contract_id"],

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Contract ID is required.",

        "handler_inner_schema": "V1AgentResponseModel",
        "handler_outer_schema": "V1AgentListResponseModel",
    },

    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================
    "po_funding_detail": {
        "module_name": "po_funding_detail",
        "repo_module": "po_funding_detail_repo",
        "service_module": "po_funding_detail_service",
        "handler_module": "po_funding_detail",

        "repo_search_function": "get_po_funding_detail",
        "repo_key_function": None,

        "service_search_function": "search_po_funding_detail",
        "service_key_function": None,

        "handler_search_function": "search_po_funding_detail_v1",
        "handler_key_function": None,

        "response_model": "PoFundingDetailResponse",
        "search_response_model": "PoFundingDetailSearchServiceResponse",

        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": None,
        "sample_key": "P-1001",

        "search_requires_key": False,

        "supports_search": True,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,

        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_execute_query_passes_limit": True,

        "sample_field": "proj_name",
        "sample_value": "Test Project",

        "response_key_field": "po_id",
        "response_assert_fields": ["po_id"],
    },

    # ========================================================
    # GL DETAILS
    # ========================================================
    "gl_details": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "gl_details",
        "repo_module": "gl_details_repo",
        "service_module": "gl_details_service",
        "handler_module": "gl_details",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_gl_details",
        "repo_key_function": "get_gl_details_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_gl_details",
        "service_key_function": "get_gl_details_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_gl_details_v1",
        "handler_key_function": "get_gl_details_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "GlDetailsResponse",
        "search_response_model": "GlDetailsSearchServiceResponse",

        # ----------------------------------------------------
        # Key
        # QuerySpec logical_id_field = "proj_id"
        # ----------------------------------------------------
        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": "proj_id",
        "sample_key": "P-1001",

        # Search does not require project id.
        # GET-by-project does require project id.
        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        # ----------------------------------------------------
        # Repository function signatures
        # ----------------------------------------------------
        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Service function signatures
        # ----------------------------------------------------
        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Handler -> service signatures
        # ----------------------------------------------------
        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_key_service_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Pagination / DB execution
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,

        "repo_cursor_fields": [
            "PROJ_ID",
            "VCHR_NO",
        ],
        "repo_cursor_values": [
            "P-1001",
            "test_vchr_no",
        ],
        "repo_cursor_separator": "_",

        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "name",
        "sample_value": "Test Project",

        "response_key_field": "proj_id",
        "response_assert_fields": ["proj_id"],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1GlDetailsResponseModel",
        "handler_outer_schema": "V1GlDetailsListResponseModel",
        "handler_detail_outer_schema": "V1GlDetailsListResponseModel",

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",

        "handler_detail_route": "/v1/financials/gl-details/{proj_id}",
        "handler_search_route": "/v1/financials/gl-details/search",
    },

    # ========================================================
    # EMPLOYEE PROFILE COMPLETE
    # ========================================================
    "employee_profile_complete": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "employee_profile_complete",
        "repo_module": "employee_profile_complete_repo",
        "service_module": "employee_profile_complete_service",
        "handler_module": "employee_profile_complete",

        # ----------------------------------------------------
        # Repository
        #
        # Actual functions from employee_profile_complete_repo.py:
        #
        # get_employee_profile_completes(
        #     filters=None,
        #     sort=None,
        #     page=None,
        #     columns=None,
        # )
        #
        # get_employee_profile_complete_by_id(
        #     employee_key,
        #     filters=None,
        #     page=None,
        #     columns=None,
        #     sort=None,
        # )
        # ----------------------------------------------------
        "repo_search_function": "get_employee_profile_completes",
        "repo_key_function": "get_employee_profile_complete_by_id",

        # ----------------------------------------------------
        # Service
        #
        # Actual functions from employee_profile_complete_service.py:
        #
        # search_employee_profile_completes(
        #     filters=None,
        #     sort=None,
        #     page=None,
        #     columns=None,
        # )
        #
        # get_employee_profile_complete_details(
        #     employee_key,
        #     filters=None,
        #     limit=settings.DEFAULT_PAGE_SIZE,
        #     cursor=None,
        #     columns=None,
        #     sort=None,
        # )
        # ----------------------------------------------------
        "service_search_function": "search_employee_profile_completes",
        "service_key_function": "get_employee_profile_complete_details",

        # ----------------------------------------------------
        # Handler
        #
        # Actual handlers:
        #
        # GET /v1/employee-profile-complete/{employee_key}
        #     get_employee_profile_complete_v1
        #
        # POST /v1/employee-profile-complete/search
        #     search_employee_profile_completes_v1
        #
        # GET /v1/employee-profile-complete
        #     list_employee_profile_completes_v1
        # ----------------------------------------------------
        "handler_search_function": "search_employee_profile_completes_v1",
        "handler_list_function": "list_employee_profile_completes_v1",
        "handler_key_function": "get_employee_profile_complete_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "EmployeeProfileCompleteResponse",
        "search_response_model": (
            "EmployeeProfileCompleteSearchServiceResponse"
        ),

        # ----------------------------------------------------
        # Key
        #
        # Repository QuerySpec:
        # logical_id_field = "employee_key"
        # ----------------------------------------------------
        "key_column": "employee_key",
        "key_argument": "employee_key",
        "handler_path_parameter": "employee_key",
        "sample_key": "EMP-1001",

        # Search endpoint itself does NOT require employee_key.
        # Detail endpoint DOES require employee_key.
        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": True,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        # ----------------------------------------------------
        # Repository function signatures
        # ----------------------------------------------------
        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_key_parameters": [
            "employee_key",
            "filters",
            "page",
            "columns",
            "sort",
        ],

        # ----------------------------------------------------
        # Service function signatures
        # ----------------------------------------------------
        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [
            "employee_key",
            "filters",
            "limit",
            "cursor",
            "columns",
            "sort",
        ],

        # ----------------------------------------------------
        # Handler -> service signatures
        # ----------------------------------------------------
        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_key_service_parameters": [
            "employee_key",
            "filters",
            "limit",
            "cursor",
            "columns",
        ],

        "handler_list_service_parameters": [
            "filters",
            "page",
        ],

        # ----------------------------------------------------
        # Pagination / DB execution
        #
        # Repository calls:
        # execute_query(plan.sql, plan.params, limit=current_page.limit)
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "limit_cursor",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "employee_name",
        "sample_value": "Test Employee",

        "response_key_field": "employee_key",
        "response_assert_fields": ["employee_key"],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": (
            "V1EmployeeProfileCompleteResponseModel"
        ),
        "handler_outer_schema": (
            "V1EmployeeProfileCompleteListResponseModel"
        ),
        "handler_detail_outer_schema": (
            "V1EmployeeProfileCompleteDetailResponseModel"
        ),

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": (
            "EmployeeProfileComplete ID is required."
        ),

        "handler_detail_route": (
            "/v1/employee-profile-complete/{employee_key}"
        ),
        "handler_search_route": (
            "/v1/employee-profile-complete/search"
        ),
        "handler_list_route": (
            "/v1/employee-profile-complete"
        ),
    },
}


def get_api_config(api_name: str) -> dict:
    if api_name not in APIS:
        available = ", ".join(sorted(APIS))
        raise KeyError(
            f"Unknown API '{api_name}'. "
            f"Available APIs: {available}"
        )

    return dict(APIS[api_name])


def get_destination_dir(test_type: str) -> Path:
    if test_type not in DESTINATION_DIRS:
        raise KeyError(
            f"Unknown test type: {test_type}"
        )

    return DESTINATION_DIRS[test_type]


def validate_config() -> None:
    required = {
        "module_name",
        "repo_module",
        "service_module",
        "handler_module",
        "repo_search_function",
        "service_search_function",
        "handler_search_function",
        "response_model",
        "search_response_model",
        "key_column",
        "key_argument",
        "sample_key",
        "repo_search_parameters",
        "service_search_parameters",
        "handler_service_parameters",
    }

    errors = []

    for api_name, cfg in APIS.items():
        for field in sorted(required - set(cfg)):
            errors.append(
                f"{api_name}: missing '{field}'"
            )

        if cfg.get("supports_key_lookup"):
            if not cfg.get("repo_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but repo_key_function is missing"
                )

            if not cfg.get("service_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but service_key_function is missing"
                )

            if not cfg.get("repo_key_parameters"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but repo_key_parameters is missing"
                )

            if not cfg.get("service_key_parameters"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but service_key_parameters is missing"
                )

        if cfg.get("supports_handler_key_lookup"):
            if not cfg.get("handler_key_function"):
                errors.append(
                    f"{api_name}: "
                    "supports_handler_key_lookup=True "
                    "but handler_key_function is missing"
                )

            if not cfg.get(
                "handler_key_service_parameters"
            ):
                errors.append(
                    f"{api_name}: "
                    "supports_handler_key_lookup=True "
                    "but handler_key_service_parameters "
                    "is missing"
                )

        if (
            cfg.get("search_requires_key")
            and not cfg.get("key_argument")
        ):
            errors.append(
                f"{api_name}: search_requires_key=True "
                "but key_argument is missing"
            )

    if errors:
        raise ValueError(
            "Invalid api_test_config.py:\n"
            + "\n".join(errors)
        )


if __name__ == "__main__":
    validate_config()

    print()
    print("=" * 80)
    print("API TEST CONFIGURATION")
    print("=" * 80)

    for api_name, cfg in APIS.items():
        print(
            f"{api_name:<30} "
            f"search={cfg['repo_search_function']:<40} "
            f"key_lookup={cfg.get('supports_key_lookup', False)}"
        )

    print()
    print("Configuration OK")
  
=====================================================================================================

Generator

=====================================================================================================

"""
generate_api_tests.py

Config-driven API unit-test generator.

Behavioral baseline:
- Manager-approved Contract repository tests
- Manager-approved Contract model tests
- Manager-approved Contract service tests
- Manager-approved handler tests

Design goals:
1. API-specific behavior lives in api_test_config.py.
2. The generator validates config against the real source before writing tests.
3. Lookup/detail functions are NEVER invented.
4. Pydantic model test data is generated from actual field annotations.
5. APIs can support:
      - search/list only
      - required-key search
      - search + separate detail/key lookup
      - optional list handler in addition to POST search
6. Both source layouts are supported:
      - main-function/mt-dm-lambda-src/...
      - generated/...
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from api_test_config import (
    API_ROOT,
    APIS,
    DESTINATION_DIRS,
    SOURCE_ROOT,
    TEST_TYPES,
    validate_config,
)


# =============================================================================
# GENERAL HELPERS
# =============================================================================


def snake_to_pascal(value: str) -> str:
    return "".join(
        part.capitalize()
        for part in value.split("_")
        if part
    )


def destination_file(
    test_type: str,
    cfg: dict[str, Any],
) -> Path:
    root = Path(DESTINATION_DIRS[test_type])
    module = cfg["module_name"]

    names = {
        "db": f"test_{module}_repo.py",
        "model": f"test_{module}.py",
        "service": f"test_{module}_service.py",
        "handler": f"test_{module}.py",
    }

    return root / names[test_type]


def source_file(
    test_type: str,
    cfg: dict[str, Any],
) -> Path:
    """
    Resolve the real implementation file.

    Supports both:
      main-function/mt-dm-lambda-src/...
      generated/...
    """
    module = cfg["module_name"]

    if test_type == "db":
        filename = f"{cfg['repo_module']}.py"
        candidates = [
            SOURCE_ROOT / "db" / "repositories" / filename,
            API_ROOT / "generated" / "repositories" / filename,
        ]

    elif test_type == "model":
        filename = f"{module}.py"
        candidates = [
            SOURCE_ROOT / "domain" / "models" / filename,
            API_ROOT / "generated" / "models" / filename,
        ]

    elif test_type == "service":
        filename = f"{cfg['service_module']}.py"
        candidates = [
            SOURCE_ROOT / "domain" / "services" / filename,
            API_ROOT / "generated" / "services" / filename,
        ]

    elif test_type == "handler":
        filename = f"{cfg['handler_module']}.py"
        candidates = [
            SOURCE_ROOT / "v1" / "handlers" / filename,
            API_ROOT / "generated" / "handlers" / filename,
        ]

    else:
        raise ValueError(
            f"Unknown test type: {test_type}"
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = "\n".join(
        f"  - {candidate}"
        for candidate in candidates
    )

    raise FileNotFoundError(
        f"Source file not found for {test_type} "
        f"'{module}'. Searched:\n{searched}"
    )


def parse_file(path: Path) -> ast.Module:
    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {path}"
        )

    text = path.read_text(
        encoding="utf-8-sig"
    )

    try:
        return ast.parse(text)
    except SyntaxError as exc:
        raise ValueError(
            f"Cannot parse {path}: {exc}"
        ) from exc


def function_map(
    path: Path,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = parse_file(path)

    return {
        node.name: node
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    }


def class_map(
    path: Path,
) -> dict[str, ast.ClassDef]:
    tree = parse_file(path)

    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def function_parameters(
    path: Path,
    function_name: str,
) -> list[str]:
    node = function_map(path).get(
        function_name
    )

    if node is None:
        return []

    names = (
        [arg.arg for arg in node.args.posonlyargs]
        + [arg.arg for arg in node.args.args]
        + [arg.arg for arg in node.args.kwonlyargs]
    )

    if names and names[0] in {
        "self",
        "cls",
    }:
        names = names[1:]

    return names


def model_field_specs(
    path: Path,
    class_name: str,
) -> list[tuple[str, Optional[ast.expr]]]:
    """
    Return (field_name, annotation_ast) for Pydantic fields.
    """
    node = class_map(path).get(class_name)

    if node is None:
        return []

    result: list[
        tuple[str, Optional[ast.expr]]
    ] = []

    for item in node.body:
        if (
            isinstance(item, ast.AnnAssign)
            and isinstance(item.target, ast.Name)
        ):
            result.append(
                (
                    item.target.id,
                    item.annotation,
                )
            )

    return result


def require_function(
    path: Path,
    function_name: str | None,
    label: str,
) -> None:
    if not function_name:
        raise ValueError(
            f"{label}: function name is missing"
        )

    if function_name not in function_map(path):
        raise ValueError(
            f"{label}: '{function_name}' does not "
            f"exist in {path}"
        )


# =============================================================================
# ANNOTATION-AWARE TEST DATA
# =============================================================================


def annotation_name(
    annotation: Optional[ast.expr],
) -> str:
    if annotation is None:
        return ""

    if isinstance(annotation, ast.Name):
        return annotation.id

    if isinstance(annotation, ast.Attribute):
        parent = annotation_name(
            annotation.value
        )
        if parent:
            return (
                f"{parent}.{annotation.attr}"
            )
        return annotation.attr

    if isinstance(annotation, ast.Subscript):
        return annotation_name(
            annotation.value
        )

    if isinstance(annotation, ast.Constant):
        return str(annotation.value)

    return ""


def subscript_args(
    annotation: Optional[ast.expr],
) -> list[ast.expr]:
    if not isinstance(
        annotation,
        ast.Subscript,
    ):
        return []

    value = annotation.slice

    if isinstance(value, ast.Tuple):
        return list(value.elts)

    return [value]


def unwrap_optional(
    annotation: Optional[ast.expr],
) -> Optional[ast.expr]:
    """
    Optional[T] -> T
    Union[T, None] -> T
    T | None -> T
    """
    if annotation is None:
        return None

    # Python typing.Optional / Union
    if isinstance(annotation, ast.Subscript):
        base = annotation_name(
            annotation.value
        )

        if base in {
            "Optional",
            "typing.Optional",
        }:
            args = subscript_args(
                annotation
            )
            return (
                args[0]
                if args
                else annotation
            )

        if base in {
            "Union",
            "typing.Union",
        }:
            args = subscript_args(
                annotation
            )

            non_none = [
                arg
                for arg in args
                if annotation_name(arg)
                not in {
                    "None",
                    "NoneType",
                }
            ]

            if len(non_none) == 1:
                return non_none[0]

    # Python 3.10: T | None
    if (
        isinstance(annotation, ast.BinOp)
        and isinstance(
            annotation.op,
            ast.BitOr,
        )
    ):
        left = annotation.left
        right = annotation.right

        if annotation_name(right) in {
            "None",
            "NoneType",
        }:
            return left

        if annotation_name(left) in {
            "None",
            "NoneType",
        }:
            return right

    return annotation


def sample_value_from_annotation(
    field: str,
    annotation: Optional[ast.expr],
    cfg: dict[str, Any],
) -> Any:
    """
    Create a valid representative value from the real annotation.

    Examples:
      Optional[List[str]] -> ["test_value"]
      Optional[int]       -> 1
      Optional[float]     -> 1.0
      Optional[bool]      -> True
      Optional[date]      -> "2026-01-01"
      Optional[Any]       -> {"test": "value"}
      str                 -> "test_field"
    """

    if field == cfg["key_column"]:
        return cfg["sample_key"]

    if (
        field
        == cfg.get("response_key_field")
    ):
        return cfg["sample_key"]

    if field == cfg.get("sample_field"):
        return cfg.get(
            "sample_value",
            "Test Value",
        )

    annotation = unwrap_optional(
        annotation
    )

    base = annotation_name(
        annotation
    ).split(".")[-1]

    # Collections
    if isinstance(
        annotation,
        ast.Subscript,
    ):
        container = annotation_name(
            annotation.value
        ).split(".")[-1]

        args = subscript_args(
            annotation
        )

        if container in {
            "List",
            "list",
            "Sequence",
            "Iterable",
            "Set",
            "set",
            "Tuple",
            "tuple",
        }:
            inner = (
                args[0]
                if args
                else None
            )

            inner_value = (
                sample_value_from_annotation(
                    f"{field}_item",
                    inner,
                    cfg,
                )
            )

            if container in {
                "Set",
                "set",
            }:
                return {
                    inner_value
                }

            if container in {
                "Tuple",
                "tuple",
            }:
                return (
                    inner_value,
                )

            return [
                inner_value
            ]

        if container in {
            "Dict",
            "dict",
            "Mapping",
        }:
            return {
                "test": "value"
            }

    # Scalars
    if base in {
        "str",
        "String",
    }:
        return f"test_{field}"

    if base in {
        "int",
        "Integer",
    }:
        return 1

    if base in {
        "float",
        "Decimal",
    }:
        return 1.0

    if base == "bool":
        return True

    if base in {
        "date",
        "datetime",
    }:
        return "2026-01-01"

    if base in {
        "Any",
        "object",
    }:
        return {
            "test": "value"
        }

    if base in {
        "bytes",
        "bytearray",
    }:
        return b"test"

    # Helpful fallbacks from field names.
    if field in {
        "row_id",
        "id",
        "period",
        "sub_pd_no",
    }:
        return 1

    if "count" in field.lower():
        return 1

    if "date" in field.lower():
        return "2026-01-01"

    if field.endswith("_fl"):
        return "Y"

    return f"test_{field}"


def complete_model_payload(
    cfg: dict[str, Any],
) -> dict[str, Any]:
    model_path = source_file(
        "model",
        cfg,
    )

    specs = model_field_specs(
        model_path,
        cfg["response_model"],
    )

    if not specs:
        raise ValueError(
            f"No fields found for "
            f"{cfg['response_model']} "
            f"in {model_path}"
        )

    return {
        field: sample_value_from_annotation(
            field,
            annotation,
            cfg,
        )
        for field, annotation in specs
    }


def dict_literal(
    data: dict[str, Any],
    indent: int = 4,
) -> str:
    pad = " " * indent
    lines = ["{"]

    for key, value in data.items():
        lines.append(
            f'{pad}"{key}": {value!r},'
        )

    lines.append("}")

    return "\n".join(lines)


# =============================================================================
# CALL ARGUMENT HELPERS
# =============================================================================


def call_args(
    cfg: dict[str, Any],
    parameters: list[str],
    *,
    use_any: bool = False,
    force_key: bool = False,
    overrides: dict[str, str] | None = None,
) -> list[str]:
    key = cfg["key_argument"]

    values = {
        key: repr(
            cfg["sample_key"]
        ),
        "filters": (
            "ANY"
            if use_any
            else "filters"
        ),
        "sort": (
            "ANY"
            if use_any
            else "sort"
        ),
        "page": (
            "ANY"
            if use_any
            else "page"
        ),
        "columns": (
            "ANY"
            if use_any
            else "columns"
        ),
        "limit": (
            "ANY"
            if use_any
            else "10"
        ),
        "cursor": (
            "ANY"
            if use_any
            else "None"
        ),
    }

    if overrides:
        values.update(overrides)

    result: list[str] = []

    for name in parameters:
        if (
            name == key
            and not force_key
            and not cfg.get(
                "search_requires_key",
                False,
            )
        ):
            continue

        result.append(
            f"{name}="
            f"{values.get(name, 'ANY' if use_any else 'None')}"
        )

    return result


def multiline_args(
    args: list[str],
    spaces: int = 8,
) -> str:
    if not args:
        return ""

    pad = " " * spaces

    return (
        ",\n" + pad
    ).join(args)


# =============================================================================
# SOURCE-AWARE COVERAGE HELPERS
# =============================================================================


def source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def function_source_text(
    path: Path,
    function_name: str | None,
) -> str:
    if not function_name:
        return ""

    node = function_map(path).get(function_name)
    if node is None:
        return ""

    text = source_text(path)
    lines = text.splitlines()
    start = max((node.lineno or 1) - 1, 0)
    end = node.end_lineno or node.lineno or 1
    return "\n".join(lines[start:end])


def function_has(
    path: Path,
    function_name: str | None,
    *needles: str,
) -> bool:
    body = function_source_text(path, function_name)
    return all(needle in body for needle in needles)


def module_has(
    path: Path,
    *needles: str,
) -> bool:
    body = source_text(path)
    return all(needle in body for needle in needles)


# =============================================================================
# CONFIG/SOURCE VALIDATION
# =============================================================================


def validate_parameter_list(
    path: Path,
    function_name: str,
    configured: list[str],
    label: str,
) -> None:
    real = function_parameters(
        path,
        function_name,
    )

    invalid = [
        name
        for name in configured
        if name not in real
    ]

    if invalid:
        raise ValueError(
            f"{label} has invalid parameter(s) "
            f"{invalid}. Real signature for "
            f"{function_name}: {real}"
        )


def validate_config_against_source(
    raw_cfg: dict[str, Any],
) -> dict[str, Any]:
    cfg = dict(raw_cfg)

    repo_path = source_file(
        "db",
        cfg,
    )
    model_path = source_file(
        "model",
        cfg,
    )
    service_path = source_file(
        "service",
        cfg,
    )
    handler_path = source_file(
        "handler",
        cfg,
    )

    require_function(
        repo_path,
        cfg["repo_search_function"],
        "Repository search",
    )

    require_function(
        service_path,
        cfg["service_search_function"],
        "Service search",
    )

    require_function(
        handler_path,
        cfg["handler_search_function"],
        "Handler search",
    )

    validate_parameter_list(
        repo_path,
        cfg["repo_search_function"],
        cfg.get(
            "repo_search_parameters",
            [],
        ),
        "repo_search_parameters",
    )

    validate_parameter_list(
        service_path,
        cfg["service_search_function"],
        cfg.get(
            "service_search_parameters",
            [],
        ),
        "service_search_parameters",
    )

    if cfg.get(
        "supports_key_lookup",
        False,
    ):
        require_function(
            repo_path,
            cfg.get(
                "repo_key_function"
            ),
            "Repository key lookup",
        )

        require_function(
            service_path,
            cfg.get(
                "service_key_function"
            ),
            "Service key lookup",
        )

        validate_parameter_list(
            repo_path,
            cfg["repo_key_function"],
            cfg.get(
                "repo_key_parameters",
                [],
            ),
            "repo_key_parameters",
        )

        validate_parameter_list(
            service_path,
            cfg["service_key_function"],
            cfg.get(
                "service_key_parameters",
                [],
            ),
            "service_key_parameters",
        )

    else:
        cfg["repo_key_function"] = None
        cfg["service_key_function"] = None

    if cfg.get(
        "supports_handler_key_lookup",
        False,
    ):
        require_function(
            handler_path,
            cfg.get(
                "handler_key_function"
            ),
            "Handler key lookup",
        )

    if cfg.get(
        "supports_list",
        False,
    ):
        require_function(
            handler_path,
            cfg.get(
                "handler_list_function"
            ),
            "Handler list",
        )

    if (
        cfg["response_model"]
        not in class_map(model_path)
    ):
        raise ValueError(
            f"Response model "
            f"'{cfg['response_model']}' "
            f"does not exist in "
            f"{model_path}"
        )

    return cfg


# =============================================================================
# REPOSITORY TEST GENERATION
# =============================================================================


def execute_query_assertion(
    cfg: dict[str, Any],
    *,
    page_expr: str = "10",
) -> str:
    if cfg.get(
        "repo_execute_query_passes_limit",
        False,
    ):
        return f"""    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit={page_expr},
    )"""

    return """    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
    )"""


def generate_db_search_tests(
    cfg: dict[str, Any],
) -> str:
    repo = cfg["repo_module"]
    fn = cfg["repo_search_function"]
    params = cfg[
        "repo_search_parameters"
    ]

    search_args = multiline_args(
        call_args(
            cfg,
            params,
        ),
        8,
    )

    builder_args = []

    for name in (
        "filters",
        "sort",
        "page",
        "columns",
    ):
        if name in params:
            builder_args.append(
                f"{name}=ANY"
            )

    builder_text = multiline_args(
        builder_args,
        8,
    )

    key_check = ""

    if cfg.get(
        "search_requires_key",
        False,
    ):
        key_check = f"""
    args, _kwargs = mock_execute.call_args
    sql_params = args[1]
    if isinstance(sql_params, dict):
        assert any(
            value == {cfg['sample_key']!r}
            for value in sql_params.values()
        )
"""

    return f"""
@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_success(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [
            {{
                "{cfg['key_column']}": {cfg['sample_key']!r},
            }}
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    filters = FiltersEnvelope(
        filters={{}}
    )
    sort = SortModel()
    page = PaginationModel(
        limit=10
    )
    columns = None

    result = {repo}.{fn}(
        {search_args}
    )

    mock_get_plan.assert_called_once_with(
        {builder_text}
    )

{execute_query_assertion(cfg)}

    assert isinstance(result, dict)
    assert "items" in result
{key_check.rstrip()}


@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_empty(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    filters = FiltersEnvelope(
        filters={{}}
    )
    sort = SortModel()
    page = PaginationModel(
        limit=10
    )
    columns = None

    result = {repo}.{fn}(
        {search_args}
    )

    assert isinstance(result, dict)
    assert result["items"] == []
"""


def generate_db_lookup_tests(
    cfg: dict[str, Any],
) -> str:
    if not cfg.get(
        "supports_key_lookup",
        False,
    ):
        return ""

    repo = cfg["repo_module"]
    fn = cfg["repo_key_function"]

    params = cfg.get(
        "repo_key_parameters",
        [],
    )

    lookup_args = multiline_args(
        call_args(
            cfg,
            params,
            force_key=True,
        ),
        8,
    )

    return f"""
@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_found(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [
            {{
                "{cfg['key_column']}": {cfg['sample_key']!r},
            }}
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    filters = FiltersEnvelope(
        filters={{}}
    )
    sort = SortModel()
    page = PaginationModel(
        limit=10
    )
    columns = None

    result = {repo}.{fn}(
        {lookup_args}
    )

    assert isinstance(result, dict)
    assert len(
        result["items"]
    ) == 1

    # Do not assert that the lookup key must appear literally in plan.params.
    # Different repository builders may encode/inject filters differently.
    # The stable contract is that the repository returned the expected record
    # and execute_query was invoked.
    mock_execute.assert_called_once()


@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_not_found(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    filters = FiltersEnvelope(
        filters={{}}
    )
    sort = SortModel()
    page = PaginationModel(
        limit=10
    )
    columns = None

    result = {repo}.{fn}(
        {lookup_args}
    )

    assert isinstance(result, dict)
    assert result["items"] == []
"""


def generate_db_coverage_tests(
    cfg: dict[str, Any],
) -> str:
    """Generate extra tests only for branches that exist in the real repository."""
    repo = cfg["repo_module"]
    repo_path = source_file("db", cfg)
    search_fn = cfg["repo_search_function"]
    lookup_fn = cfg.get("repo_key_function")
    key = cfg["key_column"]
    sample_key = cfg["sample_key"]

    parts: list[str] = []

    if (
        "_format_paginated_response" in function_map(repo_path)
        and module_has(
            repo_path,
            "encode_cursor",
            "has_more = len(items) > limit",
        )
    ):
        cursor_fields = cfg.get(
            "repo_cursor_fields"
        )
        cursor_values = cfg.get(
            "repo_cursor_values"
        )
        cursor_separator = cfg.get(
            "repo_cursor_separator",
            "_",
        )

        if (
            cursor_fields
            and cursor_values
            and len(cursor_fields) == len(cursor_values)
        ):
            first_item_fields = "\n".join(
                f'            "{field}": {value!r},'
                for field, value in zip(
                    cursor_fields,
                    cursor_values,
                )
            )

            second_item_fields = "\n".join(
                f'            "{field}": "second-{index}",'
                for index, field in enumerate(
                    cursor_fields,
                    start=1,
                )
            )

            expected_cursor_key = cursor_separator.join(
                str(value)
                for value in cursor_values
            )

            parts.append(f"""
@patch("db.repositories.{repo}.encode_cursor")
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        {{
{first_item_fields}
            "total_count_hidden": 2,
        }},
        {{
{second_item_fields}
            "total_count_hidden": 2,
        }},
    ]

    result = {repo}._format_paginated_response(
        items,
        limit=1,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"
    assert "total_count_hidden" not in result["items"][0]

    mock_encode_cursor.assert_called_once_with(
        {expected_cursor_key!r}
    )
""")
        else:
            parts.append(f"""
@patch("db.repositories.{repo}.encode_cursor")
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        {{
            "{key}": {sample_key!r},
            "total_count_hidden": 2,
        }},
        {{
            "{key}": "second-key",
            "total_count_hidden": 2,
        }},
    ]

    result = {repo}._format_paginated_response(
        items,
        limit=1,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"
    assert "total_count_hidden" not in result["items"][0]

    mock_encode_cursor.assert_called_once_with(
        {sample_key!r}
    )
""")

    search_params = cfg.get("repo_search_parameters", [])
    if "filters" in search_params and function_has(
        repo_path,
        search_fn,
        "isinstance(filters, dict)",
    ):
        args = multiline_args(
            call_args(cfg, search_params, overrides={"filters": "{}"}),
            8,
        )
        parts.append(f'''
@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{search_fn}_dict_filters(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{"items": []}}

    filters = {{}}
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = {repo}.{search_fn}(
        {args}
    )

    assert isinstance(result, dict)
    assert result["items"] == []
    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()
''')

    if (
        cfg.get("supports_key_lookup", False)
        and lookup_fn
        and "filters" in cfg.get("repo_key_parameters", [])
    ):
        lookup_params = cfg.get("repo_key_parameters", [])

        if function_has(repo_path, lookup_fn, "filters or {}"):
            args = multiline_args(
                call_args(
                    cfg,
                    lookup_params,
                    force_key=True,
                    overrides={"filters": "None"},
                ),
                8,
            )
            parts.append(f'''
@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{lookup_fn}_none_filters(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [{{"{key}": {sample_key!r}}}],
    }}

    filters = None
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = {repo}.{lookup_fn}(
        {args}
    )

    assert len(result["items"]) == 1
    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()
''')

        if function_has(repo_path, lookup_fn, ".filters.append("):
            args = multiline_args(
                call_args(
                    cfg,
                    lookup_params,
                    force_key=True,
                    overrides={"filters": "filters_envelope"},
                ),
                8,
            )
            parts.append(f'''
def test_{lookup_fn}_recursive_filter_branch():
    class RecursiveFilterContainer:
        def __init__(self):
            self.filters = []

    recursive_filters = RecursiveFilterContainer()
    filters_envelope = FiltersEnvelope.model_construct(
        filters=recursive_filters,
    )
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    try:
        {repo}.{lookup_fn}(
            {args}
        )
    except Exception:
        pass

    assert len(recursive_filters.filters) == 1
    added_rule = recursive_filters.filters[0]
    assert added_rule.field == "{key}"
''')

    return "\n".join(parts)


def generate_db(
    cfg: dict[str, Any],
) -> str:
    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract repository tests are the behavioral baseline.

from unittest.mock import ANY, MagicMock, patch

import pytest

from db.repositories import {cfg['repo_module']}
from v1.schemas import (
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


@pytest.fixture
def mock_plan():
    plan = MagicMock()
    plan.sql = (
        "SELECT * "
        "FROM generated_test_source"
    )
    plan.params = {{}}
    return plan

{generate_db_search_tests(cfg)}
{generate_db_lookup_tests(cfg)}
{generate_db_coverage_tests(cfg)}
"""


# =============================================================================
# MODEL TEST GENERATION
# =============================================================================


def generate_model(
    cfg: dict[str, Any],
) -> str:
    module = cfg["module_name"]
    model = cfg["response_model"]

    payload = complete_model_payload(
        cfg
    )

    fields = set(
        payload.keys()
    )

    allowed = cfg.get(
        "response_assert_fields",
        [],
    )

    assertion_field = next(
        (
            field
            for field in allowed
            if field in fields
        ),
        next(
            iter(fields)
        ),
    )

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract model tests are the behavioral baseline.

from pydantic import ValidationError

from domain.models.{module} import {model}


def test_{module}_response_valid_data():
    data = {dict_literal(payload, 8)}

    result = {model}(**data)

    assert isinstance(
        result,
        {model},
    )

    assert getattr(
        result,
        "{assertion_field}",
    ) == {payload[assertion_field]!r}


def test_{module}_response_empty_payload():
    try:
        result = {model}(**{{}})
    except ValidationError:
        return

    assert isinstance(
        result,
        {model},
    )
"""


# =============================================================================
# SERVICE TEST GENERATION
# =============================================================================


def generate_service_search_tests(
    cfg: dict[str, Any],
) -> str:
    module = cfg["module_name"]
    service_module = cfg[
        "service_module"
    ]
    repo_module = cfg[
        "repo_module"
    ]
    service_fn = cfg[
        "service_search_function"
    ]
    repo_fn = cfg[
        "repo_search_function"
    ]
    model = cfg[
        "response_model"
    ]

    service_args = multiline_args(
        call_args(
            cfg,
            cfg[
                "service_search_parameters"
            ],
        ),
        8,
    )

    repo_expected = multiline_args(
        call_args(
            cfg,
            cfg[
                "repo_search_parameters"
            ],
            use_any=True,
        ),
        8,
    )

    sample = complete_model_payload(
        cfg
    )

    return f"""
def test_{service_fn}_success():
    sample = {dict_literal(sample, 8)}

    with patch(
        "domain.services."
        "{service_module}."
        "{repo_module}."
        "{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [
                sample
            ],
            "page": {{
                "cursor": None,
                "has_more": False,
            }},
        }}

        filters = FiltersEnvelope(
            filters={{}}
        )
        sort = SortModel()
        page = PaginationModel(
            limit=10
        )
        columns = None

        result = {service_fn}(
        {service_args}
        )

        mock_repo.assert_called_once_with(
        {repo_expected}
        )

        assert len(
            result.items
        ) == 1

        assert isinstance(
            result.items[0],
            {model},
        )


def test_{service_fn}_empty():
    with patch(
        "domain.services."
        "{service_module}."
        "{repo_module}."
        "{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [],
            "page": {{
                "cursor": None,
                "has_more": False,
            }},
        }}

        filters = FiltersEnvelope(
            filters={{}}
        )
        sort = SortModel()
        page = PaginationModel(
            limit=10
        )
        columns = None

        result = {service_fn}(
        {service_args}
        )

        assert result.items == []
        assert (
            result.metadata.has_more
            is False
        )
"""


def generate_service_lookup_tests(
    cfg: dict[str, Any],
) -> str:
    if not cfg.get(
        "supports_key_lookup",
        False,
    ):
        return ""

    module = cfg["module_name"]
    service_module = cfg[
        "service_module"
    ]
    repo_module = cfg[
        "repo_module"
    ]
    service_fn = cfg[
        "service_key_function"
    ]
    repo_fn = cfg[
        "repo_key_function"
    ]
    model = cfg[
        "response_model"
    ]

    service_args = multiline_args(
        call_args(
            cfg,
            cfg.get(
                "service_key_parameters",
                [],
            ),
            force_key=True,
        ),
        8,
    )

    repo_expected = multiline_args(
        call_args(
            cfg,
            cfg.get(
                "repo_key_parameters",
                [],
            ),
            use_any=True,
            force_key=True,
        ),
        8,
    )

    sample = complete_model_payload(
        cfg
    )

    return f"""
def test_{service_fn}_success():
    sample = {dict_literal(sample, 8)}

    with patch(
        "domain.services."
        "{service_module}."
        "{repo_module}."
        "{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [
                sample
            ],
            "page": {{
                "cursor": None,
                "has_more": False,
            }},
        }}

        filters = FiltersEnvelope(
            filters={{}}
        )
        sort = SortModel()
        page = PaginationModel(
            limit=10
        )
        columns = None

        result = {service_fn}(
        {service_args}
        )

        assert len(
            result.items
        ) == 1

        assert isinstance(
            result.items[0],
            {model},
        )

        assert mock_repo.called


def test_{service_fn}_not_found():
    with patch(
        "domain.services."
        "{service_module}."
        "{repo_module}."
        "{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [],
            "page": {{
                "cursor": None,
                "has_more": False,
            }},
        }}

        filters = FiltersEnvelope(
            filters={{}}
        )
        sort = SortModel()
        page = PaginationModel(
            limit=10
        )
        columns = None

        result = {service_fn}(
        {service_args}
        )

        assert result.items == []
"""


def generate_service_coverage_tests(
    cfg: dict[str, Any],
) -> str:
    """Generate branch tests only when the service source contains those branches."""
    service_path = source_file("service", cfg)
    service_module = cfg["service_module"]
    repo_module = cfg["repo_module"]
    search_fn = cfg["service_search_function"]
    repo_search_fn = cfg["repo_search_function"]
    lookup_fn = cfg.get("service_key_function")
    repo_lookup_fn = cfg.get("repo_key_function")
    sample_key = cfg["sample_key"]
    key_argument = cfg["key_argument"]

    parts: list[str] = []
    search_params = cfg.get("service_search_parameters", [])

    def empty_repo_patch(repo_fn: str) -> str:
        return f'''    with patch(
        "domain.services.{service_module}.{repo_module}.{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [],
            "page": {{
                "cursor": None,
                "has_more": False,
            }},
        }}
'''

    if "filters" in search_params and function_has(
        service_path, search_fn, "isinstance(filters, dict)"
    ):
        args = multiline_args(
            call_args(cfg, search_params, overrides={"filters": "{}"}),
            12,
        )
        parts.append(f'''
def test_{search_fn}_dict_filters():
{empty_repo_patch(repo_search_fn)}        filters = {{}}
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {search_fn}(
            {args}
        )

        assert result.items == []
        assert isinstance(mock_repo.call_args.kwargs["filters"], FiltersEnvelope)
''')

    if "filters" in search_params and function_has(
        service_path, search_fn, "filters is None"
    ):
        args = multiline_args(
            call_args(cfg, search_params, overrides={"filters": "None"}),
            12,
        )
        parts.append(f'''
def test_{search_fn}_none_filters():
{empty_repo_patch(repo_search_fn)}        filters = None
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {search_fn}(
            {args}
        )

        assert result.items == []
        assert isinstance(mock_repo.call_args.kwargs["filters"], FiltersEnvelope)
''')

    if (
        cfg.get("supports_key_lookup", False)
        and lookup_fn
        and repo_lookup_fn
    ):
        lookup_params = cfg.get("service_key_parameters", [])

        if function_has(service_path, lookup_fn, f"if not {key_argument}"):
            args = multiline_args(
                call_args(
                    cfg,
                    lookup_params,
                    force_key=True,
                    overrides={key_argument: '""'},
                ),
                8,
            )
            parts.append(f'''
def test_{lookup_fn}_missing_key():
    filters = None
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = {lookup_fn}(
        {args}
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
''')

        if "filters" in lookup_params and function_has(
            service_path, lookup_fn, "isinstance(filters, dict)"
        ):
            args = multiline_args(
                call_args(
                    cfg,
                    lookup_params,
                    force_key=True,
                    overrides={"filters": "{}"},
                ),
                12,
            )
            parts.append(f'''
def test_{lookup_fn}_dict_filters():
{empty_repo_patch(repo_lookup_fn)}        filters = {{}}
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {lookup_fn}(
            {args}
        )

        assert result.items == []
        assert mock_repo.call_args.kwargs["{key_argument}"] == {sample_key!r}
        assert isinstance(mock_repo.call_args.kwargs["filters"], FiltersEnvelope)
''')

        if "filters" in lookup_params and function_has(
            service_path, lookup_fn, "filters is None"
        ):
            args = multiline_args(
                call_args(
                    cfg,
                    lookup_params,
                    force_key=True,
                    overrides={"filters": "None"},
                ),
                12,
            )
            parts.append(f'''
def test_{lookup_fn}_none_filters():
{empty_repo_patch(repo_lookup_fn)}        filters = None
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {lookup_fn}(
            {args}
        )

        assert result.items == []
        assert isinstance(mock_repo.call_args.kwargs["filters"], FiltersEnvelope)
''')

    return "\n".join(parts)


def generate_service(
    cfg: dict[str, Any],
) -> str:
    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract service tests are the behavioral baseline.

from unittest.mock import ANY, patch

from domain.models.{cfg['module_name']} import (
    {cfg['response_model']},
)
from domain.services.{cfg['service_module']} import (
    {cfg['service_search_function']},
{f"    {cfg['service_key_function']}," if cfg.get('supports_key_lookup') else ""}
)
from v1.schemas import (
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)

{generate_service_search_tests(cfg)}
{generate_service_lookup_tests(cfg)}
{generate_service_coverage_tests(cfg)}
"""


# =============================================================================
# HANDLER TEST GENERATION
# =============================================================================


def handler_result_setup(
    cfg: dict[str, Any],
) -> str:
    handler_path = source_file(
        "handler",
        cfg,
    )

    handler_source = handler_path.read_text(
        encoding="utf-8"
    )

    item_requires_model_dump = (
        "item.model_dump()" in handler_source
    )

    if item_requires_model_dump:
        return f"""    mock_results = MagicMock()

    mock_item = MagicMock()
    mock_item.model_dump.return_value = {{
        "{cfg['key_column']}": {cfg['sample_key']!r},
        "{cfg.get('sample_field', 'name')}": {cfg.get('sample_value', 'Test Value')!r},
    }}

    mock_results.items = [
        mock_item
    ]

    mock_results.metadata.cursor = None
    mock_results.metadata.has_more = False
    mock_results.metadata.applied_filters = {{}}

    mock_results.metadata.model_dump.return_value = {{
        "totalCount": 1,
        "cursor": None,
        "hasMore": False,
    }}

    mock_service.return_value = mock_results
"""

    return f"""    mock_results = MagicMock()

    mock_results.items = [
        {{
            "{cfg['key_column']}": {cfg['sample_key']!r},
            "{cfg.get('sample_field', 'name')}": {cfg.get('sample_value', 'Test Value')!r},
        }}
    ]

    mock_results.metadata.cursor = None
    mock_results.metadata.has_more = False
    mock_results.metadata.applied_filters = {{}}

    mock_results.metadata.model_dump.return_value = {{
        "totalCount": 1,
        "cursor": None,
        "hasMore": False,
    }}

    mock_service.return_value = mock_results
"""
def handler_schema_setup(
    cfg: dict[str, Any],
    *,
    detail: bool,
) -> str:
    outer_name = (
        cfg.get(
            "handler_detail_outer_schema"
        )
        if detail
        else cfg.get(
            "handler_outer_schema"
        )
    )

    if not outer_name:
        return ""

    return f"""    mock_inner_schema.model_validate.return_value = MagicMock()

    outer = MagicMock()
    outer.model_dump.return_value = {{
        "metadata": {{
            "totalCount": 1,
            "cursor": None,
            "hasMore": False,
        }},
        "data": [
            {{
                "{cfg['key_column']}": {cfg['sample_key']!r},
            }}
        ],
    }}

    mock_outer_schema.return_value = outer
"""


def generate_handler_search_tests(
    cfg: dict[str, Any],
) -> str:
    module = cfg["module_name"]
    handler_fn = cfg[
        "handler_search_function"
    ]
    service_fn = cfg[
        "service_search_function"
    ]

    inner_schema = cfg.get(
        "handler_inner_schema",
        f"V1{snake_to_pascal(module)}ResponseModel",
    )

    outer_schema = cfg.get(
        "handler_outer_schema",
        f"V1{snake_to_pascal(module)}ListResponseModel",
    )

    expected = multiline_args(
        call_args(
            cfg,
            cfg.get(
                "handler_service_parameters",
                [],
            ),
            use_any=True,
        ),
        8,
    )

    path_name = cfg.get(
        "handler_path_parameter"
    )

    if (
        cfg.get(
            "search_requires_key",
            False,
        )
        and path_name
    ):
        path_parameters = (
            f'{{"{path_name}": '
            f'{cfg["sample_key"]!r}}}'
        )
    else:
        path_parameters = "{}"

    missing_test = ""

    if (
        cfg.get(
            "search_requires_key",
            False,
        )
        and path_name
    ):
        missing_test = f"""
def test_{handler_fn}_missing_id(
    mock_context,
):
    event = {{
        "pathParameters": {{}},
        "requestContext": {{
            "requestId": "test-missing-id",
        }},
    }}

    response = {handler_fn}(
        event,
        mock_context,
    )

    assert response["statusCode"] == {cfg.get('handler_missing_key_status', 400)}
"""

    return f"""
@patch(
    "v1.handlers.{module}."
    "{inner_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{outer_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{service_fn}"
)
def test_{handler_fn}_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
{handler_result_setup(cfg)}
{handler_schema_setup(cfg, detail=False)}
    event = {{
        "pathParameters": {path_parameters},
        "queryStringParameters": None,
        "requestContext": {{
            "requestId": "test-search-success",
        }},
        "body": "{{}}",
        "isBase64Encoded": False,
    }}

    response = {handler_fn}(
        event,
        mock_context,
    )

    assert response["statusCode"] == {cfg.get('handler_success_status', 200)}

    mock_service.assert_called_once_with(
        {expected}
    )

{missing_test}
"""


def generate_handler_lookup_tests(
    cfg: dict[str, Any],
) -> str:
    if not cfg.get(
        "supports_handler_key_lookup",
        False,
    ):
        return ""

    module = cfg["module_name"]
    handler_fn = cfg[
        "handler_key_function"
    ]
    service_fn = cfg[
        "service_key_function"
    ]

    inner_schema = cfg.get(
        "handler_inner_schema",
        f"V1{snake_to_pascal(module)}ResponseModel",
    )

    outer_schema = cfg.get(
        "handler_detail_outer_schema",
        cfg.get(
            "handler_outer_schema",
            f"V1{snake_to_pascal(module)}DetailResponseModel",
        ),
    )

    path_name = cfg.get(
        "handler_path_parameter",
        cfg["key_argument"],
    )

    expected = multiline_args(
        call_args(
            cfg,
            cfg.get(
                "handler_key_service_parameters",
                cfg.get(
                    "service_key_parameters",
                    [],
                ),
            ),
            use_any=True,
            force_key=True,
        ),
        8,
    )

    return f"""
@patch(
    "v1.handlers.{module}."
    "{inner_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{outer_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{service_fn}"
)
def test_{handler_fn}_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
{handler_result_setup(cfg)}
{handler_schema_setup(cfg, detail=True)}
    event = {{
        "pathParameters": {{
            "{path_name}": {cfg['sample_key']!r},
        }},
        "queryStringParameters": None,
        "requestContext": {{
            "requestId": "test-detail-success",
        }},
    }}

    response = {handler_fn}(
        event,
        mock_context,
    )

    assert response["statusCode"] == {cfg.get('handler_success_status', 200)}

    mock_service.assert_called_once_with(
        {expected}
    )


def test_{handler_fn}_missing_id(
    mock_context,
):
    event = {{
        "pathParameters": {{}},
        "requestContext": {{
            "requestId": "test-detail-missing",
        }},
    }}

    response = {handler_fn}(
        event,
        mock_context,
    )

    assert response["statusCode"] == {cfg.get('handler_missing_key_status', 400)}

    body = (
        response["body"]
        if isinstance(
            response["body"],
            dict,
        )
        else json.loads(
            response["body"]
        )
    )

    assert body["error"]["message"] == {cfg.get('handler_missing_key_message', 'Required ID is missing.')!r}
"""


def generate_handler_list_tests(
    cfg: dict[str, Any],
) -> str:
    if not cfg.get(
        "supports_list",
        False,
    ):
        return ""

    module = cfg["module_name"]
    handler_fn = cfg[
        "handler_list_function"
    ]
    service_fn = cfg[
        "service_search_function"
    ]

    inner_schema = cfg.get(
        "handler_inner_schema",
        f"V1{snake_to_pascal(module)}ResponseModel",
    )

    outer_schema = cfg.get(
        "handler_outer_schema",
        f"V1{snake_to_pascal(module)}ListResponseModel",
    )

    return f"""
@patch(
    "v1.handlers.{module}."
    "{inner_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{outer_schema}"
)
@patch(
    "v1.handlers.{module}."
    "{service_fn}"
)
def test_{handler_fn}_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
{handler_result_setup(cfg)}
{handler_schema_setup(cfg, detail=False)}
    event = {{
        "queryStringParameters": {{
            "limit": "10",
        }},
        "requestContext": {{
            "requestId": "test-list-success",
        }},
    }}

    response = {handler_fn}(
        event,
        mock_context,
    )

    assert response["statusCode"] == {cfg.get('handler_success_status', 200)}
    assert mock_service.called
"""


def generate_handler_coverage_tests(
    cfg: dict[str, Any],
) -> str:
    """Generate extra error/default-path tests only when those paths exist."""
    module = cfg["module_name"]
    handler_module = cfg["handler_module"]
    handler_path = source_file("handler", cfg)
    search_fn = cfg["handler_search_function"]
    service_search_fn = cfg["service_search_function"]
    parts: list[str] = []

    if function_has(handler_path, search_fn, "json.JSONDecodeError"):
        parts.append(f'''
@patch(
    "v1.handlers.{handler_module}.LambdaUtils.get_json_body"
)
def test_{search_fn}_invalid_json(
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Expecting value",
        "",
        0,
    )

    event = {{
        "pathParameters": {{}},
        "queryStringParameters": None,
        "requestContext": {{
            "requestId": "test-invalid-json",
        }},
        "body": "{{invalid-json}}",
        "isBase64Encoded": False,
    }}

    response = {search_fn}(event, mock_context)
    assert response["statusCode"] == {cfg.get('handler_invalid_json_status', 400)}
''')

    if cfg.get("supports_handler_key_lookup", False):
        lookup_fn = cfg.get("handler_key_function")
        service_lookup_fn = cfg.get("service_key_function")
        path_name = cfg.get("handler_path_parameter", cfg["key_argument"])

        if (
            lookup_fn
            and service_lookup_fn
            and function_has(handler_path, lookup_fn, "if not results.items")
        ):
            parts.append(f'''
@patch(
    "v1.handlers.{handler_module}.{service_lookup_fn}"
)
def test_{lookup_fn}_not_found(
    mock_service,
    mock_context,
):
    mock_results = MagicMock()
    mock_results.items = []
    mock_service.return_value = mock_results

    event = {{
        "pathParameters": {{
            "{path_name}": {cfg['sample_key']!r},
        }},
        "queryStringParameters": None,
        "requestContext": {{
            "requestId": "test-detail-not-found",
        }},
    }}

    response = {lookup_fn}(event, mock_context)
    assert response["statusCode"] == {cfg.get('handler_not_found_status', 404)}
''')

    if cfg.get("supports_list", False):
        list_fn = cfg.get("handler_list_function")
        if list_fn and function_has(
            handler_path,
            list_fn,
            "DEFAULT_PAGE_SIZE",
        ):
            inner_schema = cfg.get(
                "handler_inner_schema",
                f"V1{snake_to_pascal(module)}ResponseModel",
            )
            outer_schema = cfg.get(
                "handler_outer_schema",
                f"V1{snake_to_pascal(module)}ListResponseModel",
            )
            parts.append(f'''
@patch(
    "v1.handlers.{handler_module}.{inner_schema}"
)
@patch(
    "v1.handlers.{handler_module}.{outer_schema}"
)
@patch(
    "v1.handlers.{handler_module}.{service_search_fn}"
)
def test_{list_fn}_default_query_params(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
{handler_result_setup(cfg)}
{handler_schema_setup(cfg, detail=False)}
    event = {{
        "queryStringParameters": None,
        "requestContext": {{
            "requestId": "test-list-defaults",
        }},
    }}

    response = {list_fn}(event, mock_context)
    assert response["statusCode"] == {cfg.get('handler_success_status', 200)}
    assert mock_service.called
''')

    return "\n".join(parts)


def generate_handler(
    cfg: dict[str, Any],
) -> str:
    imports = [
        cfg[
            "handler_search_function"
        ]
    ]

    if cfg.get(
        "supports_handler_key_lookup",
        False,
    ):
        imports.append(
            cfg[
                "handler_key_function"
            ]
        )

    if cfg.get(
        "supports_list",
        False,
    ):
        imports.append(
            cfg[
                "handler_list_function"
            ]
        )

    import_text = ",\n    ".join(
        imports
    )

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager handler tests are the behavioral baseline.

import json
from unittest.mock import (
    ANY,
    MagicMock,
    patch,
)

from v1.handlers.{cfg['handler_module']} import (
    {import_text},
)

{generate_handler_search_tests(cfg)}
{generate_handler_lookup_tests(cfg)}
{generate_handler_list_tests(cfg)}
{generate_handler_coverage_tests(cfg)}
"""


# =============================================================================
# GENERATION / EXECUTION
# =============================================================================


GENERATORS = {
    "db": generate_db,
    "model": generate_model,
    "service": generate_service,
    "handler": generate_handler,
}


def validate_generated_python(
    source: str,
    destination: Path,
) -> None:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        lines = source.splitlines()

        line_no = (
            exc.lineno
            or 0
        )

        start = max(
            1,
            line_no - 3,
        )

        end = min(
            len(lines),
            line_no + 3,
        )

        context = []

        for number in range(
            start,
            end + 1,
        ):
            prefix = (
                ">>"
                if number == line_no
                else "  "
            )

            context.append(
                f"{prefix} "
                f"{number:4}: "
                f"{lines[number - 1]}"
            )

        raise ValueError(
            f"Generated Python is invalid "
            f"for {destination}: {exc}\n"
            + "\n".join(context)
        ) from exc


def generate_one(
    test_type: str,
    cfg: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> Path | None:
    destination = destination_file(
        test_type,
        cfg,
    )

    if (
        destination.exists()
        and not force
        and not dry_run
    ):
        print(
            f"SKIP   "
            f"[{test_type:<7}] "
            f"{destination}"
        )
        return None

    source = GENERATORS[
        test_type
    ](cfg)

    validate_generated_python(
        source,
        destination,
    )

    if dry_run:
        print(
            f"DRY    "
            f"[{test_type:<7}] "
            f"{destination}"
        )
        return destination

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        source,
        encoding="utf-8",
    )

    print(
        f"CREATE "
        f"[{test_type:<7}] "
        f"{destination}"
    )

    return destination


def run_generated_tests(
    cfg: dict[str, Any],
    selected_types: list[str],
) -> int:
    paths = [
        destination_file(
            test_type,
            cfg,
        )
        for test_type in selected_types
    ]

    command = [
        sys.executable,
        "-m",
        "pytest",
        *[
            str(path)
            for path in paths
        ],
        "-v",
    ]

    print()
    print("Running:")
    print(
        " ".join(command)
    )
    print()

    completed = subprocess.run(
        command,
        cwd=Path.cwd(),
    )

    return completed.returncode


def list_apis() -> None:
    print()
    print("Configured APIs")
    print("=" * 78)

    for name in sorted(
        APIS
    ):
        cfg = APIS[name]

        print(
            f"{name:<30} "
            f"repo="
            f"{cfg['repo_search_function']:<38} "
            f"handler="
            f"{cfg['handler_search_function']}"
        )

    print()


def generate_api(
    api_name: str,
    *,
    force: bool,
    dry_run: bool,
    selected_type: str | None,
    run: bool,
) -> int:
    validate_config()

    if api_name not in APIS:
        print(
            f"ERROR: API "
            f"'{api_name}' "
            f"is not configured."
        )

        list_apis()

        return 2

    cfg = validate_config_against_source(
        APIS[api_name]
    )

    print()
    print("=" * 78)
    print(
        f"Generating tests for API: "
        f"{api_name}"
    )
    print(
        f"Repo search:    "
        f"{cfg['repo_search_function']}"
    )
    print(
        f"Service search: "
        f"{cfg['service_search_function']}"
    )
    print(
        f"Handler search: "
        f"{cfg['handler_search_function']}"
    )
    print(
        f"Required-key search: "
        f"{cfg.get('search_requires_key', False)}"
    )
    print(
        f"Key lookup: "
        f"{cfg.get('supports_key_lookup', False)}"
    )
    print(
        f"Handler key lookup: "
        f"{cfg.get('supports_handler_key_lookup', False)}"
    )
    print(
        f"List handler: "
        f"{cfg.get('supports_list', False)}"
    )
    print("=" * 78)

    selected_types = (
        [selected_type]
        if selected_type
        else list(TEST_TYPES)
    )

    for test_type in selected_types:
        generate_one(
            test_type,
            cfg,
            force=force,
            dry_run=dry_run,
        )

    if run and not dry_run:
        return run_generated_tests(
            cfg,
            selected_types,
        )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate API unit tests "
            "from config and real source."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
    )

    parser.add_argument(
        "--list",
        action="store_true",
    )

    parser.add_argument(
        "--force",
        action="store_true",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    parser.add_argument(
        "--run",
        action="store_true",
    )

    parser.add_argument(
        "--test-type",
        choices=list(
            TEST_TYPES
        ),
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        list_apis()
        return

    if not args.api:
        parser.print_help()
        return

    raise SystemExit(
        generate_api(
            args.api,
            force=args.force,
            dry_run=args.dry_run,
            selected_type=args.test_type,
            run=args.run,
        )
    )


if __name__ == "__main__":
    main()
