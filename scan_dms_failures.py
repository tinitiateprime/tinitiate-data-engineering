#!/usr/bin/env python3
"""
generate_repo_stack.py

Generates the 4-layer file stack (repo -> service -> domain model -> handler)
for a materialized-view-backed entity, following the contract_repo.py /
contract_service.py / contract.py / contracts-handler pattern.

USAGE
-----
python generate_repo_stack.py --config my_view_config.json --outdir ./generated
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict


PY_TYPE_MAP = {
    "int": "int",
    "text": "str",
    "date": "date",
    "numeric": "float",
    "bool": "bool",
}

REQUIRED_KEYS = [
    "entity",
    "entity_snake",
    "entity_plural_snake",
    "materialized_view",
    "logical_id_field",
    "lookup_field",
    "route_base",
    "columns",
]


def _validate_config(config: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ValueError(f"Config missing required keys: {missing}")
    if not config["columns"]:
        raise ValueError("Config must include at least one column")
    for col in config["columns"]:
        for required_col_key in ("name", "col", "type", "alias"):
            if required_col_key not in col:
                raise ValueError(f"Column {col} missing '{required_col_key}'")
        if col["type"] not in PY_TYPE_MAP:
            raise ValueError(
                f"Column '{col['name']}' has unknown type '{col['type']}'. "
                f"Known types: {list(PY_TYPE_MAP)}"
            )


def render_repo(config: Dict[str, Any]) -> str:
    entity_upper = config["entity"].upper()
    entity_snake = config["entity_snake"]
    entity_plural_snake = config["entity_plural_snake"]
    materialized_view = config["materialized_view"]
    logical_id_field = config["logical_id_field"]
    lookup_field = config["lookup_field"]
    columns = config["columns"]

    column_map_lines = ",\n".join(
        f'        "{c["name"]}": {{"col": "{c["col"]}", "type": "{c["type"]}"}}'
        for c in columns
    )
    sort_fields = [c["name"] for c in columns if c.get("sortable", True)]
    allowed_sort_lines = ",\n".join(f'        "{f}"' for f in sort_fields)
    select_fields = [c["name"] for c in columns if c.get("selectable", True)]
    default_select_lines = ",\n".join(f'        "{f}"' for f in select_fields)

    return f'''"""
Auto-generated repository for materialized view: {materialized_view}
"""
from typing import List, Optional, Union

from core import config
from core.logging import logger
from db.builders.base_builder import BaseRepositoryBuilder
from db.builders.pypika_builder import QuerySpec, encode_cursor
from db.connection import execute_query
from v1.schemas import FilterOps, FilterRule, FiltersEnvelope, PaginationModel, SortModel


# Define the Spec targeting the materialized view
{entity_upper}_VIEW_SPEC = QuerySpec(
    table="{materialized_view}",
    column_map={{
{column_map_lines}
    }},
    # Keyset pagination requires a unique, non-nullable field.
    logical_id_field="{logical_id_field}",
    allowed_sort_fields={{
{allowed_sort_lines}
    }},
    default_select=[
{default_select_lines}
    ],
)

# Initialize the builder for this repository
_builder = BaseRepositoryBuilder({entity_upper}_VIEW_SPEC)


##############################################################################
## Helpers
##############################################################################
def _format_paginated_response(items: list, limit: int) -> dict:
    """Helper to process DB results into a standardized response envelope."""
    has_more = len(items) > limit

    next_cursor = None
    if has_more:
        items = items[:limit]
        next_cursor = encode_cursor(items[-1].get("{logical_id_field}"))

    for item in items:
        item.pop("total_count_hidden", None)

    return {{
        "items": items,
        "page": {{"cursor": next_cursor, "has_more": has_more}},
    }}


def get_{entity_plural_snake}(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Retrieves a list of {entity_plural_snake} from the view.
    Handles the POST body JSON containing filters, sort, and page config.
    """
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters or FiltersEnvelope(filters={{}})

    current_sort = sort or SortModel()
    current_page = page or PaginationModel(limit=config.settings.DEFAULT_PAGE_SIZE)

    plan = _builder.get_list_plan(
        filters=current_filters, sort=current_sort, page=current_page, columns=columns
    )

    raw_results = execute_query(plan.sql, plan.params, limit=current_page.limit)
    items = raw_results.get("items", [])

    return _format_paginated_response(items, current_page.limit)


