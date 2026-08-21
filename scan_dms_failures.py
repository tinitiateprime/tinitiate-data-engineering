# AUTO-GENERATED / PROJECT INFO REPOSITORY TESTS
# tests/unit/db/test_project_info_repo.py

from unittest.mock import ANY, MagicMock, patch

import pytest

from db.repositories import project_info_repo
from v1.schemas import (
    FilterOps,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def mock_plan():
    """
    Common query plan returned by BaseRepositoryBuilder.
    """
    plan = MagicMock()
    plan.sql = "SELECT * FROM generated_test_source"
    plan.params = {}
    return plan


# ============================================================
# _format_paginated_response
# NO MORE RESULTS
# ============================================================

def test_format_paginated_response_no_more():
    items = [
        {
            "proj_id": "P-1001",
            "proj_name": "Project One",
            "total_count_hidden": 1,
        }
    ]

    result = project_info_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert isinstance(result, dict)

    assert "items" in result
    assert "page" in result

    assert len(result["items"]) == 1

    assert result["items"][0]["proj_id"] == "P-1001"

    # Internal DB-only value must be removed
    assert "total_count_hidden" not in result["items"][0]

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


# ============================================================
# _format_paginated_response
# HAS MORE RESULTS
# ============================================================

@patch("db.repositories.project_info_repo.encode_cursor")
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    mock_encode_cursor.return_value = "encoded-project-cursor"

    items = [
        {
            "proj_id": "P-1001",
            "proj_name": "Project One",
            "total_count_hidden": 3,
        },
        {
            "proj_id": "P-1002",
            "proj_name": "Project Two",
            "total_count_hidden": 3,
        },
        {
            "proj_id": "P-1003",
            "proj_name": "Project Three",
            "total_count_hidden": 3,
        },
    ]

    result = project_info_repo._format_paginated_response(
        items=items,
        limit=2,
    )

    assert isinstance(result, dict)

    assert len(result["items"]) == 2

    assert result["items"][0]["proj_id"] == "P-1001"
    assert result["items"][1]["proj_id"] == "P-1002"

    assert "total_count_hidden" not in result["items"][0]
    assert "total_count_hidden" not in result["items"][1]

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-project-cursor"

    mock_encode_cursor.assert_called_once_with("P-1002")


# ============================================================
# GET PROJECT INFO
# SUCCESS
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_success(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
                "cust_id": "C-100",
                "customer_name": "Test Customer",
                "total_count_hidden": 1,
            }
        ]
    }

    filters = FiltersEnvelope(
        filters={}
    )

    sort = SortModel()

    page = PaginationModel(
        limit=10
    )

    columns = None

    result = project_info_repo.get_project_info(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )

    assert isinstance(result, dict)

    assert "items" in result
    assert "page" in result

    assert len(result["items"]) == 1

    assert result["items"][0]["proj_id"] == "P-1001"

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once_with(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )

    # IMPORTANT:
    # project_info_repo passes limit=current_page.limit
    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=10,
    )


# ============================================================
# GET PROJECT INFO
# DEFAULT / EMPTY INPUT
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_empty(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": []
    }

    result = project_info_repo.get_project_info()

    assert isinstance(result, dict)

    assert result["items"] == []

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once()

    repo_call = mock_get_plan.call_args

    assert isinstance(
        repo_call.kwargs["filters"],
        FiltersEnvelope,
    )

    assert isinstance(
        repo_call.kwargs["sort"],
        SortModel,
    )

    assert isinstance(
        repo_call.kwargs["page"],
        PaginationModel,
    )

    assert repo_call.kwargs["columns"] is None

    expected_limit = repo_call.kwargs["page"].limit

    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=expected_limit,
    )


# ============================================================
# GET PROJECT INFO
# DICT FILTERS
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_dict_filters(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
                "total_count_hidden": 1,
            }
        ]
    }

    filters = {
        "proj_id": FilterOps(
            eq="P-1001"
        )
    }

    result = project_info_repo.get_project_info(
        filters=filters,
    )

    assert isinstance(result, dict)

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"

    mock_get_plan.assert_called_once()

    repo_call = mock_get_plan.call_args

    generated_filters = repo_call.kwargs["filters"]

    assert isinstance(
        generated_filters,
        FiltersEnvelope,
    )

    assert generated_filters.filters is not None

    assert "proj_id" in generated_filters.filters

    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=repo_call.kwargs["page"].limit,
    )


