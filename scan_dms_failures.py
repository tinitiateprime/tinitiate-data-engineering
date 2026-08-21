from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from db.repositories import po_funding_detail_repo as repo


# ============================================================
# GET PO FUNDING DETAIL - SUCCESS
# ============================================================
def test_get_po_funding_detail_success(monkeypatch):
    mock_plan = SimpleNamespace(
        sql="SELECT * FROM po_funding_detail",
        params=[],
    )

    mock_get_list_plan = MagicMock(return_value=mock_plan)

    mock_execute_query = MagicMock(
        return_value={
            "items": [
                {
                    "project_id": "P100",
                    "order_date": "2026-08-20",
                    "total_count_hidden": 1,
                }
            ]
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    result = repo.get_po_funding_detail()

    assert result is not None
    assert "items" in result
    assert "page" in result

    assert len(result["items"]) == 1

    assert result["items"][0]["project_id"] == "P100"

    # Internal pagination helper field should not be returned
    assert "total_count_hidden" not in result["items"][0]

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


# ============================================================
# GET PO FUNDING DETAIL - EMPTY RESULT
# ============================================================
def test_get_po_funding_detail_empty(monkeypatch):
    mock_plan = SimpleNamespace(
        sql="SELECT * FROM po_funding_detail",
        params=[],
    )

    mock_get_list_plan = MagicMock(return_value=mock_plan)

    mock_execute_query = MagicMock(
        return_value={
            "items": []
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    result = repo.get_po_funding_detail()

    assert result is not None

    assert result["items"] == []

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


# ============================================================
# FORMAT PAGINATED RESPONSE - HAS MORE
# ============================================================
def test_format_paginated_response_has_more():
    items = [
        {
            "project_id": "P100",
            "order_date": "2026-08-20",
            "total_count_hidden": 3,
        },
        {
            "project_id": "P101",
            "order_date": "2026-08-19",
            "total_count_hidden": 3,
        },
        {
            "project_id": "P102",
            "order_date": "2026-08-18",
            "total_count_hidden": 3,
        },
    ]

    result = repo._format_paginated_response(
        items,
        limit=2,
    )

    assert result is not None
    assert "items" in result
    assert "page" in result

    # Limit is 2 but 3 records were supplied,
    # therefore only 2 should be returned.
    assert len(result["items"]) == 2

    assert result["page"]["has_more"] is True

    # Internal field should be removed
    for item in result["items"]:
        assert "total_count_hidden" not in item


# ============================================================
# GET PO FUNDING DETAIL - DICT FILTERS
# ============================================================
def test_get_po_funding_detail_dict_filters(monkeypatch):
    mock_plan = SimpleNamespace(
        sql="SELECT * FROM po_funding_detail WHERE project_id = %s",
        params=["P100"],
    )

    mock_get_list_plan = MagicMock(return_value=mock_plan)

    mock_execute_query = MagicMock(
        return_value={
            "items": [
                {
                    "project_id": "P100",
                    "order_date": "2026-08-20",
                    "total_count_hidden": 1,
                }
            ]
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    filters = {
        "project_id": "P100"
    }

    result = repo.get_po_funding_detail(
        filters=filters,
    )

    assert result is not None
    assert len(result["items"]) == 1
    assert result["items"][0]["project_id"] == "P100"

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - EMPTY PROJECT ID
#
# Covers:
#     lines 127-130
# ============================================================
@pytest.mark.parametrize(
    "project_id",
    [
        "",
        "   ",
    ],
)
def test_get_po_funding_detail_by_project_id_empty(project_id):
    result = repo.get_po_funding_detail_by_project_id(
        project_id
    )

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - SUCCESS
#
# Covers:
#     FiltersEnvelope
#     FilterOps
#     default PaginationModel
#     default SortModel
#     builder.get_list_plan
#     execute_query
#     response formatting
#
# Covers approximately lines 122-148
# ============================================================
def test_get_po_funding_detail_by_project_id_success(monkeypatch):
    mock_plan = SimpleNamespace(
        sql="SELECT * FROM po_funding_detail WHERE project_id = %s",
        params=["ABC123"],
    )

    mock_get_list_plan = MagicMock(
        return_value=mock_plan
    )

    mock_execute_query = MagicMock(
        return_value={
            "items": [
                {
                    "project_id": "ABC123",
                    "order_date": "2026-08-20",
                    "total_count_hidden": 1,
                }
            ]
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    result = repo.get_po_funding_detail_by_project_id(
        "  ABC123  "
    )

    # --------------------------------------------------------
    # Validate returned response
    # --------------------------------------------------------
    assert result is not None

    assert "items" in result
    assert "page" in result

    assert len(result["items"]) == 1

    assert result["items"][0]["project_id"] == "ABC123"

    # Internal field must be removed
    assert "total_count_hidden" not in result["items"][0]

    assert result["page"]["has_more"] is False

    # --------------------------------------------------------
    # Validate builder was called
    # --------------------------------------------------------
    mock_get_list_plan.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert "filters" in call_kwargs
    assert "sort" in call_kwargs
    assert "page" in call_kwargs
    assert "columns" in call_kwargs

    # No columns supplied
    assert call_kwargs["columns"] is None

    # Default sort from repo
    assert call_kwargs["sort"].field == "order_date"
    assert call_kwargs["sort"].order == "desc"

    # --------------------------------------------------------
    # Validate execute_query
    # --------------------------------------------------------
    mock_execute_query.assert_called_once()

    execute_call = mock_execute_query.call_args

    assert execute_call.args[0] == mock_plan.sql
    assert execute_call.args[1] == mock_plan.params

    assert "limit" in execute_call.kwargs


# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - CUSTOM PAGE/SORT/COLUMNS
#
# Covers the path where defaults are NOT used.
# ============================================================
def test_get_po_funding_detail_by_project_id_custom_options(
    monkeypatch,
):
    mock_plan = SimpleNamespace(
        sql="SELECT project_id FROM po_funding_detail",
        params=["ABC123"],
    )

    mock_get_list_plan = MagicMock(
        return_value=mock_plan
    )

    mock_execute_query = MagicMock(
        return_value={
            "items": [
                {
                    "project_id": "ABC123",
                    "total_count_hidden": 1,
                }
            ]
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    page = repo.PaginationModel(
        limit=10
    )

    sort = repo.SortModel(
        field="project_id",
        order="asc",
    )

    columns = [
        "project_id",
    ]

    result = repo.get_po_funding_detail_by_project_id(
        project_id="ABC123",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert result is not None
    assert len(result["items"]) == 1

    mock_get_list_plan.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert call_kwargs["page"] is page
    assert call_kwargs["sort"] is sort
    assert call_kwargs["columns"] == columns

    mock_execute_query.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=10,
    )
