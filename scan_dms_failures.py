"""
Unit tests for domain.services.agent_service.

Tests the Agent Contract Locations service.

IMPORTANT:
- Actual model: AgentContractLocationResponse
- Actual service: agent_get_contract_locations
- Actual repository call: get_work_locations_by_contract_id
"""

from unittest.mock import patch

import pytest

from domain.models.agent import AgentContractLocationResponse
from domain.services.agent_service import agent_get_contract_locations
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_agent_repo():
    """
    Patch repository used by agent_service.
    """
    with patch(
        "domain.services.agent_service.agent_repo"
    ) as mock_repo:
        yield mock_repo


@pytest.fixture
def sample_agent_dict():
    """
    Valid AgentContractLocationResponse database-style record.
    """
    return {
        "contract_id": "CONT-1001",
        "award_number": "AMD-1001",
        "order_number": "ORD-1001",
        "mod_number": "MOD-01",
        "places": "Dallas, TX",
        "project_name": "Test Project",
        "program_manager_name": "Test Manager",
        "status": "ACTIVE",
    }


@pytest.fixture
def second_agent_dict():
    return {
        "contract_id": "CONT-1002",
        "award_number": "AMD-1002",
        "order_number": "ORD-1002",
        "mod_number": "MOD-02",
        "places": "Houston, TX",
        "project_name": "Second Project",
        "program_manager_name": "Second Manager",
        "status": "ACTIVE",
    }


def make_repo_result(
    items=None,
    cursor=None,
    has_more=False,
):
    """
    Build repository response expected by agent_service.
    """
    return {
        "items": items or [],
        "page": {
            "cursor": cursor,
            "has_more": has_more,
        },
    }


# =============================================================================
# BASIC SUCCESS TEST
# =============================================================================


def test_agent_get_contract_locations_success(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
            cursor="next-token",
            has_more=True,
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters={
            "project_name": {
                "eq": "Test Project",
            }
        },
        limit=10,
        cursor=None,
    )

    mock_agent_repo.get_work_locations_by_contract_id.assert_called_once()

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert kwargs["contract_id"] == "CONT-1001"

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert kwargs["page"].limit == 10
    assert kwargs["page"].cursor is None

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    assert kwargs["columns"] is None

    assert len(result.items) == 1

    assert isinstance(
        result.items[0],
        AgentContractLocationResponse,
    )

    item = result.items[0]

    assert item.contract_id == "CONT-1001"
    assert item.award_number == "AMD-1001"
    assert item.order_number == "ORD-1001"
    assert item.mod_number == "MOD-01"
    assert item.places == "Dallas, TX"
    assert item.project_name == "Test Project"
    assert item.program_manager_name == "Test Manager"
    assert item.status == "ACTIVE"

    assert result.metadata.cursor == "next-token"
    assert result.metadata.has_more is True


# =============================================================================
# DICT FILTER TEST
# =============================================================================


def test_agent_get_contract_locations_dict_filter(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters={
            "project_name": {
                "eq": "Test Project",
            }
        },
        limit=10,
        cursor=None,
    )

    assert len(result.items) == 1

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    assert (
        kwargs["filters"]
        .filters["project_name"]
        .eq
        == "Test Project"
    )


# =============================================================================
# NONE FILTER
# =============================================================================


def test_agent_get_contract_locations_none_filter(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert len(result.items) == 1

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )


# =============================================================================
# EMPTY RESULT
# =============================================================================


