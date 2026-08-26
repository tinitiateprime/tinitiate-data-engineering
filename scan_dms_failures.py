from typing import List, Optional, Union

from core import config
from core.logging import logger
from db.builders.base_builder import BaseRepositoryBuilder
from db.builders.pypika_builder import QuerySpec, encode_cursor
from db.connection import execute_query
from v1.schemas import (
    FilterGroup,
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


AGENT_GET_CONTRACT_LOCATIONS_SPEC = QuerySpec(
    table="gold_work_locations_vw",
    columns_map={
        "award_number": {"col": "AWARD_NUMBER", "type": "text"},
        "order_number": {"col": "ORDER_NUMBER", "type": "text"},
        "contract_id": {"col": "CONTRACT_ID", "type": "text"},
        "task_number": {"col": "TASK_NUMBER", "type": "text"},
        "places": {"col": "PLACES", "type": "text"},
        "project_name": {"col": "PROJECT_NAME", "type": "text"},
        "program_manager_name": {
            "col": "PROGRAM_MANAGER_NAME",
            "type": "text",
        },
        "status": {"col": "STATUS", "type": "text"},
    },
    logical_id_field="contract_id",
    allowed_sort_fields={
        "contract_id",
        "award_number",
        "order_number",
        "project_name",
        "status",
    },
    default_select=[
        "contract_id",
        "award_number",
        "order_number",
        "places",
        "project_name",
        "program_manager_name",
        "status",
    ],
)


# Initialize the builder for this repository
_builder = BaseRepositoryBuilder(AGENT_GET_CONTRACT_LOCATIONS_SPEC)


###############################################################################
# Helpers
###############################################################################


def _format_paginated_response(
    items: list,
    limit: int,
) -> dict:
    """
    Helper to process DB results into a standardized response envelope.

    The query may return limit + 1 rows so we can determine whether another
    page exists. The extra row is removed before returning the response.
    """
    has_more = len(items) > limit

    next_cursor = None

    if has_more:
        items = items[:limit]

        next_cursor = encode_cursor(
            items[-1].get(
                AGENT_GET_CONTRACT_LOCATIONS_SPEC.logical_id_field
            )
        )

    # Remove internal/hidden count field before returning to API consumer.
    for item in items:
        item.pop("total_count_hidden", None)

    return {
        "items": items,
        "page": {
            "cursor": next_cursor,
            "has_more": has_more,
        },
    }


def _normalize_filters(
    filters: Optional[
        Union[
            FiltersEnvelope,
            FilterGroup,
            dict,
        ]
    ],
    field_name: str,
    field_value: str,
) -> FiltersEnvelope:
    """
    Normalize the supported filter shapes into FiltersEnvelope and inject
    the required equality filter.

    Supported inputs:
        * None
        * dict
        * FilterGroup
        * FiltersEnvelope

    Existing filters are preserved.
    """

    # ------------------------------------------------------------------
    # Existing FiltersEnvelope
    # ------------------------------------------------------------------
    if isinstance(filters, FiltersEnvelope):
        current_data = filters.filters

    # ------------------------------------------------------------------
    # Direct FilterGroup
    # ------------------------------------------------------------------
    elif isinstance(filters, FilterGroup):
        current_data = filters

    # ------------------------------------------------------------------
    # Dictionary or None
    # ------------------------------------------------------------------
    else:
        current_data = filters or {}

    # ------------------------------------------------------------------
    # Dictionary-style filters
    #
    # Example:
    # {
    #     "proj_name": FilterOps(eq="Test Project")
    # }
    # ------------------------------------------------------------------
    if isinstance(current_data, dict):
        current_data[field_name] = FilterOps(eq=field_value)

    # ------------------------------------------------------------------
    # Recursive FilterGroup-style filters
    # ------------------------------------------------------------------
    elif isinstance(current_data, FilterGroup):
        id_rule = FilterRule(
            field=field_name,
            ops=FilterOps(eq=field_value),
        )

        current_data.filters.append(id_rule)

    # ------------------------------------------------------------------
    # Convert final structure into FiltersEnvelope
    # ------------------------------------------------------------------
    return FiltersEnvelope(filters=current_data)


###############################################################################
# Repository functions
###############################################################################


def get_work_locations_by_contract_id(
    contract_id: str,
    filters: Optional[
        Union[
            FiltersEnvelope,
            FilterGroup,
            dict,
        ]
    ] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> dict:
    """
    Fetch records for a specific contract_id.

    Ensures the required contract_id equality filter is injected into the
    supplied filter structure while preserving any existing filters.
    """

    validated_filters = _normalize_filters(
        filters=filters,
        field_name="contract_id",
        field_value=contract_id,
    )

    current_page = page or PaginationModel(limit=50)
    current_sort = sort or SortModel()

    plan = _builder.get_list_plan(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    # IMPORTANT:
    # execute_query needs the requested limit. The unit tests specifically
    # verify this argument.
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
    )

    items = raw_results.get("items", [])

    return _format_paginated_response(
        items,
        current_page.limit,
    )


def get_work_locations_by_contract_id_by_id(
    proj_id: str,
    filters: Optional[
        Union[
            FiltersEnvelope,
            FilterGroup,
            dict,
        ]
    ] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> dict:
    """
    Fetch work-location records for a specific project ID.

    The function name follows the existing API/repository naming convention,
    while the actual lookup field required by this endpoint is ``proj_id``.

    Existing filters are preserved and the required proj_id equality
    condition is added.
    """

    validated_filters = _normalize_filters(
        filters=filters,
        field_name="proj_id",
        field_value=proj_id,
    )

    current_page = page or PaginationModel(limit=50)
    current_sort = sort or SortModel()

    plan = _builder.get_list_plan(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    raw_results = execute_query(
        plan.sql,
        plan.params,
    )

    items = raw_results.get("items", [])

    return _format_paginated_response(
        items,
        current_page.limit,
    )