def get_{entity_snake}_by_id(
    {lookup_field}: str,
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> dict:
    """
    Fetches records for a specific {lookup_field}.
    Ensures that manual ID filtering is injected into the recursive filter structure.
    """
    if isinstance(filters, FiltersEnvelope):
        current_data = filters.filters
    else:
        current_data = filters or {{}}

    if isinstance(current_data, dict):
        current_data["{lookup_field}"] = FilterOps(eq={lookup_field})
    else:
        id_rule = FilterRule(field="{lookup_field}", ops=FilterOps(eq={lookup_field}))
        current_data.filters.append(id_rule)

    validated_filters = FiltersEnvelope(filters=current_data)

    current_page = page or PaginationModel(limit=50)
    current_sort = sort or SortModel()

    plan = _builder.get_list_plan(
        filters=validated_filters, sort=current_sort, page=current_page, columns=columns
    )

    raw_results = execute_query(plan.sql, plan.params)
    items = raw_results.get("items", [])

    return _format_paginated_response(items, current_page.limit)
'''


def render_service(config: Dict[str, Any]) -> str:
    entity = config["entity"]
    entity_snake = config["entity_snake"]
    entity_plural_snake = config["entity_plural_snake"]
    lookup_field = config["lookup_field"]
    default_sort_field = config.get("default_sort_field", config["lookup_field"])

    return f'''"""
Auto-generated service layer for {entity}
"""
from typing import List, Optional, Union

from core.config import settings
from core.filters import FiltersEnvelope, SortModel
from core.pagination import DEFAULT_PAGE_SIZE, PaginationModel
from db.repositories import {entity_snake}_repo
from domain.models import {entity}Response, {entity}SearchServiceResponse
from domain.models.metadata import MetadataModel


def search_{entity_plural_snake}(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> {entity}SearchServiceResponse:
    """
    Orchestrates the transformation of API inputs into domain objects.
    """
    current_page = page or PaginationModel(limit=DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="{default_sort_field}", order="asc")

    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(filters=filters)
    elif filters is None:
        validated_filters = FiltersEnvelope(filters={{}})
    else:
        validated_filters = filters

    db_result = {entity_snake}_repo.get_{entity_plural_snake}(
        filters=validated_filters, sort=current_sort, page=current_page, columns=columns
    )

    items = [
        {entity}Response.model_validate(item) for item in db_result.get("items", [])
    ]

    return {entity}SearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result["page"].get("cursor"),
            has_more=db_result["page"].get("has_more"),
            applied_filters=validated_filters if validated_filters.filters else None,
        ),
    )


def get_{entity_snake}_details(
    {lookup_field}: str,
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    limit: int = settings.DEFAULT_PAGE_SIZE,
    cursor: Optional[str] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> {entity}SearchServiceResponse:
    if not {lookup_field}:
        return {entity}SearchServiceResponse(
            items=[],
            metadata=MetadataModel(cursor=None, has_more=False, applied_filters=None),
        )

    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(filters=filters)
    elif filters is None:
        validated_filters = FiltersEnvelope(filters={{}})
    else:
        validated_filters = filters

    page = PaginationModel(limit=limit, cursor=cursor)

    db_result = {entity_snake}_repo.get_{entity_snake}_by_id(
        {lookup_field}={lookup_field},
        filters=validated_filters,
        page=page,
        columns=columns,
        sort=sort,
    )

    items = [
        {entity}Response.model_validate(item) for item in db_result.get("items", [])
    ]

    return {entity}SearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result["page"].get("cursor"),
            has_more=db_result["page"].get("has_more", False),
            applied_filters=validated_filters if validated_filters.filters else None,
        ),
    )
'''


def render_model(config: Dict[str, Any]) -> str:
    entity = config["entity"]
    columns = config["columns"]
    needs_date = any(c["type"] == "date" for c in columns)

    field_lines = []
    for c in columns:
        py_type = PY_TYPE_MAP[c["type"]]
        required = c.get("required", True)
        default = c.get("default")
        alias = c["alias"]
        name = c["name"]

        if required:
            field_lines.append(f'    {name}: {py_type} = Field(..., alias="{alias}")')
        else:
            if default is not None:
                annotation = py_type
                default_literal = default
            else:
                annotation = f"Optional[{py_type}]"
                default_literal = "None"
            field_lines.append(
                f'    {name}: {annotation} = Field({default_literal}, alias="{alias}")'
            )

    fields_block = "\n".join(field_lines)
    date_import = "from datetime import date\n" if needs_date else ""

    return f'''"""
Auto-generated domain model for {entity}
"""
{date_import}from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .metadata import MetadataModel


