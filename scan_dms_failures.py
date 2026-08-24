"""
Unit tests for db.repositories.project_forecasts.
"""

from unittest.mock import MagicMock, patch

import pytest

from v1.schemas import (
    FilterOps,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)

from db.repositories import project_forecasts


# =============================================================================
# TEST DATA
# =============================================================================


def _forecast(
    row_id=1,
    proj_id="P-1001",
    lvl_no=1,
    cust_name="ABC Customer",
    proj_name="Project Alpha",
    proj_type_dc="FIXED_PRICE",
    reporting_category="ACTIVE",
    prime_contr_id="PRIME-001",
    org_id="ORG-001",
    active_fl="Y",
    proj_mgr_name="John Smith",
    proj_start_dt="2020-01-01",
    proj_end_dt="2026-12-31",
    value_total_amount=1000000.0,
    project_value_cost=800000.0,
    project_value_fee=200000.0,
    proj_f_tot_amt=900000.0,
    cost_funded=700000.0,
    fee_funded=150000.0,
    total_billed=500000.0,
    billed_cost=400000.0,
    billed_fee=100000.0,
    open_billing_detail_amt=50000.0,
    open_commit_amt=300000.0,
    eac=950000.0,
    etc=450000.0,
    date_75_expended="2025-01-01",
    date_100_expended="2026-01-01",
    forecast_by_period=None,
):
    """
    Create a representative project forecast row.
    """
    return {
        "row_id": row_id,
        "proj_id": proj_id,
        "lvl_no": lvl_no,
        "cust_name": cust_name,
        "proj_name": proj_name,
        "proj_type_dc": proj_type_dc,
        "reporting_category": reporting_category,
        "prime_contr_id": prime_contr_id,
        "org_id": org_id,
        "active_fl": active_fl,
        "proj_mgr_name": proj_mgr_name,
        "proj_start_dt": proj_start_dt,
        "proj_end_dt": proj_end_dt,
        "value_total_amount": value_total_amount,
        "project_value_cost": project_value_cost,
        "project_value_fee": project_value_fee,
        "proj_f_tot_amt": proj_f_tot_amt,
        "cost_funded": cost_funded,
        "fee_funded": fee_funded,
        "total_billed": total_billed,
        "billed_cost": billed_cost,
        "billed_fee": billed_fee,
        "open_billing_detail_amt": open_billing_detail_amt,
        "open_commit_amt": open_commit_amt,
        "eac": eac,
        "etc": etc,
        "date_75_expended": date_75_expended,
        "date_100_expended": date_100_expended,
        "forecast_by_period": forecast_by_period,
    }


# =============================================================================
# QUERY SPEC TESTS
# =============================================================================


def test_project_forecasts_view_spec():
    """
    Verify the project forecast QuerySpec configuration.
    """
    spec = project_forecasts.PROJECT_FORECASTS_VIEW_SPEC

    assert spec is not None

    assert spec.table == "gold.project_forecasts_vw"

    assert spec.use_array_any is False

    assert spec.logical_id_field == "row_id"

    assert "row_id" in spec.column_map
    assert "proj_id" in spec.column_map
    assert "lvl_no" in spec.column_map
    assert "proj_name" in spec.column_map
    assert "forecast_by_period" in spec.column_map

    assert spec.column_map["row_id"]["col"] == "row_id"
    assert spec.column_map["row_id"]["type"] == "int"

    assert spec.column_map["proj_id"]["col"] == "proj_id"
    assert spec.column_map["proj_id"]["type"] == "text"

    assert spec.column_map["lvl_no"]["type"] == "int"

    assert spec.column_map["proj_start_dt"]["type"] == "date"
    assert spec.column_map["proj_end_dt"]["type"] == "date"

    assert spec.column_map["value_total_amount"]["type"] == "numeric"
    assert spec.column_map["project_value_cost"]["type"] == "numeric"
    assert spec.column_map["project_value_fee"]["type"] == "numeric"

    assert "row_id" in spec.allowed_sort_fields
    assert "proj_id" in spec.allowed_sort_fields
    assert "lvl_no" in spec.allowed_sort_fields
    assert "proj_name" in spec.allowed_sort_fields
    assert "prime_contr_id" in spec.allowed_sort_fields
    assert "proj_mgr_name" in spec.allowed_sort_fields
    assert "value_total_amount" in spec.allowed_sort_fields
    assert "proj_f_tot_amt" in spec.allowed_sort_fields
    assert "total_billed" in spec.allowed_sort_fields
    assert "open_commit_amt" in spec.allowed_sort_fields
    assert "eac" in spec.allowed_sort_fields
    assert "etc" in spec.allowed_sort_fields

    assert "row_id" in spec.default_select
    assert "proj_id" in spec.default_select
    assert "lvl_no" in spec.default_select
    assert "cust_name" in spec.default_select
    assert "proj_name" in spec.default_select
    assert "forecast_by_period" in spec.default_select