def test_agent_get_contract_locations_empty(
    mock_agent_repo,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[],
            cursor=None,
            has_more=False,
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-9999",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


# =============================================================================
# MULTIPLE RESULTS
# =============================================================================


def test_agent_get_contract_locations_multiple(
    mock_agent_repo,
    sample_agent_dict,
    second_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[
                sample_agent_dict,
                second_agent_dict,
            ]
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert len(result.items) == 2

    assert isinstance(
        result.items[0],
        AgentContractLocationResponse,
    )

    assert isinstance(
        result.items[1],
        AgentContractLocationResponse,
    )

    assert result.items[0].contract_id == "CONT-1001"
    assert result.items[1].contract_id == "CONT-1002"


# =============================================================================
# PAGINATION
# =============================================================================


def test_agent_get_contract_locations_pagination(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=25,
        cursor="cursor-123",
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert kwargs["page"].limit == 25
    assert kwargs["page"].cursor == "cursor-123"


# =============================================================================
# COLUMNS
# =============================================================================


def test_agent_get_contract_locations_columns(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    columns = [
        "contract_id",
        "project_name",
        "places",
        "status",
    ]

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
        columns=columns,
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert kwargs["columns"] == columns


# =============================================================================
# CUSTOM SORT
# =============================================================================


def test_agent_get_contract_locations_sort(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    sort = SortModel(
        field="contract_id",
        order="asc",
    )

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
        sort=sort,
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert kwargs["sort"] == sort


# =============================================================================
# MODEL CONVERSION
# =============================================================================


def test_agent_get_contract_locations_model_conversion(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict],
        )
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    item = result.items[0]

    assert isinstance(
        item,
        AgentContractLocationResponse,
    )

    assert item.contract_id == "CONT-1001"
    assert item.project_name == "Test Project"


# =============================================================================
# DATABASE STYLE PAYLOAD
# =============================================================================


def test_agent_model_database_payload(
    sample_agent_dict,
):
    model = AgentContractLocationResponse.model_validate(
        sample_agent_dict
    )

    assert model.contract_id == "CONT-1001"
    assert model.award_number == "AMD-1001"
    assert model.order_number == "ORD-1001"
    assert model.mod_number == "MOD-01"
    assert model.places == "Dallas, TX"
    assert model.project_name == "Test Project"
    assert model.program_manager_name == "Test Manager"
    assert model.status == "ACTIVE"


# =============================================================================
# API ALIAS PAYLOAD
# =============================================================================


def test_agent_model_api_alias_payload():
    payload = {
        "contractId": "CONT-1001",
        "awardNumber": "AMD-1001",
        "orderNumber": "ORD-1001",
        "modNumber": "MOD-01",
        "places": "Dallas, TX",
        "projectName": "Test Project",
        "programManagerName": "Test Manager",
        "status": "ACTIVE",
    }

    model = AgentContractLocationResponse.model_validate(
        payload
    )

    assert model.contract_id == "CONT-1001"
    assert model.award_number == "AMD-1001"
    assert model.order_number == "ORD-1001"
    assert model.mod_number == "MOD-01"
    assert model.places == "Dallas, TX"
    assert model.project_name == "Test Project"
    assert model.program_manager_name == "Test Manager"
    assert model.status == "ACTIVE"


# =============================================================================
# OPTIONAL FIELDS
# =============================================================================


def test_agent_model_optional_fields():
    model = AgentContractLocationResponse(
        contract_id="CONT-1001"
    )

    assert model.contract_id == "CONT-1001"

    assert model.award_number is None
    assert model.order_number is None
    assert model.mod_number is None
    assert model.places is None
    assert model.project_name is None
    assert model.program_manager_name is None
    assert model.status is None


# =============================================================================
# REPOSITORY CALLED ONCE
# =============================================================================


def test_agent_repo_called_once(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict]
        )
    )

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    mock_agent_repo.get_work_locations_by_contract_id.assert_called_once()


# =============================================================================
# CONTRACT ID FORWARDED
# =============================================================================


def test_agent_contract_id_forwarded(
    mock_agent_repo,
    sample_agent_dict,
):
    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        make_repo_result(
            items=[sample_agent_dict]
        )
    )

    agent_get_contract_locations(
        contract_id="CONT-2000",
        filters=None,
        limit=10,
        cursor=None,
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert kwargs["contract_id"] == "CONT-2000"
