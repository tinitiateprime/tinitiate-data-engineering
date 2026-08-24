"""
Unit tests for db.repositories.project_forecasts.
"""

from unittest.mock import MagicMock, patch

import pytest

from core.filters import FiltersEnvelope
from core.pagination import PaginationModel
from core.sort import SortModel

from db.repositories import project_forecasts


# ============================================================
# TEST DATA
# ============================================================


def _forecast(
    row_id=1,
    proj_id="P-1001",
    lvl_no=1,
    proj_name="Project Alpha",
):
    return {
        "row_id": row_id,
        "proj_id": proj_id,
        "lvl_no": lvl_no,
        "cust_name": "ABC Customer",
        "proj_name": proj_name,
        "proj_type_dc": "FIXED_PRICE",
        "reporting_category": "ACTIVE",
        "prime_contr_id": "PRIME-001",
        "org_id": "ORG-001",
        "active_fl": "Y",
        "proj_mgr_name": "John Smith",
        "proj_start_dt": "2026-01-01",
        "proj_end_dt": "2026-12-31",
        "value_total_amount": 1000000.0,
        "project_value_cost": 800000.0,
        "project_value_fee": 200000.0,
        "proj_f_tot_amt": 900000.0,
        "cost_funded": 700000.0,
        "fee_funded": 200000.0,
        "total_billed": 500000.0,
        "billed_cost": 400000.0,
        "billed_fee": 100000.0,
        "open_billing_detail_amt": 50000.0,
        "open_commit_amt": 300000.0,
        "eac": 950000.0,
        "etc": 450000.0,
        "date_75_expended": "2026-08-01",
        "date_100_expended": "2026-12-01",
        "forecast_by_period": "{}",
        "total_count_hidden": 99,
    }


# ============================================================
# QUERY SPEC
# ============================================================


def test_project_forecasts_view_spec():
    """
    Verify important QuerySpec configuration.
    """

    spec = project_forecasts.PROJECT_FORECASTS_VIEW_SPEC

    assert spec is not None
    assert spec.table == "gold.project_forecasts_vw"
    assert spec.logical_id_field == "row_id"

    assert spec.use_array_any is False

    assert "row_id" in spec.column_map
    assert "proj_id" in spec.column_map
    assert "lvl_no" in spec.column_map
    assert "proj_name" in spec.column_map
    assert "eac" in spec.column_map
    assert "etc" in spec.column_map
    assert "forecast_by_period" in spec.column_map

    assert "row_id" in spec.allowed_sort_fields
    assert "proj_id" in spec.allowed_sort_fields
    assert "proj_name" in spec.allowed_sort_fields
    assert "eac" in spec.allowed_sort_fields
    assert "etc" in spec.allowed_sort_fields

    assert "row_id" in spec.default_select
    assert "proj_id" in spec.default_select
    assert "proj_name" in spec.default_select
    assert "forecast_by_period" in spec.default_select


# ============================================================
# _format_paginated_response
# ============================================================


