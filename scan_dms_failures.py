#!/usr/bin/env python3
"""
generate_repo_stack.py

Generates the 4-layer file stack (repo -> service -> domain model -> handler)
for a new materialized view / mat view-backed entity, following the same
pattern as the existing contract_repo.py / contract_service.py / contract.py /
contracts handler files.

USAGE
-----
1. Fill in a config dict (see EXAMPLE_CONFIG below for the shape) describing
   your new view: table name, entity name, columns, id fields, sort fields.

2. Run:
     python generate_repo_stack.py --config my_view_config.json --outdir ./generated

   or, to see it work immediately with the bundled example:
     python generate_repo_stack.py --example --outdir ./generated

3. Four files land in --outdir:
     <entity>_repo.py       (db/repositories layer)
     <entity>_service.py    (domain/services layer)
     <entity>_model.py      (domain/models layer)
     <entity>_handler.py    (v1 route handlers + v1 schemas)

You can also import this module and call `generate(config, outdir)` directly
from other tooling.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Type mapping: your "type" strings -> Python annotation used in the domain
# model. Extend this if you introduce new column types.
# ---------------------------------------------------------------------------
PY_TYPE_MAP = {
    "int": "int",
    "text": "str",
    "date": "date",
    "numeric": "float",
    "bool": "bool",
}


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------
REQUIRED_KEYS = [
    "entity",               # PascalCase singular, e.g. "Project"
    "entity_snake",         # snake_case singular, e.g. "project"
    "entity_plural_snake",  # snake_case plural, e.g. "projects"
    "materialized_view",    # e.g. "gold.project_active_mv"
    "logical_id_field",     # unique non-nullable field for keyset pagination, e.g. "row_id"
    "lookup_field",         # business key used in get_by_id, e.g. "project_id"
    "route_base",           # e.g. "/v1/projects"
    "columns",              # list of column dicts (see below)
]

# Each column dict:
# {
#   "name": "project_id",     # python attr / column_map key (snake_case)
#   "col": "project_id",      # actual DB column name (usually same as name)
#   "type": "text",           # one of PY_TYPE_MAP keys
#   "alias": "projectId",     # camelCase JSON alias for pydantic Field
#   "required": True,         # whether it's a required field (no default)
#   "default": None,          # python-literal-as-string default, e.g. '"Y"' or "0"
#   "sortable": True,         # whether to include in allowed_sort_fields
#   "selectable": True,       # whether to include in default_select
# }


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


# ---------------------------------------------------------------------------
# Repository layer (stage 1)
# ---------------------------------------------------------------------------
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
    # 1. Normalize Inputs
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters or FiltersEnvelope(filters={{}})

    current_sort = sort or SortModel()
    current_page = page or PaginationModel(limit=config.settings.DEFAULT_PAGE_SIZE)

    # 2. Generate Plan (the builder handles the recursive AND/OR logic)
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
    # 1. Extract raw filter dictionary for modification
    if isinstance(filters, FiltersEnvelope):
        # We need to peek into the 'filters' attribute of the envelope
        current_data = filters.filters
    else:
        current_data = filters or {{}}

    # 2. Inject {lookup_field} filter
    if isinstance(current_data, dict):
        # Explicitly wrap the dict in a FilterOps instance
        current_data["{lookup_field}"] = FilterOps(eq={lookup_field})
    else:
        # If the root is a FilterGroup, we append a new FilterRule
        id_rule = FilterRule(field="{lookup_field}", ops=FilterOps(eq={lookup_field}))
        current_data.filters.append(id_rule)

    validated_filters = FiltersEnvelope(filters=current_data)

    # 3. Defaults
    current_page = page or PaginationModel(limit=50)
    current_sort = sort or SortModel()

    # 4. Plan & Execute
    plan = _builder.get_list_plan(
        filters=validated_filters, sort=current_sort, page=current_page, columns=columns
    )

    raw_results = execute_query(plan.sql, plan.params)
    items = raw_results.get("items", [])

    return _format_paginated_response(items, current_page.limit)
'''


# ---------------------------------------------------------------------------
# Service layer (stage 2)
# ---------------------------------------------------------------------------
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
    # 1. Normalize Models (defaults if not provided in POST body)
    current_page = page or PaginationModel(limit=DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="{default_sort_field}", order="asc")

    # 2. Normalize filters to ensure we have a FiltersEnvelope object
    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(filters=filters)
    elif filters is None:
        validated_filters = FiltersEnvelope(filters={{}})
    else:
        validated_filters = filters

    # 3. Call Repository
    db_result = {entity_snake}_repo.get_{entity_plural_snake}(
        filters=validated_filters, sort=current_sort, page=current_page, columns=columns
    )

    # 4. Transform to Domain Objects
    items = [
        {entity}Response.model_validate(item) for item in db_result.get("items", [])
    ]

    # 5. Return Pydantic Model
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
    # 1. Early Return for invalid IDs
    if not {lookup_field}:
        return {entity}SearchServiceResponse(
            items=[],
            metadata=MetadataModel(
                cursor=None,
                has_more=False,
                applied_filters=None,
            ),
        )

    # 2. Normalize filters to ensure we have a FiltersEnvelope object
    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(filters=filters)
    elif filters is None:
        validated_filters = FiltersEnvelope(filters={{}})
    else:
        validated_filters = filters

    # Package the raw limit and cursor into the PaginationModel the repo expects
    page = PaginationModel(limit=limit, cursor=cursor)

    # 3. Call Repo
    db_result = {entity_snake}_repo.get_{entity_snake}_by_id(
        {lookup_field}={lookup_field},
        filters=validated_filters,
        page=page,
        columns=columns,
        sort=sort,
    )

    # 4. Transform & Validate
    items = [
        {entity}Response.model_validate(item) for item in db_result.get("items", [])
    ]

    # 5. Wrap and Return (ensures consistency with search_{entity_plural_snake})
    return {entity}SearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result["page"].get("cursor"),
            has_more=db_result["page"].get("has_more", False),
            applied_filters=validated_filters if validated_filters.filters else None,
        ),
    )
'''


# ---------------------------------------------------------------------------
# Domain model layer (stage 3)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Handler / route layer (stage 4) — includes the v1 schema wrapper models
# ---------------------------------------------------------------------------
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

    # Quick exit: required parameter is missing for this route
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


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def generate(config: Dict[str, Any], outdir: str) -> Dict[str, str]:
    """
    Generates all 4 files for the given config and writes them to outdir.
    Returns a dict of {filename: filepath} for the files written.
    """
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


# ---------------------------------------------------------------------------
# Bundled example config (mirrors the "contracts" pattern you already have)
# ---------------------------------------------------------------------------
EXAMPLE_CONFIG: Dict[str, Any] = {
    "entity": "Project",
    "entity_snake": "project",
    "entity_plural_snake": "projects",
    "materialized_view": "gold.project_active_mv",
    "logical_id_field": "row_id",
    "lookup_field": "project_id",
    "default_sort_field": "project_id",
    "route_base": "/v1/projects",
    "columns": [
        {"name": "row_id", "col": "row_id", "type": "int", "alias": "rowId", "required": True, "sortable": True, "selectable": True},
        {"name": "project_id", "col": "project_id", "type": "text", "alias": "projectId", "required": True, "sortable": True, "selectable": True},
        {"name": "project_name", "col": "project_name", "type": "text", "alias": "projectName", "required": True, "sortable": True, "selectable": True},
        {"name": "active_fl", "col": "active_fl", "type": "text", "alias": "activeFl", "required": False, "default": '"Y"', "sortable": False, "selectable": True},
        {"name": "created_date", "col": "created_date", "type": "date", "alias": "createdDate", "required": False, "sortable": True, "selectable": True},
        {"name": "total_value", "col": "total_value", "type": "numeric", "alias": "totalValue", "required": False, "sortable": True, "selectable": True},
    ],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Path to a JSON config file")
    parser.add_argument("--example", action="store_true", help="Use the bundled example config instead of --config")
    parser.add_argument("--outdir", default="./generated", help="Directory to write generated files to")
    args = parser.parse_args()

    if args.example:
        config = EXAMPLE_CONFIG
    elif args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        parser.error("Provide either --config <file.json> or --example")
        return

    written = generate(config, args.outdir)
    print("Generated files:")
    for filename, path in written.items():
        print(f"  {filename} -> {path}")


if __name__ == "__main__":
    main()

{
  "_comment_entity": "PascalCase singular name for the entity, e.g. 'Project', 'PurchaseOrder'",
  "entity": "REPLACE_ME_Entity",

  "_comment_entity_snake": "snake_case singular, e.g. 'project', 'purchase_order'",
  "entity_snake": "replace_me_entity",

  "_comment_entity_plural_snake": "snake_case plural, e.g. 'projects', 'purchase_orders'",
  "entity_plural_snake": "replace_me_entities",

  "_comment_materialized_view": "the materialized view name as it appears in the DB, e.g. 'gold.project_active_mv'",
  "materialized_view": "gold.REPLACE_ME_mv",

  "_comment_logical_id_field": "a unique, non-nullable field used for keyset pagination (usually a surrogate row id)",
  "logical_id_field": "row_id",

  "_comment_lookup_field": "the business key used for the get-by-id endpoint, e.g. 'project_id'",
  "lookup_field": "replace_me_id",

  "_comment_default_sort_field": "field used as the default sort when none is provided",
  "default_sort_field": "replace_me_id",

  "_comment_route_base": "the base API route for this entity, e.g. '/v1/projects'",
  "route_base": "/v1/replace_me_entities",

  "_comment_columns": "one entry per column exposed via the view. type must be one of: int, text, date, numeric, bool. 'required' controls whether the pydantic Field has a default. 'default' (optional) is a python-literal string, e.g. '\"Y\"' or '0', used only when required=false. 'sortable' controls inclusion in allowed_sort_fields. 'selectable' controls inclusion in default_select.",
  "columns": [
    {
      "name": "row_id",
      "col": "row_id",
      "type": "int",
      "alias": "rowId",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "replace_me_id",
      "col": "replace_me_id",
      "type": "text",
      "alias": "replaceMeId",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "replace_me_name",
      "col": "replace_me_name",
      "type": "text",
      "alias": "replaceMeName",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "active_fl",
      "col": "active_fl",
      "type": "text",
      "alias": "activeFl",
      "required": false,
      "default": "\"Y\"",
      "sortable": false,
      "selectable": true
    },
    {
      "name": "created_date",
      "col": "created_date",
      "type": "date",
      "alias": "createdDate",
      "required": false,
      "sortable": true,
      "selectable": true
    }
  ]
}

