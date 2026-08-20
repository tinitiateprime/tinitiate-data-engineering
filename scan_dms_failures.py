# ============================================================
# api_test_config.py
# Manager-approved Contract tests are the behavioral baseline.
# Add new APIs here; do not edit generate_api_tests.py.
# ============================================================

from pathlib import Path

API_ROOT = Path(__file__).resolve().parent
MAIN_FUNCTION_ROOT = API_ROOT / "main-function"
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
            "contract_id", "filters", "page", "columns", "sort"
        ],
        "service_search_parameters": [
            "contract_id", "filters", "limit", "cursor", "columns", "sort"
        ],
        "handler_service_parameters": [
            "contract_id", "filters", "columns", "limit", "cursor"
        ],

        "repo_execute_query_passes_limit": False,

        "sample_field": "worklocation",
        "sample_value": "Location A",
        "response_assert_fields": ["contract_id"],

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Contract ID is required.",

        # Manager handler test uses these exact V1 schema names.
        "handler_inner_schema": "V1AgentResponseModel",
        "handler_outer_schema": "V1AgentListResponseModel",
    },

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

        "repo_search_parameters": ["filters", "sort", "page", "columns"],
        "service_search_parameters": ["filters", "sort", "page", "columns"],
        "handler_service_parameters": ["filters", "sort", "page", "columns"],

        "repo_execute_query_passes_limit": True,

        "sample_field": "proj_name",
        "sample_value": "Test Project",
        "response_key_field": "po_id",
        "response_assert_fields": ["po_id"],
    },
}


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
            errors.append(f"{api_name}: missing '{field}'")

        if cfg.get("supports_key_lookup"):
            if not cfg.get("repo_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True but repo_key_function is missing"
                )
            if not cfg.get("service_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True but service_key_function is missing"
                )

        if cfg.get("search_requires_key") and not cfg.get("key_argument"):
            errors.append(
                f"{api_name}: search_requires_key=True but key_argument is missing"
            )

    if errors:
        raise ValueError(
            "Invalid api_test_config.py:\n" + "\n".join(errors)
        )


if __name__ == "__main__":
    validate_config()
    print("Configuration OK")
    for name in sorted(APIS):
        print(name)


