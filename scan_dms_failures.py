"""
Repository for materialized view: irc_census_report_mv
"""

from typing import List, Optional, Union

from core import config
from db.builders.base_builder import BaseRepositoryBuilder
from db.builders.pypika_builder import QuerySpec, encode_cursor
from db.connection import execute_query
from v1.schemas import (
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ============================================================
# QUERY SPEC
# ============================================================

IRCCENSUSREPORT_VIEW_SPEC = QuerySpec(
    table="irc_census_report_mv",

    column_map={
        "row_id": {
            "col": "row_id",
            "type": "int",
        },
        "my_id": {
            "col": "MY_ID",
            "type": "text",
        },
        "last_first_name": {
            "col": "LAST_FIRST_NAME",
            "type": "text",
        },
        "prir_name": {
            "col": "PRIR_NAME",
            "type": "text",
        },
        "s_empl_status_cd": {
            "col": "S_EMPL_STATUS_CD",
            "type": "text",
        },
        "hire_dt": {
            "col": "HIRE_DT",
            "type": "date",
        },
        "reh_dt": {
            "col": "REH_DT",
            "type": "date",
        },
        "term_dt": {
            "col": "TERM_DT",
            "type": "date",
        },
        "seniority_dt": {
            "col": "SENIORITY_DT",
            "type": "date",
        },
        "term_reason_cd": {
            "col": "TERM_REASON_CD",
            "type": "text",
        },
        "taxble_entity_id": {
            "col": "TAXBLE_ENTITY_ID",
            "type": "text",
        },
        "locator_cd": {
            "col": "LOCATOR_CD",
            "type": "text",
        },
        "empl_class_cd": {
            "col": "EMPL_CLASS_CD",
            "type": "text",
        },
        "pto_accrl_cd": {
            "col": "PTO_ACCRL_CD",
            "type": "text",
        },
        "bu_name": {
            "col": "BU_NAME",
            "type": "text",
        },
        "dept_num": {
            "col": "DEPT_NUM",
            "type": "text",
        },
        "detl_job_cd": {
            "col": "DETL_JOB_CD",
            "type": "text",
        },
        "title_desc": {
            "col": "TITLE_DESC",
            "type": "text",
        },
        "mgr_name": {
            "col": "MGR_NAME",
            "type": "text",
        },
    },

    # IMPORTANT:
    # Keep row_id here.
    # This is used for unique keyset/cursor pagination.
    logical_id_field="row_id",

    allowed_sort_fields={
        "row_id",
        "my_id",
        "last_first_name",
        "prir_name",
        "s_empl_status_cd",
        "hire_dt",
        "reh_dt",
        "term_dt",
        "seniority_dt",
        "term_reason_cd",
        "taxble_entity_id",
        "locator_cd",
        "empl_class_cd",
        "pto_accrl_cd",
        "bu_name",
        "dept_num",
        "detl_job_cd",
        "title_desc",
        "mgr_name",
    },

    default_select=[
        "row_id",
        "my_id",
        "last_first_name",
        "prir_name",
        "s_empl_status_cd",
        "hire_dt",
        "reh_dt",
        "term_dt",
        "seniority_dt",
        "term_reason_cd",
        "taxble_entity_id",
        "locator_cd",
        "empl_class_cd",
        "pto_accrl_cd",
        "bu_name",
        "dept_num",
        "detl_job_cd",
        "title_desc",
        "mgr_name",
    ],
)


# ============================================================
# BUILDER
# ============================================================

_builder = BaseRepositoryBuilder(
    IRCCENSUSREPORT_VIEW_SPEC
)


# ============================================================
# HELPERS
# ============================================================

def _format_paginated_response(
    items: list,
    limit: int,
) -> dict:
    """
    Process DB results into the standardized response envelope.
    """

    has_more = len(items) > limit
    next_cursor = None

    if has_more:
        items = items[:limit]

        # row_id remains the cursor because it is unique
        # and safe for keyset pagination.
        next_cursor = encode_cursor(
            items[-1].get("row_id")
        )

    for item in items:
        item.pop(
            "total_count_hidden",
            None,
        )

    return {
        "items": items,
        "page": {
            "cursor": next_cursor,
            "has_more": has_more,
        },
    }


# ============================================================
# LIST / SEARCH
# ============================================================

def get_irc_census_reports(
    filters: Optional[
        Union[
            FiltersEnvelope,
            dict,
        ]
    ] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Retrieves a list of IRC census reports.

    Supports:
        - filtering
        - sorting
        - pagination
        - selected columns
        - last_first_name filtering
    """

    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(
            filters=filters
        )
    else:
        current_filters = (
            filters
            or FiltersEnvelope(
                filters={}
            )
        )

    current_sort = (
        sort
        or SortModel()
    )

    current_page = (
        page
        or PaginationModel(
            limit=config.settings.DEFAULT_PAGE_SIZE
        )
    )

    plan = _builder.get_list_plan(
        filters=current_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
    )

    items = raw_results.get(
        "items",
        [],
    )

    return _format_paginated_response(
        items,
        current_page.limit,
    )


# ============================================================
# LOOKUP BY LAST_FIRST_NAME
# ============================================================

def get_irc_census_report_by_id(
    last_first_name: str,
    filters: Optional[
        Union[
            FiltersEnvelope,
            dict,
        ]
    ] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> dict:
    """
    Fetch IRC census report records for a specific employee.

    IMPORTANT:
    Although the existing function name is
    get_irc_census_report_by_id, the business lookup
    is performed using LAST_FIRST_NAME.

    row_id remains the pagination/cursor key.
    """

    # --------------------------------------------------------
    # Build existing filter data
    # --------------------------------------------------------

    if isinstance(
        filters,
        FiltersEnvelope,
    ):
        current_data = filters.filters
    else:
        current_data = (
            filters
            or {}
        )

    # --------------------------------------------------------
    # Inject LAST_FIRST_NAME filter
    # --------------------------------------------------------

    if isinstance(
        current_data,
        dict,
    ):
        current_data[
            "last_first_name"
        ] = FilterOps(
            eq=last_first_name
        )

    else:
        name_rule = FilterRule(
            field="last_first_name",
            ops=FilterOps(
                eq=last_first_name
            ),
        )

        current_data.filters.append(
            name_rule
        )

    # --------------------------------------------------------
    # Validate filter envelope
    # --------------------------------------------------------

    validated_filters = FiltersEnvelope(
        filters=current_data
    )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    current_page = (
        page
        or PaginationModel(
            limit=50
        )
    )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    current_sort = (
        sort
        or SortModel()
    )

    # --------------------------------------------------------
    # Build query
    # --------------------------------------------------------

    plan = _builder.get_list_plan(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    # --------------------------------------------------------
    # Execute query
    # --------------------------------------------------------

    raw_results = execute_query(
        plan.sql,
        plan.params,
    )

    items = raw_results.get(
        "items",
        [],
    )

    # --------------------------------------------------------
    # Return standardized result
    # --------------------------------------------------------

    return _format_paginated_response(
        items,
        current_page.limit,
    )
