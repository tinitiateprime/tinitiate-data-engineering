from unittest.mock import MagicMock, patch

from db.repositories import agent_repo
from v1.schemas import (
    FilterGroup,
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# =============================================================================
# _format_paginated_response TESTS
# =============================================================================


def test_format_paginated_response_has_more():
    items = [
        {"proj_id": "C-1001"},
        {"proj_id": "P-1001"},
        {"proj_id": "P-1002"},
    ]

    result = agent_repo._format_paginated_response(
        items,
        limit=2,
    )

    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] is not None
    assert len(result["items"]) == 2
    assert result["items"][0]["proj_id"] == "C-1001"
    assert result["items"][1]["proj_id"] == "P-1001"


def test_format_paginated_response_no_more():
    items = [
        {"proj_id": "C-1001"},
        {"proj_id": "P-1002"},
    ]

    result = agent_repo._format_paginated_response(
        items,
        limit=10,
    )

    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None
    assert len(result["items"]) == 2


def test_format_paginated_response_removes_hidden_count():
    items = [
        {
            "proj_id": "C-1001",
            "total_count_hidden": 10,
        },
        {
            "proj_id": "P-1002",
            "total_count_hidden": 10,
        },
    ]

    result = agent_repo._format_paginated_response(
        items,
        limit=10,
    )

    assert "total_count_hidden" not in result["items"][0]
    assert "total_count_hidden" not in result["items"][1]


# =============================================================================
# get_work_locations_by_contract_id TESTS
# =============================================================================


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_success(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
                "cust_name": "Test Customer",
                "proj_name": "Test Project",
            }
        ]
    }

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)

    result = agent_repo.get_work_locations_by_contract_id(
        contract_id="C-1001",
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
    assert result["items"][0]["proj_id"] == "C-1001"
    assert result["items"][0]["proj_name"] == "Test Project"


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_with_custom_columns(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT proj_id, proj_name FROM agent_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    columns = ["proj_id", "proj_name"]

    result = agent_repo.get_work_locations_by_contract_id(
        contract_id="C-1001",
        filters=FiltersEnvelope(filters={}),
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=columns,
    )

    mock_get_list_plan.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert call_kwargs["columns"] == columns

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "C-1001"


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_with_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {"p0": "C-1001"}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    result = agent_repo.get_work_locations_by_contract_id(
        contract_id="C-1001",
        filters={
            "proj_id": FilterOps(eq="C-1001"),
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


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_with_none_defaults(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": []
    }

    result = agent_repo.get_work_locations_by_contract_id(
        contract_id="C-1001",
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


# =============================================================================
# get_work_locations_by_contract_id_by_id TESTS
# =============================================================================


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_by_id_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {"p0": "C-1001"}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    result = agent_repo.get_work_locations_by_contract_id_by_id(
        proj_id="C-1001",
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "C-1001"

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

    assert validated_filters.filters["proj_id"].eq == "C-1001"


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_by_id_not_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {"p0": "NONEXISTENT"}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": []
    }

    result = agent_repo.get_work_locations_by_contract_id_by_id(
        proj_id="NONEXISTENT",
    )

    assert result["items"] == []
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_by_id_with_filter_group(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
                "proj_name": "Test Project",
            }
        ]
    }

    filter_group = FilterGroup(
        filters=[
            FilterRule(
                field="proj_name",
                ops=FilterOps(
                    like="%Test%",
                ),
            )
        ]
    )

    result = agent_repo.get_work_locations_by_contract_id_by_id(
        proj_id="C-1001",
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
    assert project_id_rules[0].ops.eq == "C-1001"


@patch("db.repositories.agent_repo.execute_query")
@patch("db.repositories.agent_repo._builder.get_list_plan")
def test_get_work_locations_by_contract_id_by_id_with_existing_envelope(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT * FROM agent_source_vw"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "proj_id": "C-1001",
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

    result = agent_repo.get_work_locations_by_contract_id_by_id(
        proj_id="C-1001",
        filters=filters,
    )

    assert len(result["items"]) == 1

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert validated_filters.filters["proj_id"].eq == "C-1001"
    assert (
        validated_filters.filters["proj_name"].eq
        == "Test Project"
    )



py -m pytest main-function\tests\unit\db\test_agent_repo.py -v --cov=db.repositories.agent_repo --cov-report=term-missing
