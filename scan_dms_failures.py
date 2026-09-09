from unittest.mock import MagicMock, patch

import pytest

from db.repositories import irc_census_report_repo
from v1.schemas import (
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def mock_plan():
    plan = MagicMock()
    plan.sql = "SELECT * FROM irc_census_report_mv"
    plan.params = []
    return plan


# ============================================================
# GET IRC CENSUS REPORTS - SUCCESS
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_reports_success(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "row_id": "1001",
                "last_first_name": "Doe, Jane",
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

    result = irc_census_report_repo.get_irc_census_reports(
        filters=filters,
        sort=sort,
        page=page,
        columns=None,
    )

    assert isinstance(result, dict)
    assert len(result["items"]) == 1
    assert result["items"][0]["row_id"] == "1001"

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# GET IRC CENSUS REPORTS - EMPTY
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_reports_empty(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = irc_census_report_repo.get_irc_census_reports(
        filters=None,
        sort=None,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert isinstance(result, dict)
    assert result["items"] == []

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME - FOUND
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_report_by_id_found(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "row_id": "1001",
                "last_first_name": "Doe, Jane",
            }
        ]
    }

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = irc_census_report_repo.get_irc_census_report_by_id(
        last_first_name="Doe, Jane",
        filters=filters,
        page=page,
        columns=columns,
        sort=sort,
    )

    assert isinstance(result, dict)
    assert len(result["items"]) == 1
    assert result["items"][0]["last_first_name"] == "Doe, Jane"

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME - NOT FOUND
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_report_by_id_not_found(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": []
    }

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = irc_census_report_repo.get_irc_census_report_by_id(
        last_first_name="Missing, Person",
        filters=filters,
        page=page,
        columns=columns,
        sort=sort,
    )

    assert isinstance(result, dict)
    assert result["items"] == []

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# FORMAT PAGINATED RESPONSE - HAS MORE
# ============================================================

@patch("db.repositories.irc_census_report_repo.encode_cursor")
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        {
            "row_id": "1001",
            "last_first_name": "Doe, Jane",
            "total_count_hidden": 2,
        },
        {
            "row_id": "1002",
            "last_first_name": "Smith, John",
            "total_count_hidden": 2,
        },
    ]

    result = irc_census_report_repo._format_paginated_response(
        items,
        limit=1,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"

    assert "total_count_hidden" not in result["items"][0]

    # row_id stays here because it is the pagination/keyset cursor
    mock_encode_cursor.assert_called_once_with("1001")


# ============================================================
# FORMAT PAGINATED RESPONSE - NO MORE
# ============================================================

def test_format_paginated_response_no_more():
    items = [
        {
            "row_id": "1001",
            "last_first_name": "Doe, Jane",
            "total_count_hidden": 1,
        }
    ]

    result = irc_census_report_repo._format_paginated_response(
        items,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None

    assert "total_count_hidden" not in result["items"][0]


# ============================================================
# GET IRC CENSUS REPORTS - DICT FILTERS
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_reports_dict_filters(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan
    mock_execute.return_value = {
        "items": []
    }

    filters = {}

    result = irc_census_report_repo.get_irc_census_reports(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert isinstance(result, dict)
    assert result["items"] == []

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME - NONE FILTERS
# ============================================================

@patch("db.repositories.irc_census_report_repo.execute_query")
@patch("db.repositories.irc_census_report_repo._builder.get_list_plan")
def test_get_irc_census_report_by_id_none_filters(
    mock_get_plan,
    mock_execute,
    mock_plan,
):
    mock_get_plan.return_value = mock_plan

    mock_execute.return_value = {
        "items": [
            {
                "row_id": "1001",
                "last_first_name": "Doe, Jane",
            }
        ]
    }

    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    result = irc_census_report_repo.get_irc_census_report_by_id(
        last_first_name="Doe, Jane",
        filters=None,
        page=page,
        columns=columns,
        sort=sort,
    )

    assert isinstance(result, dict)
    assert len(result["items"]) == 1
    assert result["items"][0]["last_first_name"] == "Doe, Jane"

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()


# ============================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME
# RECURSIVE FILTER BRANCH
# ============================================================

def test_get_irc_census_report_by_id_recursive_filter_branch():
    class RecursiveFilterContainer:
        def __init__(self):
            self.filters = []

    recursive_filters = RecursiveFilterContainer()

    filters_envelope = FiltersEnvelope.model_construct(
        filters=recursive_filters,
    )

    sort = SortModel()
    page = PaginationModel(limit=10)
    columns = None

    try:
        irc_census_report_repo.get_irc_census_report_by_id(
            last_first_name="Doe, Jane",
            filters=filters_envelope,
            page=page,
            columns=columns,
            sort=sort,
        )
    except Exception:
        # This test only exercises the recursive-filter branch.
        # We are not testing actual DB execution here.
        pass

    assert len(recursive_filters.filters) == 1

    added_rule = recursive_filters.filters[0]

    assert added_rule.field == "last_first_name"
    assert added_rule.ops.eq == "Doe, Jane"