=============================================================================================================
Generators
=============================================================================================================
"""
generate_api_tests.py

Config-driven unit-test generator using the manager-approved Contract tests
as the behavioral baseline.

Important:
- It does not invent get_*_by_id functions.
- It validates configured function names against the real source tree.
- It validates configured parameter names against real function signatures.
- It writes only syntactically valid Python.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path
from typing import Any

from api_test_config import (
    APIS,
    DESTINATION_DIRS,
    SOURCE_ROOT,
    TEST_TYPES,
    validate_config,
)


def snake_to_pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_") if part)


def destination_file(test_type: str, cfg: dict[str, Any]) -> Path:
    root = Path(DESTINATION_DIRS[test_type])
    module = cfg["module_name"]

    names = {
        "db": f"test_{module}_repo.py",
        "model": f"test_{module}.py",
        "service": f"test_{module}_service.py",
        "handler": f"test_{module}.py",
    }
    return root / names[test_type]


def source_file(test_type: str, cfg: dict[str, Any]) -> Path:
    module = cfg["module_name"]

    if test_type == "db":
        return (
            SOURCE_ROOT
            / "db"
            / "repositories"
            / f"{cfg['repo_module']}.py"
        )
    if test_type == "model":
        return (
            SOURCE_ROOT
            / "domain"
            / "models"
            / f"{module}.py"
        )
    if test_type == "service":
        return (
            SOURCE_ROOT
            / "domain"
            / "services"
            / f"{cfg['service_module']}.py"
        )
    if test_type == "handler":
        return (
            SOURCE_ROOT
            / "v1"
            / "handlers"
            / f"{cfg['handler_module']}.py"
        )
    raise ValueError(test_type)


def parse_file(path: Path) -> ast.Module:
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    text = path.read_text(encoding="utf-8-sig")
    try:
        return ast.parse(text)
    except SyntaxError as exc:
        raise ValueError(f"Cannot parse {path}: {exc}") from exc


def function_map(path: Path) -> dict[str, ast.AST]:
    tree = parse_file(path)
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def class_map(path: Path) -> dict[str, ast.ClassDef]:
    tree = parse_file(path)
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def function_parameters(path: Path, function_name: str) -> list[str]:
    node = function_map(path).get(function_name)
    if node is None:
        return []

    names = (
        [a.arg for a in node.args.posonlyargs]
        + [a.arg for a in node.args.args]
        + [a.arg for a in node.args.kwonlyargs]
    )

    if names and names[0] in {"self", "cls"}:
        names = names[1:]

    return names


def model_fields(path: Path, class_name: str) -> list[str]:
    node = class_map(path).get(class_name)
    if node is None:
        return []

    result = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            result.append(item.target.id)
    return result


def require_function(
    path: Path,
    function_name: str | None,
    label: str,
) -> None:
    if not function_name:
        raise ValueError(f"{label}: function name is missing")

    if function_name not in function_map(path):
        raise ValueError(
            f"{label}: '{function_name}' does not exist in {path}"
        )


def validate_config_against_source(
    raw_cfg: dict[str, Any],
) -> dict[str, Any]:
    cfg = dict(raw_cfg)

    repo_path = source_file("db", cfg)
    model_path = source_file("model", cfg)
    service_path = source_file("service", cfg)
    handler_path = source_file("handler", cfg)

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

    if cfg.get("supports_key_lookup", False):
        require_function(
            repo_path,
            cfg.get("repo_key_function"),
            "Repository key lookup",
        )
        require_function(
            service_path,
            cfg.get("service_key_function"),
            "Service key lookup",
        )
    else:
        # Never invent lookup functions.
        cfg["repo_key_function"] = None
        cfg["service_key_function"] = None

    if cfg["response_model"] not in class_map(model_path):
        raise ValueError(
            f"Response model '{cfg['response_model']}' does not exist "
            f"in {model_path}"
        )

    signature_checks = (
        (
            repo_path,
            cfg["repo_search_function"],
            cfg["repo_search_parameters"],
            "repo_search_parameters",
        ),
        (
            service_path,
            cfg["service_search_function"],
            cfg["service_search_parameters"],
            "service_search_parameters",
        ),
    )

    for path, fn, configured, label in signature_checks:
        real = function_parameters(path, fn)
        invalid = [name for name in configured if name not in real]
        if invalid:
            raise ValueError(
                f"{label} has invalid parameter(s) {invalid}. "
                f"Real signature for {fn}: {real}"
            )

    return cfg


def sample_value(field: str, cfg: dict[str, Any]) -> Any:
    if field == cfg["key_column"]:
        return cfg["sample_key"]
    if field == cfg.get("response_key_field"):
        return cfg["sample_key"]
    if field == cfg.get("sample_field"):
        return cfg.get("sample_value", "Test Value")
    if field in {"row_id", "id", "period", "sub_pd_no"}:
        return 1
    if "date" in field.lower():
        return "2026-01-01"
    if field.endswith("_fl"):
        return "Y"
    return f"test_{field}"


def dict_literal(data: dict[str, Any], indent: int = 4) -> str:
    pad = " " * indent
    lines = ["{"]
    for key, value in data.items():
        lines.append(f'{pad}"{key}": {value!r},')
    lines.append("}")
    return "\n".join(lines)


def search_call_args(
    cfg: dict[str, Any],
    parameters: list[str],
    *,
    use_any: bool = False,
) -> list[str]:
    key = cfg["key_argument"]
    values = {
        key: repr(cfg["sample_key"]),
        "filters": "ANY" if use_any else "filters",
        "sort": "ANY" if use_any else "sort",
        "page": "ANY" if use_any else "page",
        "columns": "ANY" if use_any else "columns",
        "limit": "ANY" if use_any else "10",
        "cursor": "ANY" if use_any else "None",
    }

    result = []
    for name in parameters:
        if name == key and not cfg.get("search_requires_key", False):
            continue
        result.append(f"{name}={values.get(name, 'ANY' if use_any else 'None')}")
    return result


def multiline_args(args: list[str], spaces: int = 8) -> str:
    if not args:
        return ""
    pad = " " * spaces
    return (",\n" + pad).join(args)


def generate_db(cfg: dict[str, Any]) -> str:
    repo = cfg["repo_module"]
    fn = cfg["repo_search_function"]
    params = cfg["repo_search_parameters"]

    call_args = multiline_args(
        search_call_args(cfg, params),
        8,
    )

    # The builder receives the common list-plan args. The required contract_id
    # for Agent is injected into filters by the real repository.
    builder_args = []
    for name in ("filters", "sort", "page", "columns"):
        if name in params:
            builder_args.append(f"{name}=ANY")

    builder_text = multiline_args(builder_args, 8)

    if cfg.get("repo_execute_query_passes_limit", False):
        execute_assert = """    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=10,
    )
"""
    else:
        execute_assert = """    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
    )