def test_format_paginated_response_empty():
    """
    Empty result should return no cursor and has_more False.
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
    Fewer records than the requested limit should not paginate.
    """

    items = [
        _forecast(row_id=1),
        _forecast(row_id=2),
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
    Exactly limit records should not indicate another page.
    """

    items = [
        _forecast(row_id=1),
        _forecast(row_id=2),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=2,
    )

    assert len(result["items"]) == 2
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch("db.repositories.project_forecasts.encode_cursor")
def test_format_paginated_response_has_more(mock_encode_cursor):
    """
    limit + 1 rows should set has_more and create next cursor
    using the last returned row.
    """

    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        _forecast(row_id=1),
        _forecast(row_id=2),
        _forecast(row_id=3),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=2,
    )

    assert len(result["items"]) == 2
    assert result["items"][0]["row_id"] == 1
    assert result["items"][1]["row_id"] == 2

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"

    mock_encode_cursor.assert_called_once_with(2)


@patch("db.repositories.project_forecasts.encode_cursor")
def test_format_paginated_response_removes_total_count_hidden(
    mock_encode_cursor,
):
    """
    Internal total_count_hidden field must be removed from
    returned records.
    """

    mock_encode_cursor.return_value = "next"

    items = [
        _forecast(row_id=1),
        _forecast(row_id=2),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=10,
    )

    for item in result["items"]:
        assert "total_count_hidden" not in item


@patch("db.repositories.project_forecasts.encode_cursor")
def test_format_paginated_response_cursor_uses_last_visible_row(
    mock_encode_cursor,
):
    """
    When the DB returns limit + 1 rows, cursor should be generated
    from the final row retained after slicing.
    """

    mock_encode_cursor.return_value = "cursor-20"

    items = [
        _forecast(row_id=10),
        _forecast(row_id=20),
        _forecast(row_id=30),
    ]

    result = project_forecasts._format_paginated_response(
        items=items,
        limit=2,
    )

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "cursor-20"

    mock_encode_cursor.assert_called_once_with(20)


# ============================================================
# get_project_forecasts
# ============================================================


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_defaults(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Verify defaults are created when no arguments are supplied.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT * FROM gold.project_forecasts_vw"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [],
    }

    result = project_forecasts.get_project_forecasts()

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_list_plan.assert_called_once()

    kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(kwargs["filters"], FiltersEnvelope)
    assert isinstance(kwargs["sort"], SortModel)
    assert isinstance(kwargs["page"], PaginationModel)
    assert kwargs["columns"] is None

    mock_execute_query.assert_called_once()


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Dictionary filters should be wrapped in FiltersEnvelope.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = ["P-1001"]

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_forecast()],
    }

    filters = {
        "proj_id": "P-1001",
    }

    result = project_forecasts.get_project_forecasts(
        filters=filters,
    )

    assert len(result["items"]) == 1

    kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(kwargs["filters"], FiltersEnvelope)

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_filters_envelope(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Existing FiltersEnvelope should be passed directly to builder.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_forecast()],
    }

    filters = FiltersEnvelope(filters={})

    result = project_forecasts.get_project_forecasts(
        filters=filters,
    )

    assert len(result["items"]) == 1

    kwargs = mock_get_list_plan.call_args.kwargs

    assert kwargs["filters"] is filters


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_custom_sort(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Custom sort should be forwarded unchanged.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_forecast()],
    }

    sort = SortModel(
        field="proj_id",
        order="asc",
    )

    project_forecasts.get_project_forecasts(
        sort=sort,
    )

    kwargs = mock_get_list_plan.call_args.kwargs

    assert kwargs["sort"] is sort


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_custom_page(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Custom PaginationModel should be forwarded unchanged.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_forecast()],
    }

    page = PaginationModel(
        limit=5,
    )

    project_forecasts.get_project_forecasts(
        page=page,
    )

    kwargs = mock_get_list_plan.call_args.kwargs

    assert kwargs["page"] is page


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_custom_columns(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Requested columns should be forwarded to the builder.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT proj_id, proj_name"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_forecast()],
    }

    columns = [
        "proj_id",
        "proj_name",
    ]

    project_forecasts.get_project_forecasts(
        columns=columns,
    )

    kwargs = mock_get_list_plan.call_args.kwargs

    assert kwargs["columns"] == columns


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_all_arguments(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Verify filters, sort, pagination and columns are all forwarded.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = ["P-1001"]

    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _forecast(row_id=1),
        ],
    }

    filters = FiltersEnvelope(filters={})

    sort = SortModel(
        field="proj_id",
        order="desc",
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

    assert len(result["items"]) == 1

    kwargs = mock_get_list_plan.call_args.kwargs

    assert kwargs["filters"] is filters
    assert kwargs["sort"] is sort
    assert kwargs["page"] is page
    assert kwargs["columns"] == columns


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_multiple_items_no_more(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Multiple records <= page limit should return has_more False.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _forecast(row_id=1),
            _forecast(row_id=2),
            _forecast(row_id=3),
        ],
    }

    page = PaginationModel(limit=10)

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 3
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None


@patch("db.repositories.project_forecasts.encode_cursor")
@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_multiple_items_has_more(
    mock_get_list_plan,
    mock_execute_query,
    mock_encode_cursor,
):
    """
    DB result containing limit + 1 records should produce next cursor.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _forecast(row_id=100),
            _forecast(row_id=200),
            _forecast(row_id=300),
        ],
    }

    mock_encode_cursor.return_value = "cursor-200"

    page = PaginationModel(limit=2)

    result = project_forecasts.get_project_forecasts(
        page=page,
    )

    assert len(result["items"]) == 2
    assert result["items"][0]["row_id"] == 100
    assert result["items"][1]["row_id"] == 200

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "cursor-200"

    mock_encode_cursor.assert_called_once_with(200)


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_removes_hidden_count(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    total_count_hidden should never appear in returned API records.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan

    item = _forecast()
    assert "total_count_hidden" in item

    mock_execute_query.return_value = {
        "items": [item],
    }

    result = project_forecasts.get_project_forecasts()

    assert len(result["items"]) == 1
    assert "total_count_hidden" not in result["items"][0]


@patch("db.repositories.project_forecasts.execute_query")
@patch.object(project_forecasts._builder, "get_list_plan")
def test_get_project_forecasts_builder_called_with_correct_values(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Explicitly validate builder input.
    """

    mock_plan = MagicMock()
    mock_plan.sql = "SELECT TEST"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {"items": []}

    filters = FiltersEnvelope(filters={})
    sort = SortModel(field="row_id", order="asc")
    page = PaginationModel(limit=25)
    columns = ["row_id", "proj_id"]

    project_forecasts.get_project_forecasts(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )

    mock_get_list_plan.assert_called_once_with(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )


# ============================================================
# BUILDER INITIALIZATION
# ============================================================


def test_builder_exists():
    """
    Repository builder must be initialized.
    """

    assert project_forecasts._builder is not None


def test_builder_uses_project_forecasts_spec():
    """
    The repository's builder should exist for the Project Forecasts spec.
    """

    assert project_forecasts.PROJECT_FORECASTS_VIEW_SPEC is not None
    assert project_forecasts._builder is not None