def test_builder_exists():
    """
    Repository should initialize its BaseRepositoryBuilder.
    """
    assert project_forecasts._builder is not None


# =============================================================================
# _format_paginated_response TESTS
# =============================================================================


def test_format_paginated_response_empty():
    """
    Empty results should return no cursor and has_more=False.
    """
    result = project_forecasts._format_paginated_response(
        items=[],
        limit=10,
    )

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


def test_format_paginated_response_less_than_limit():
    """
    Results below the requested limit should not have another page.
    """
    items = [
        _forecast(row_id=1, proj_id="P-1001"),
        _forecast(row_id=2, proj_id="P-1002"),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 2
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_format_paginated_response_exact_limit():
    """
    Exactly limit rows should not indicate has_more because the repository
    determines has_more only when more than limit rows are returned.
    """
    items = [
        _forecast(row_id=1, proj_id="P-1001"),
        _forecast(row_id=2, proj_id="P-1002"),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=2,
    )

    assert len(result["items"]) == 2
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_format_paginated_response_has_more():
    """
    limit + 1 rows should be reduced to limit and return a next cursor.
    """
    items = [
        _forecast(row_id=1, proj_id="P-1001"),
        _forecast(row_id=2, proj_id="P-1002"),
        _forecast(row_id=3, proj_id="P-1003"),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=2,
    )

    assert len(result["items"]) == 2
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] is not None


def test_format_paginated_response_removes_total_count_hidden():
    """
    Internal total_count_hidden should not be returned to API consumers.
    """
    items = [
        {
            **_forecast(row_id=1),
            "total_count_hidden": 100,
        }
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert "total_count_hidden" not in result["items"][0]


def test_format_paginated_response_removes_total_count_hidden_multiple():
    """
    Internal total_count_hidden must be removed from every returned row.
    """
    items = [
        {
            **_forecast(row_id=1, proj_id="P-1001"),
            "total_count_hidden": 2,
        },
        {
            **_forecast(row_id=2, proj_id="P-1002"),
            "total_count_hidden": 2,
        },
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 2

    for item in result["items"]:
        assert "total_count_hidden" not in item


# =============================================================================
# get_project_forecasts TEST HELPERS
# =============================================================================


def _mock_plan():
    """
    Create a query plan matching BaseRepositoryBuilder output.
    """
    plan = MagicMock()

    plan.sql = """
        SELECT *
        FROM gold.project_forecasts_vw
    """

    plan.params = []

    return plan


# =============================================================================
# get_project_forecasts BASIC TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_defaults(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Repository should create default filters, sort and pagination objects.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(),
        ]
    }

    result = project_forecasts.get_project_forecasts()

    assert result is not None
    assert "items" in result
    assert "page" in result
    assert len(result["items"]) == 1

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()

    builder_call = mock_get_list_plan.call_args

    assert isinstance(
        builder_call.kwargs["filters"],
        FiltersEnvelope,
    )

    assert isinstance(
        builder_call.kwargs["sort"],
        SortModel,
    )

    assert isinstance(
        builder_call.kwargs["page"],
        PaginationModel,
    )

    assert builder_call.kwargs["columns"] is None


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_empty(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Empty database results should return a valid empty page response.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [],
    }

    result = project_forecasts.get_project_forecasts()

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