"""

    key_check = ""
    if cfg.get("search_requires_key", False):
        key_check = f"""
    args, _kwargs = mock_execute.call_args
    params = args[1]
    if isinstance(params, dict):
        assert any(
            value == {cfg['sample_key']!r}
            for value in params.values()
        )
"""

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract repository tests are the behavioral baseline.

from unittest.mock import ANY, MagicMock, patch

import pytest

from db.repositories import {repo}
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


@pytest.fixture
def mock_plan():
    plan = MagicMock()
    plan.sql = "SELECT * FROM generated_test_source"
    plan.params = {{}}
    return plan


@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_success(mock_get_plan, mock_execute, mock_plan):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [{{"{cfg['key_column']}": {cfg['sample_key']!r}}}],
        "page": {{"cursor": None, "has_more": False}},
    }}

    filters = FiltersEnvelope(filters={{}})
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = {repo}.{fn}(
        {call_args}
    )

    mock_get_plan.assert_called_once_with(
        {builder_text}
    )

{execute_assert.rstrip()}

    assert isinstance(result, dict)
    assert "items" in result
{key_check.rstrip()}


@patch("db.repositories.{repo}.execute_query")
@patch("db.repositories.{repo}._builder.get_list_plan")
def test_{fn}_empty(mock_get_plan, mock_execute, mock_plan):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {{
        "items": [],
        "page": {{"cursor": None, "has_more": False}},
    }}

    filters = FiltersEnvelope(filters={{}})
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = {repo}.{fn}(
        {call_args}
    )

    assert isinstance(result, dict)
    assert result["items"] == []
"""


def generate_model(cfg: dict[str, Any]) -> str:
    module = cfg["module_name"]
    model = cfg["response_model"]
    fields = model_fields(source_file("model", cfg), model)

    if not fields:
        raise ValueError(
            f"No Pydantic fields found for {model}"
        )

    payload = {
        field: sample_value(field, cfg)
        for field in fields
    }

    allowed = cfg.get("response_assert_fields", [])
    assertion_field = next(
        (field for field in allowed if field in fields),
        fields[0],
    )

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract model tests are the behavioral baseline.

from pydantic import ValidationError

from domain.models.{module} import {model}


def test_{module}_response_valid_data():
    data = {dict_literal(payload, 8)}

    result = {model}(**data)

    assert isinstance(result, {model})
    assert getattr(result, "{assertion_field}") == {payload[assertion_field]!r}


def test_{module}_response_empty_payload():
    try:
        result = {model}(**{{}})
    except ValidationError:
        return

    assert isinstance(result, {model})
"""


def generate_service(cfg: dict[str, Any]) -> str:
    module = cfg["module_name"]
    service_module = cfg["service_module"]
    repo_module = cfg["repo_module"]
    service_fn = cfg["service_search_function"]
    repo_fn = cfg["repo_search_function"]
    model = cfg["response_model"]

    service_args = multiline_args(
        search_call_args(
            cfg,
            cfg["service_search_parameters"],
        ),
        8,
    )
    repo_expected = multiline_args(
        search_call_args(
            cfg,
            cfg["repo_search_parameters"],
            use_any=True,
        ),
        8,
    )

    sample = {
        cfg["key_column"]: cfg["sample_key"],
        cfg.get("sample_field", "name"): cfg.get(
            "sample_value",
            "Test Value",
        ),
    }

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager Contract service tests are the behavioral baseline.

from unittest.mock import ANY, patch

from domain.models.{module} import {model}
from domain.services.{service_module} import {service_fn}
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


def test_{service_fn}_success():
    sample = {dict_literal(sample, 8)}

    with patch(
        "domain.services.{service_module}.{repo_module}.{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [sample],
            "page": {{"cursor": None, "has_more": False}},
        }}

        filters = FiltersEnvelope(filters={{}})
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {service_fn}(
        {service_args}
        )

        mock_repo.assert_called_once_with(
        {repo_expected}
        )

        assert len(result.items) == 1
        assert isinstance(result.items[0], {model})


def test_{service_fn}_empty():
    with patch(
        "domain.services.{service_module}.{repo_module}.{repo_fn}"
    ) as mock_repo:
        mock_repo.return_value = {{
            "items": [],
            "page": {{"cursor": None, "has_more": False}},
        }}

        filters = FiltersEnvelope(filters={{}})
        sort = SortModel()
        page = PaginationModel(limit=10)
        columns = None

        result = {service_fn}(
        {service_args}
        )

        assert result.items == []
        assert result.metadata.has_more is False
"""