# ============================================================
# GET PROJECT INFO
# HAS MORE
# ============================================================

@patch(
    "db.repositories.project_info_repo.encode_cursor"
)
@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_has_more(
    mock_get_plan,
    mock_execute,
    mock_encode_cursor,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_encode_cursor.return_value = "next-project-cursor"

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "total_count_hidden": 2,
            },
            {
                "proj_id": "P-1002",
                "total_count_hidden": 2,
            },
        ]
    }

    page = PaginationModel(
        limit=1
    )

    result = project_info_repo.get_project_info(
        page=page,
    )

    assert len(result["items"]) == 1

    assert result["items"][0]["proj_id"] == "P-1001"

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "next-project-cursor"

    mock_encode_cursor.assert_called_once_with(
        "P-1001"
    )

    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=1,
    )


# ============================================================
# GET PROJECT INFO BY ID
# EMPTY PROJECT ID
# ============================================================

def test_get_project_info_by_id_empty():
    result = project_info_repo.get_project_info_by_id(
        "   "
    )

    assert isinstance(result, dict)

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# ============================================================
# GET PROJECT INFO BY ID
# SUCCESS
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_by_id_success(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
                "cust_id": "C-100",
                "customer_name": "Test Customer",
                "total_count_hidden": 1,
            }
        ]
    }

    columns = [
        "proj_id",
        "proj_name",
    ]

    result = project_info_repo.get_project_info_by_id(
        proj_id="P-1001",
        columns=columns,
    )

    assert isinstance(result, dict)

    assert len(result["items"]) == 1

    assert result["items"][0]["proj_id"] == "P-1001"

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once()

    repo_call = mock_get_plan.call_args

    generated_filters = repo_call.kwargs["filters"]
    generated_sort = repo_call.kwargs["sort"]
    generated_page = repo_call.kwargs["page"]

    assert isinstance(
        generated_filters,
        FiltersEnvelope,
    )

    assert isinstance(
        generated_sort,
        SortModel,
    )

    assert isinstance(
        generated_page,
        PaginationModel,
    )

    assert generated_page.limit == 1

    assert repo_call.kwargs["columns"] == columns

    assert generated_filters.filters is not None

    assert "proj_id" in generated_filters.filters

    proj_filter = generated_filters.filters[
        "proj_id"
    ]

    assert proj_filter.eq == "P-1001"

    # IMPORTANT:
    # by-id repository explicitly uses PaginationModel(limit=1)
    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=1,
    )


# ============================================================
# GET PROJECT INFO BY ID
# NOT FOUND
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_by_id_not_found(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": []
    }

    result = project_info_repo.get_project_info_by_id(
        proj_id="P-9999",
    )

    assert isinstance(result, dict)

    assert result["items"] == []

    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once()

    repo_call = mock_get_plan.call_args

    generated_filters = repo_call.kwargs["filters"]

    assert isinstance(
        generated_filters,
        FiltersEnvelope,
    )

    assert generated_filters.filters[
        "proj_id"
    ].eq == "P-9999"

    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=1,
    )


# ============================================================
# GET PROJECT INFO BY ID
# PROJECT ID SHOULD BE STRIPPED
# ============================================================

@patch(
    "db.repositories.project_info_repo.execute_query"
)
@patch(
    "db.repositories.project_info_repo._builder.get_list_plan"
)
def test_get_project_info_by_id_strips_project_id(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "total_count_hidden": 1,
            }
        ]
    }

    result = project_info_repo.get_project_info_by_id(
        proj_id="  P-1001  ",
    )

    assert result["items"][0]["proj_id"] == "P-1001"

    repo_call = mock_get_plan.call_args

    generated_filters = repo_call.kwargs[
        "filters"
    ]

    assert generated_filters.filters[
        "proj_id"
    ].eq == "P-1001"

    mock_execute.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=1,
    )