class {entity}Response(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

{fields_block}


class {entity}SearchServiceResponse(BaseModel):
    """
    Internal domain-level response.
    Decoupled from V1/V2 specific JSON envelopes.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[{entity}Response]
    metadata: MetadataModel
'''


def render_handler(config: Dict[str, Any]) -> str:
    entity = config["entity"]
    entity_snake = config["entity_snake"]
    entity_plural_snake = config["entity_plural_snake"]
    lookup_field = config["lookup_field"]
    route_base = config["route_base"].rstrip("/")
    filter_context_name = f"{entity.upper()}_FILTER_CONTEXT"

    return f'''"""
Auto-generated V1 handler routes for {entity}
"""
import json

from core.config import settings
from core.exceptions import ResourceNotFoundError
from core.filters import (
    FiltersEnvelope,
    SortModel,
    parse_filters_from_query_params,
)
from core.pagination import PaginationModel
from core.responses import api_handler
from core.utils import LambdaUtils
from domain.services import get_{entity_snake}_details, search_{entity_plural_snake}
from v1.logic import router
from v1.schemas.{entity_snake}s import (
    {filter_context_name},
    V1{entity}DetailResponseModel,
    V1{entity}ListResponseModel,
    V1{entity}ResponseModel,
    V1MetadataModel,
)


@router.route("GET", r"{route_base}/(?P<{lookup_field}>[^/]+)", is_regex=True)
@api_handler
def get_{entity_snake}_v1(event, context):
    {lookup_field} = LambdaUtils.get_path_param(event, "{lookup_field}")

    if not {lookup_field}:
        raise ValueError("{entity} ID is required.")

    query_params = LambdaUtils.get_all_query_params(event)
    limit = int(query_params.get("limit", settings.DEFAULT_PAGE_SIZE))
    cursor = query_params.get("cursor")
    columns = LambdaUtils.get_columns_query_parameter(event)

    filters_envelope = parse_filters_from_query_params(
        query_params, {filter_context_name}
    )

    results = get_{entity_snake}_details(
        {lookup_field}={lookup_field},
        filters=filters_envelope,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    if not results.items:
        raise ResourceNotFoundError(
            message=f"{entity} with ID {{{lookup_field}}} not found",
            details={{"{lookup_field}": {lookup_field}}},
        )

    results.metadata.applied_filters = filters_envelope

    response = V1{entity}DetailResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[V1{entity}ResponseModel.model_validate(item) for item in results.items],
    )

    return response.model_dump(by_alias=True)


@router.route("POST", r"{route_base}/search", is_regex=False)
@api_handler
def search_{entity_plural_snake}_v1(event, context):
    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    filters_data = body.get("filters", {{}})
    sort = SortModel(**body.get("sort", {{}}))
    page = PaginationModel(**body.get("page", {{}}))
    columns = LambdaUtils.get_columns_query_parameter(event)

    results = search_{entity_plural_snake}(
        filters=filters_data, sort=sort, page=page, columns=columns
    )

    results.metadata.applied_filters = FiltersEnvelope(filters=filters_data)

    response = V1{entity}ListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[V1{entity}ResponseModel.model_validate(item) for item in results.items],
    )

    return response.model_dump(by_alias=True)


@router.route("GET", r"{route_base}", is_regex=False)
@api_handler
def list_{entity_plural_snake}_v1(event, context):
    query_params = LambdaUtils.get_all_query_params(event)
    limit = int(query_params.get("limit", settings.DEFAULT_PAGE_SIZE))
    cursor = query_params.get("cursor")

    filters_envelope = parse_filters_from_query_params(
        query_params, {filter_context_name}
    )

    results = search_{entity_plural_snake}(
        filters=filters_envelope,
        page=PaginationModel(limit=limit, cursor=cursor),
    )

    results.metadata.applied_filters = filters_envelope

    response = V1{entity}ListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[V1{entity}ResponseModel.model_validate(item) for item in results.items],
    )

    return response.model_dump(by_alias=True)
'''


def generate(config: Dict[str, Any], outdir: str) -> Dict[str, str]:
    _validate_config(config)
    os.makedirs(outdir, exist_ok=True)
    entity_snake = config["entity_snake"]

    files = {
        f"{entity_snake}_repo.py": render_repo(config),
        f"{entity_snake}_service.py": render_service(config),
        f"{entity_snake}_model.py": render_model(config),
        f"{entity_snake}_handler.py": render_handler(config),
    }

    written = {}
    for filename, content in files.items():
        path = os.path.join(outdir, filename)
        with open(path, "w") as f:
            f.write(content)
        written[filename] = path

    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Path to a JSON config file")
    parser.add_argument("--outdir", default="./generated", help="Directory to write generated files to")
    args = parser.parse_args()

    if not args.config:
        parser.error("Provide --config <file.json>")
        return

    with open(args.config) as f:
        config = json.load(f)

    written = generate(config, args.outdir)
    print("Generated files:")
    for filename, path in written.items():
        print(f"  {filename} -> {path}")


if __name__ == "__main__":
    main()
