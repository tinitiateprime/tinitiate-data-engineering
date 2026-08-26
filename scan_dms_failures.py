"""
Unit tests for domain.services.agent_service.

These tests cover:
    - agent_get_contract_locations
    - get_work_locations_by_contract_id_details

IMPORTANT:
The Agent domain model is AgentContractLocationResponse.
Do NOT import/use the old AgentResponse model.
"""

from unittest.mock import ANY, patch

import pytest

from domain.models.agent import AgentContractLocationResponse
from domain.services.agent_service import (
    agent_get_contract_locations,
    get_work_locations_by_contract_id_details,
)
from v1.schemas import (
    FilterOps,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_agent_repo():
    """
    Patch the repository object used inside agent_service.
    """
    with patch(
        "domain.services.agent_service.agent_repo"
    ) as mock_repo:
        yield mock_repo


@pytest.fixture
def sample_agent_dict():
    """
    Valid database-style row for AgentContractLocationResponse.

    These are the fields belonging to the Agent contract-location API.
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
    """
    Second valid record used by list tests.
    """
    return {
        "contract_id": "CONT-1002",
        "award_number": "AMD-1002",
        "order_number": "ORD-1002",
        "mod_number": "MOD-02",
        "places": "San Antonio, TX",
        "project_name": "Second Project",
        "program_manager_name": "Second Manager",
        "status": "ACTIVE",
    }


def _repo_result(
    items=None,
    cursor=None,
    has_more=False,
):
    """
    Standard mocked repository response.
    """
    return {
        "items": items or [],
        "page": {
            "cursor": cursor,
            "has_more": has_more,
        },
    }


# =============================================================================
# agent_get_contract_locations
# =============================================================================


def test_agent_get_contract_locations_success(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify agent_get_contract_locations:

    - normalizes dict filters
    - calls repository
    - converts DB rows to AgentContractLocationResponse
    - preserves pagination metadata
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
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

    # -------------------------------------------------------------------------
    # Contract ID
    # -------------------------------------------------------------------------

    assert kwargs["contract_id"] == "CONT-1001"

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert kwargs["page"].limit == 10
    assert kwargs["page"].cursor is None

    # -------------------------------------------------------------------------
    # Sort
    # -------------------------------------------------------------------------

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------

    assert kwargs["columns"] is None

    # -------------------------------------------------------------------------
    # Result
    # -------------------------------------------------------------------------

    assert result is not None
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

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    assert result.metadata.has_more is True
    assert result.metadata.cursor == "next-token"


def test_agent_get_contract_locations_with_filters_envelope(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Existing FiltersEnvelope should pass through the service correctly.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
            cursor=None,
            has_more=False,
        )
    )

    filters = FiltersEnvelope(
        filters={
            "project_name": FilterOps(
                eq="Test Project",
            ),
        }
    )

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=filters,
        limit=25,
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


def test_agent_get_contract_locations_without_filters(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify None filters are supported.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
            cursor=None,
            has_more=False,
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


def test_agent_get_contract_locations_empty(
    mock_agent_repo,
):
    """
    Repository returning no rows should produce an empty result.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
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

    assert result is not None
    assert result.items == []

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_agent_get_contract_locations_multiple_rows(
    mock_agent_repo,
    sample_agent_dict,
    second_agent_dict,
):
    """
    Verify multiple repository rows are converted to Pydantic models.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[
                sample_agent_dict,
                second_agent_dict,
            ],
            cursor=None,
            has_more=False,
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


def test_agent_get_contract_locations_default_limit(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify service creates a PaginationModel.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
        )
    )

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
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

    assert kwargs["page"].limit > 0


def test_agent_get_contract_locations_cursor(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify supplied cursor reaches repository PaginationModel.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
        )
    )

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=20,
        cursor="current-token",
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    assert kwargs["page"].limit == 20
    assert kwargs["page"].cursor == "current-token"


def test_agent_get_contract_locations_columns(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify selected columns reach the repository.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
        )
    )

    columns = [
        "contract_id",
        "project_name",
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


def test_agent_get_contract_locations_custom_sort(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify a supplied SortModel is forwarded.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
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
# get_work_locations_by_contract_id_details
# =============================================================================


def test_get_work_locations_by_contract_id_details_success(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify detail service returns AgentContractLocationResponse objects.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
            cursor=None,
            has_more=False,
        )
    )

    result = get_work_locations_by_contract_id_details(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert result is not None
    assert len(result.items) == 1

    assert isinstance(
        result.items[0],
        AgentContractLocationResponse,
    )

    assert result.items[0].contract_id == "CONT-1001"
    assert result.items[0].project_name == "Test Project"
    assert result.items[0].places == "Dallas, TX"


def test_get_work_locations_by_contract_id_details_empty(
    mock_agent_repo,
):
    """
    Detail lookup with no repository rows should return empty items.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[],
            cursor=None,
            has_more=False,
        )
    )

    result = get_work_locations_by_contract_id_details(
        contract_id="CONT-9999",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert result is not None
    assert result.items == []


def test_get_work_locations_by_contract_id_details_filter_dict(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify dictionary filters are normalized to FiltersEnvelope.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
        )
    )

    result = get_work_locations_by_contract_id_details(
        contract_id="CONT-1001",
        filters={
            "status": {
                "eq": "ACTIVE",
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


def test_get_work_locations_by_contract_id_details_columns(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify details lookup accepts selected columns.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = (
        _repo_result(
            items=[sample_agent_dict],
        )
    )

    columns = [
        "contract_id",
        "places",
        "project_name",
    ]

    get_work_locations_by_contract_id_details(
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
# Model conversion
# =============================================================================


def test_agent_service_database_row_model_validation(
    sample_agent_dict,
):
    """
    Verify the database-style snake_case payload is valid for the
    actual Agent model.
    """

    result = AgentContractLocationResponse.model_validate(
        sample_agent_dict
    )

    assert result.contract_id == "CONT-1001"
    assert result.award_number == "AMD-1001"
    assert result.order_number == "ORD-1001"
    assert result.mod_number == "MOD-01"
    assert result.places == "Dallas, TX"
    assert result.project_name == "Test Project"
    assert result.program_manager_name == "Test Manager"
    assert result.status == "ACTIVE"


def test_agent_service_api_alias_model_validation():
    """
    Verify API camelCase aliases are accepted.
    """

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

    result = AgentContractLocationResponse.model_validate(
        payload
    )

    assert result.contract_id == "CONT-1001"
    assert result.award_number == "AMD-1001"
    assert result.order_number == "ORD-1001"
    assert result.mod_number == "MOD-01"
    assert result.project_name == "Test Project"
    assert result.program_manager_name == "Test Manager"
    assert result.status == "ACTIVE"


def test_agent_service_model_optional_fields():
    """
    Only contract_id is required by AgentContractLocationResponse.
    """

    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
    )

    assert result.contract_id == "CONT-1001"
    assert result.award_number is None
    assert result.order_number is None
    assert result.mod_number is None
    assert result.places is None
    assert result.project_name is None
    assert result.program_manager_name is None
    assert result.status is None
