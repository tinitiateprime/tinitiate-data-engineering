from unittest.mock import MagicMock, patch

from db.repositories import project_financial_repo
from v1.schemas import (
    FilterGroup,
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


def test_format_paginated_response_has_more():
    items = [
        {"proj_id": "P-1001"},
        {"proj_id": "P-1002"},
        {"proj_id": "P-1003"},
    ]

    result = project_financial_repo._format_paginated_response(
        items,
        limit=2,
    )

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] is not None
    assert len(result["items"]) == 2
    assert result["items"][0]["proj_id"] == "P-1001"
    assert result["items"][1]["proj_id"] == "P-1002"


def test_format_paginated_response_no_more():
    items = [
        {"proj_id": "P-1001"},
        {"proj_id": "P-1002"},
    ]

    result = project_financial_repo._format_paginated_response(
        items,
        limit=10,
    )

    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None
    assert len(result["items"]) == 2


def test_format_paginated_response_removes_hidden_count():
    items = [
        {
            "proj_id": "P-1001",
            "total_count_hidden": 10,
        },
        {
            "proj_id": "P-1002",
            "total_count_hidden": 10,
        },
    ]

    result = project_financial_repo._format_paginated_response(
        items,
        limit=10,
    )

    assert "total_count_hidden" not in result["items"][0]
    assert "total_count_hidden" not in result["items"][1]


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financials_success(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "cust_name": "Test Customer",
                "proj_name": "Test Project",
            }
        ]
    }

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)

    result = project_financial_repo.get_project_financials(
        filters=filters,
        sort=sort,
        page=page,
    )

    mock_get_list_plan.assert_called_once_with(
        filters=filters,
        sort=sort,
        page=page,
        columns=None,
    )

    mock_execute_query.assert_called_once_with(
        plan.sql,
        plan.params,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"
    assert result["items"][0]["proj_name"] == "Test Project"


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financials_with_custom_columns(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT proj_id, proj_name FROM project_financials_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    columns = ["proj_id", "proj_name"]

    result = project_financial_repo.get_project_financials(
        filters=FiltersEnvelope(filters={}),
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=columns,
    )

    mock_get_list_plan.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs
    assert call_kwargs["columns"] == columns

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financials_with_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {"p0": "P-1001"}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    result = project_financial_repo.get_project_financials(
        filters={
            "proj_id": FilterOps(eq="P-1001"),
        },
        sort=SortModel(),
        page=PaginationModel(limit=10),
    )

    mock_get_list_plan.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs
    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )

    assert len(result["items"]) == 1


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financials_with_none_defaults(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": []
    }

    result = project_financial_repo.get_project_financials(
        filters=None,
        sort=None,
        page=None,
    )

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )
    assert isinstance(
        call_kwargs["sort"],
        SortModel,
    )
    assert isinstance(
        call_kwargs["page"],
        PaginationModel,
    )

    assert result["items"] == []
    assert result["page"]["has_more"] is False


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financial_by_id_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {"p0": "P-1001"}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    result = project_financial_repo.get_project_financial_by_id(
        proj_id="P-1001"
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once_with(
        plan.sql,
        plan.params,
    )

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    assert validated_filters.filters["proj_id"].eq == "P-1001"


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financial_by_id_not_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {"p0": "NONEXISTENT"}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": []
    }

    result = project_financial_repo.get_project_financial_by_id(
        proj_id="NONEXISTENT"
    )

    assert result["items"] == []
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financial_by_id_with_filter_group(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    filter_group = FilterGroup(
        filters=[
            FilterRule(
                field="proj_name",
                ops=FilterOps(
                    ilike="%Test%",
                ),
            )
        ]
    )

    result = project_financial_repo.get_project_financial_by_id(
        proj_id="P-1001",
        filters=filter_group,
    )

    assert len(result["items"]) == 1

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    assert isinstance(
        validated_filters.filters,
        FilterGroup,
    )

    project_id_rules = [
        rule
        for rule in validated_filters.filters.filters
        if rule.field == "proj_id"
    ]

    assert len(project_id_rules) == 1
    assert project_id_rules[0].ops.eq == "P-1001"


@patch("db.repositories.project_financial_repo.execute_query")
@patch("db.repositories.project_financial_repo._builder.get_list_plan")
def test_get_project_financial_by_id_with_existing_envelope(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM project_financials_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    filters = FiltersEnvelope(
        filters={
            "proj_name": FilterOps(
                eq="Test Project",
            )
        }
    )

    result = project_financial_repo.get_project_financial_by_id(
        proj_id="P-1001",
        filters=filters,
    )

    assert len(result["items"]) == 1

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert validated_filters.filters["proj_id"].eq == "P-1001"
    assert validated_filters.filters["proj_name"].eq == "Test Project"