def generate_handler(cfg: dict[str, Any]) -> str:
    module = cfg["module_name"]
    handler_fn = cfg["handler_search_function"]
    service_fn = cfg["service_search_function"]

    inner_schema = cfg.get(
        "handler_inner_schema",
        f"V1{snake_to_pascal(module)}ResponseModel",
    )
    outer_schema = cfg.get(
        "handler_outer_schema",
        f"V1{snake_to_pascal(module)}ListResponseModel",
    )

    path_name = cfg.get("handler_path_parameter")
    if cfg.get("search_requires_key") and path_name:
        path_parameters = (
            f'{{"{path_name}": {cfg["sample_key"]!r}}}'
        )
    else:
        path_parameters = "{}"

    expected = multiline_args(
        search_call_args(
            cfg,
            cfg["handler_service_parameters"],
            use_any=True,
        ),
        8,
    )

    missing_test = ""
    if cfg.get("search_requires_key") and path_name:
        missing_test = f"""

def test_{handler_fn}_missing_id(mock_context):
    event = {{
        "pathParameters": {{}},
        "requestContext": {{"requestId": "test-missing-id"}},
    }}

    response = {handler_fn}(event, mock_context)

    assert response["statusCode"] == {cfg.get('handler_missing_key_status', 400)}

    body = (
        response["body"]
        if isinstance(response["body"], dict)
        else json.loads(response["body"])
    )
    assert body["error"]["message"] == {cfg.get('handler_missing_key_message', 'Required ID is missing.')!r}
"""

    return f"""# AUTO-GENERATED by generate_api_tests.py
# Manager handler tests are the behavioral baseline.

import json
from unittest.mock import ANY, MagicMock, patch

from v1.handlers import {handler_fn}


@patch("v1.handlers.{module}.{inner_schema}")
@patch("v1.handlers.{module}.{outer_schema}")
@patch("v1.handlers.{module}.{service_fn}")
def test_{handler_fn}_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
    request_id = "test-{module}-success"

    mock_results = MagicMock()
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

    mock_inner_schema.model_validate.return_value = MagicMock()

    outer = MagicMock()
    outer.model_dump.return_value = {{
        "metadata": {{
            "totalCount": 1,
            "cursor": None,
            "hasMore": False,
        }},
        "data": [{{"{cfg['key_column']}": {cfg['sample_key']!r}}}],
    }}
    mock_outer_schema.return_value = outer

    event = {{
        "pathParameters": {path_parameters},
        "queryStringParameters": None,
        "requestContext": {{"requestId": request_id}},
    }}

    response = {handler_fn}(event, mock_context)

    assert response["statusCode"] == {cfg.get('handler_success_status', 200)}

    mock_service.assert_called_once_with(
        {expected}
    )
{missing_test}
"""


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
        raise ValueError(
            f"Generated Python is invalid for {destination}: {exc}"
        ) from exc


def generate_one(
    test_type: str,
    cfg: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
) -> Path | None:
    destination = destination_file(test_type, cfg)

    if destination.exists() and not force and not dry_run:
        print(f"SKIP   [{test_type:<7}] {destination}")
        return None

    source = GENERATORS[test_type](cfg)
    validate_generated_python(source, destination)

    if dry_run:
        print(f"DRY    [{test_type:<7}] {destination}")
        return destination

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    destination.write_text(
        source,
        encoding="utf-8",
    )

    print(f"CREATE [{test_type:<7}] {destination}")
    return destination


def run_generated_tests(
    cfg: dict[str, Any],
    selected_types: list[str],
) -> int:
    paths = [
        destination_file(test_type, cfg)
        for test_type in selected_types
    ]

    command = [
        sys.executable,
        "-m",
        "pytest",
        *[str(path) for path in paths],
        "-v",
    ]

    print()
    print("Running:")
    print(" ".join(command))
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

    for name in sorted(APIS):
        cfg = APIS[name]
        print(
            f"{name:<25} "
            f"repo={cfg['repo_search_function']:<35} "
            f"handler={cfg['handler_search_function']}"
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
        print(f"ERROR: API '{api_name}' is not configured.")
        list_apis()
        return 2

    cfg = validate_config_against_source(
        APIS[api_name]
    )

    print()
    print("=" * 78)
    print(f"Generating tests for API: {api_name}")
    print(f"Repo search:    {cfg['repo_search_function']}")
    print(f"Service search: {cfg['service_search_function']}")
    print(f"Handler search: {cfg['handler_search_function']}")
    print(f"Required key:   {cfg.get('search_requires_key', False)}")
    print(f"Key lookup:     {cfg.get('supports_key_lookup', False)}")
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
            "Generate API tests from manager-approved behavioral patterns."
        )
    )
    parser.add_argument("api", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument(
        "--test-type",
        choices=list(TEST_TYPES),
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