# =============================================================================
# FILTER TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    A dict of FilterOps should be converted into FiltersEnvelope.

    IMPORTANT:
    FiltersEnvelope does not accept:
        {"proj_id": "P-1001"}

    It requires a FilterOps object:
        {"proj_id": FilterOps(eq="P-1001")}
    """

    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(
                row_id=1,
                proj_id="P-1001",
            )
        ]
    }

    filters = {
        "proj_id": FilterOps(
            eq="P-1001",
        )
    }

    result = project_forecasts.get_project_forecasts(
        filters=filters,
    )

    assert result is not None
    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"

    mock_get_list_plan.assert_called_once()

    builder_call = mock_get_list_plan.call_args

    current_filters = builder_call.kwargs["filters"]

    assert isinstance(
        current_filters,
        FiltersEnvelope,
    )


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_filters_envelope(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Existing FiltersEnvelope should be passed directly to the builder.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(),
        ]
    }

    filters = FiltersEnvelope(
        filters={
            "proj_id": FilterOps(
                eq="P-1001",
            )
        }
    )

    result = project_forecasts.get_project_forecasts(
        filters=filters,
    )

    assert len(result["items"]) == 1

    mock_get_list_plan.assert_called_once()

    builder_call = mock_get_list_plan.call_args

    assert builder_call.kwargs["filters"] is filters


# =============================================================================
# SORT TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_custom_sort(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Custom sorting should be forwarded to the repository builder.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(),
        ]
    }

    sort = SortModel(
        field="proj_name",
        order="asc",
    )

    result = project_forecasts.get_project_forecasts(
        sort=sort,
    )

    assert len(result["items"]) == 1

    builder_call = mock_get_list_plan.call_args

    assert builder_call.kwargs["sort"] is sort


# =============================================================================
# PAGINATION TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_custom_page(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Custom pagination should be forwarded to the builder and execute_query.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(),
        ]
    }

    page = PaginationModel(
        limit=5,
    )

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 1

    builder_call = mock_get_list_plan.call_args

    assert builder_call.kwargs["page"] is page

    mock_execute_query.assert_called_once()

    execute_call = mock_execute_query.call_args

    assert execute_call.kwargs["limit"] == 5


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_has_more(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Database returning limit + 1 rows should create a continuation cursor.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(
                row_id=1,
                proj_id="P-1001",
            ),
            _forecast(
                row_id=2,
                proj_id="P-1002",
            ),
            _forecast(
                row_id=3,
                proj_id="P-1003",
            ),
        ]
    }

    page = PaginationModel(
        limit=2,
    )

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 2
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] is not None


# =============================================================================
# COLUMN TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_columns(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Requested columns should be forwarded to the builder.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            {
                "row_id": 1,
                "proj_id": "P-1001",
                "proj_name": "Project Alpha",
            }
        ]
    }

    columns = [
        "row_id",
        "proj_id",
        "proj_name",
    ]

    result = project_forecasts.get_project_forecasts(
        columns=columns,
    )

    assert len(result["items"]) == 1

    builder_call = mock_get_list_plan.call_args

    assert builder_call.kwargs["columns"] == columns


# =============================================================================
# COMBINED ARGUMENT TEST
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_all_arguments(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Filters, sorting, pagination and requested columns should work together.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(
                row_id=10,
                proj_id="P-1001",
                proj_name="Project Alpha",
            )
        ]
    }

    filters = FiltersEnvelope(
        filters={
            "proj_id": FilterOps(
                eq="P-1001",
            )
        }
    )

    sort = SortModel(
        field="proj_name",
        order="asc",
    )

    page = PaginationModel(
        limit=10,
    )

    columns = [
        "row_id",
        "proj_id",
        "proj_name",
    ]

    result = project_forecasts.get_project_forecasts(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )

    assert result is not None
    assert len(result["items"]) == 1

    builder_call = mock_get_list_plan.call_args

    assert builder_call.kwargs["filters"] is filters
    assert builder_call.kwargs["sort"] is sort
    assert builder_call.kwargs["page"] is page
    assert builder_call.kwargs["columns"] == columns

    execute_call = mock_execute_query.call_args

    assert execute_call.args[0] == mock_get_list_plan.return_value.sql
    assert execute_call.args[1] == mock_get_list_plan.return_value.params
    assert execute_call.kwargs["limit"] == 10


# =============================================================================
# EXECUTE QUERY TESTS
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_execute_query_arguments(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Verify SQL, params and page limit are supplied to execute_query.
    """
    plan = MagicMock()

    plan.sql = "SELECT * FROM gold.project_forecasts_vw WHERE proj_id = %s"
    plan.params = ["P-1001"]

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            _forecast(),
        ]
    }

    page = PaginationModel(
        limit=25,
    )

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 1

    mock_execute_query.assert_called_once_with(
        plan.sql,
        plan.params,
        limit=25,
    )


# =============================================================================
# TOTAL COUNT CLEANUP THROUGH PUBLIC FUNCTION
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_removes_internal_total_count(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    total_count_hidden returned from SQL should never leak into the response.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            {
                **_forecast(),
                "total_count_hidden": 100,
            }
        ]
    }

    result = project_forecasts.get_project_forecasts()

    assert len(result["items"]) == 1

    assert "total_count_hidden" not in result["items"][0]


# =============================================================================
# MULTIPLE ROW TEST
# =============================================================================


@patch.object(project_forecasts, "execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_multiple_rows(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Multiple rows under the limit should all be returned.
    """
    mock_get_list_plan.return_value = _mock_plan()

    mock_execute_query.return_value = {
        "items": [
            _forecast(
                row_id=1,
                proj_id="P-1001",
            ),
            _forecast(
                row_id=2,
                proj_id="P-1002",
            ),
            _forecast(
                row_id=3,
                proj_id="P-1003",
            ),
        ]
    }

    page = PaginationModel(
        limit=10,
    )

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 3

    assert result["items"][0]["proj_id"] == "P-1001"
    assert result["items"][1]["proj_id"] == "P-1002"
    assert result["items"][2]["proj_id"] == "P-1003"

    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None


# =============================================================================
# BUILDER INITIALIZATION TEST
# =============================================================================


def test_repository_builder_spec():
    """
    Repository builder should be configured from PROJECT_FORECASTS_VIEW_SPEC.
    """
    assert project_forecasts._builder is not None

    assert (
        project_forecasts.PROJECT_FORECASTS_VIEW_SPEC.table
        == "gold.project_forecasts_vw"
    )
