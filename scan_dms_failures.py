from unittest.mock import ANY, MagicMock, patch

from core.filters import FilterOps, FiltersEnvelope, SortModel
from core.pagination import PaginationModel
from db.repositories import project_status_detail_repo


def _mock_plan():
    plan = MagicMock()
    plan.sql = "SELECT * FROM generated_test_source"
    plan.params = {}
    return plan


@patch("db.repositories.project_status_detail_repo.execute_query")
@patch("db.repositories.project_status_detail_repo._builder.get_list_plan")
def test_get_project_status_detail_success(
    mock_get_plan,
    mock_execute,
):
    plan = _mock_plan()
    mock_get_plan.return_value = plan

    mock_execute.return_value = {
        "items": [
            {
                "project_level": "P-1001",
                "period": 1,
                "total_count_hidden": 1,
            }
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = project_status_detail_repo.get_project_status_detail(
        filters=filters,
        sort=sort,
        page=page,
        columns=columns,
    )

    mock_get_plan.assert_called_once_with(
        filters=ANY,
        sort=ANY,
        page=ANY,
        columns=ANY,
    )

    mock_execute.assert_called_once_with(
        plan.sql,
        plan.params,
        limit=page.limit,
    )

    assert result is not None
    assert "items" in result
    assert len(result["items"]) == 1
    assert result["items"][0]["project_level"] == "P-1001"


@patch("db.repositories.project_status_detail_repo.execute_query")
@patch("db.repositories.project_status_detail_repo._builder.get_list_plan")
def test_get_project_status_detail_empty(
    mock_get_plan,
    mock_execute,
):
    plan = _mock_plan()
    mock_get_plan.return_value = plan

    mock_execute.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = project_status_detail_repo.get_project_status_detail()

    assert result is not None
    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch("db.repositories.project_status_detail_repo.execute_query")
@patch("db.repositories.project_status_detail_repo._builder.get_list_plan")
def test_get_project_status_detail_by_project_level_found(
    mock_get_plan,
    mock_execute,
):
    plan = _mock_plan()
    mock_get_plan.return_value = plan

    mock_execute.return_value = {
        "items": [
            {
                "project_level": "P-1001",
                "period": 1,
                "total_count_hidden": 1,
            }
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    page = PaginationModel(limit=10)
    sort = SortModel()

    result = project_status_detail_repo.get_project_status_detail_by_project_level(
        project_level="P-1001",
        page=page,
        sort=sort,
        columns=None,
    )

    assert result is not None
    assert len(result["items"]) == 1
    assert result["items"][0]["project_level"] == "P-1001"

    mock_get_plan.assert_called_once_with(
        filters=ANY,
        sort=ANY,
        page=ANY,
        columns=ANY,
    )

    mock_execute.assert_called_once_with(
        plan.sql,
        plan.params,
        limit=page.limit,
    )


@patch("db.repositories.project_status_detail_repo.execute_query")
@patch("db.repositories.project_status_detail_repo._builder.get_list_plan")
def test_get_project_status_detail_by_project_level_not_found(
    mock_get_plan,
    mock_execute,
):
    plan = _mock_plan()
    mock_get_plan.return_value = plan

    mock_execute.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = project_status_detail_repo.get_project_status_detail_by_project_level(
        project_level="P-9999",
    )

    assert result is not None
    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch("db.repositories.project_status_detail_repo.encode_cursor")
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        {
            "project_level": "P-1001",
            "period": 1,
            "total_count_hidden": 2,
        },
        {
            "project_level": "P-1001",
            "period": 2,
            "total_count_hidden": 2,
        },
    ]

    result = project_status_detail_repo._format_paginated_response(
        items,
        limit=1,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"
    assert "total_count_hidden" not in result["items"][0]

    mock_encode_cursor.assert_called_once_with(
        "P-1001_1"
    )


def test_get_project_status_detail_dict_filters():
    filters = {
        "project_level": FilterOps(eq="P-1001"),
    }

    with (
        patch(
            "db.repositories.project_status_detail_repo._builder.get_list_plan"
        ) as mock_get_plan,
        patch(
            "db.repositories.project_status_detail_repo.execute_query"
        ) as mock_execute,
    ):
        plan = _mock_plan()
        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [],
            "page": {
                "cursor": None,
                "has_more": False,
            },
        }

        result = project_status_detail_repo.get_project_status_detail(
            filters=filters,
        )

        assert result is not None

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=ANY,
            page=ANY,
            columns=ANY,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )
