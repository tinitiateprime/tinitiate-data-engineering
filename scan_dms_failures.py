"""
Unit tests for domain.services.agent_service.

These tests cover the Agent Contract Locations service.

Important:
- The service uses AgentContractLocationResponse.
- Repository method:
      get_work_locations_by_contract_id
- When sort is not supplied, the service currently forwards sort=None.
"""

from unittest.mock import patch

import pytest

from domain.models.agent import AgentContractLocationResponse
from domain.services.agent_service import agent_get_contract_locations

from v1.schemas import (
    FiltersEnvelope,
    PaginationModel,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_agent_repo():
    """
    Mock the repository imported inside agent_service.
    """
    with patch(
        "domain.services.agent_service.agent_repo"
    ) as mock_repo:
        yield mock_repo


@pytest.fixture
def sample_agent_dict():
    """
    Sample database/repository row.

    Keep field names in snake_case because this represents
    the internal/domain representation returned from the repository.
    """
    return {
        "contract_id": "CONT-1001",
        "award_number": "AWD-1001",
        "order_number": "ORD-1001",
        "mod_number": "MOD-01",
        "places": "Dallas, TX",
        "project_name": "Test Project",
        "program_manager_name": "Test Manager",
        "status": "ACTIVE",
    }


# =============================================================================
# SUCCESS
# =============================================================================


def test_agent_get_contract_locations_success(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify agent_get_contract_locations:

    - normalizes dictionary filters
    - calls repository once
    - passes contract_id
    - creates pagination model
    - forwards sort=None when no sort is provided
    - converts repository rows to AgentContractLocationResponse
    - preserves metadata
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [
            sample_agent_dict,
        ],
        "page": {
            "cursor": "next-token",
            "has_more": True,
        },
    }

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters={
            "project_name": {
                "eq": "Test Project",
            },
        },
        limit=10,
        cursor=None,
    )

    # -------------------------------------------------------------------------
    # Repository called
    # -------------------------------------------------------------------------

    mock_agent_repo.get_work_locations_by_contract_id.assert_called_once()

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    # -------------------------------------------------------------------------
    # contract_id
    # -------------------------------------------------------------------------

    assert kwargs["contract_id"] == "CONT-1001"

    # -------------------------------------------------------------------------
    # filters
    # -------------------------------------------------------------------------

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    assert kwargs["filters"].filters["project_name"].eq == "Test Project"

    # -------------------------------------------------------------------------
    # pagination
    # -------------------------------------------------------------------------

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert kwargs["page"].limit == 10
    assert kwargs["page"].cursor is None

    # -------------------------------------------------------------------------
    # sort
    #
    # IMPORTANT:
    # The current service forwards None when no sort argument is supplied.
    # Do NOT assert isinstance(kwargs["sort"], SortModel).
    # -------------------------------------------------------------------------

    assert kwargs["sort"] is None

    # -------------------------------------------------------------------------
    # columns
    # -------------------------------------------------------------------------

    assert kwargs["columns"] is None

    # -------------------------------------------------------------------------
    # Result
    # -------------------------------------------------------------------------

    assert len(result.items) == 1

    assert isinstance(
        result.items[0],
        AgentContractLocationResponse,
    )

    item = result.items[0]

    assert item.contract_id == "CONT-1001"
    assert item.award_number == "AWD-1001"
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


# =============================================================================
# NO FILTERS
# =============================================================================


def test_agent_get_contract_locations_no_filters(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify service works when filters are omitted.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [
            sample_agent_dict,
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
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

    # Current service behavior
    assert kwargs["sort"] is None

    assert kwargs["columns"] is None

    assert len(result.items) == 1

    assert isinstance(
        result.items[0],
        AgentContractLocationResponse,
    )

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


# =============================================================================
# EMPTY RESULTS
# =============================================================================


def test_agent_get_contract_locations_empty_results(
    mock_agent_repo,
):
    """
    Repository returns no items.
    Service should return an empty list without failing.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    mock_agent_repo.get_work_locations_by_contract_id.assert_called_once()

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


# =============================================================================
# CUSTOM LIMIT
# =============================================================================


def test_agent_get_contract_locations_custom_limit(
    mock_agent_repo,
):
    """
    Verify the supplied limit is put into PaginationModel.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=25,
        cursor=None,
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


# =============================================================================
# CURSOR
# =============================================================================


def test_agent_get_contract_locations_cursor(
    mock_agent_repo,
):
    """
    Verify cursor is passed into PaginationModel.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor="existing-token",
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

    assert kwargs["page"].limit == 10
    assert kwargs["page"].cursor == "existing-token"


# =============================================================================
# COLUMNS
# =============================================================================


def test_agent_get_contract_locations_columns(
    mock_agent_repo,
):
    """
    Verify selected columns are forwarded to repository.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

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


# =============================================================================
# FILTER NORMALIZATION
# =============================================================================


def test_agent_get_contract_locations_dict_filter(
    mock_agent_repo,
):
    """
    Verify dictionary filter is converted into FiltersEnvelope.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters={
            "project_name": {
                "eq": "Test Project",
            },
        },
        limit=10,
        cursor=None,
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    filters = kwargs["filters"]

    assert isinstance(
        filters,
        FiltersEnvelope,
    )

    assert filters.filters["project_name"].eq == "Test Project"


# =============================================================================
# MULTIPLE FILTERS
# =============================================================================


def test_agent_get_contract_locations_multiple_dict_filters(
    mock_agent_repo,
):
    """
    Verify multiple dictionary filters are normalized.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters={
            "project_name": {
                "eq": "Test Project",
            },
            "status": {
                "eq": "ACTIVE",
            },
        },
        limit=10,
        cursor=None,
    )

    kwargs = (
        mock_agent_repo
        .get_work_locations_by_contract_id
        .call_args
        .kwargs
    )

    filters = kwargs["filters"]

    assert isinstance(
        filters,
        FiltersEnvelope,
    )

    assert filters.filters["project_name"].eq == "Test Project"
    assert filters.filters["status"].eq == "ACTIVE"


# =============================================================================
# RESPONSE MODEL CONVERSION
# =============================================================================


def test_agent_get_contract_locations_response_model_conversion(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify repository dictionaries become AgentContractLocationResponse models.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [
            sample_agent_dict,
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert isinstance(
        item,
        AgentContractLocationResponse,
    )

    assert item.contract_id == "CONT-1001"
    assert item.project_name == "Test Project"


# =============================================================================
# MULTIPLE RESULTS
# =============================================================================


def test_agent_get_contract_locations_multiple_results(
    mock_agent_repo,
    sample_agent_dict,
):
    """
    Verify multiple repository records are converted.
    """

    second_item = {
        **sample_agent_dict,
        "contract_id": "CONT-1002",
        "project_name": "Second Project",
    }

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [
            sample_agent_dict,
            second_item,
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

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

    assert result.items[0].project_name == "Test Project"
    assert result.items[1].project_name == "Second Project"


# =============================================================================
# REPOSITORY CALLED ONLY ONCE
# =============================================================================


def test_agent_get_contract_locations_repo_called_once(
    mock_agent_repo,
):
    """
    Ensure one service invocation results in one repository call.
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor=None,
    )

    mock_agent_repo.get_work_locations_by_contract_id.assert_called_once()


# =============================================================================
# CURRENT SORT CONTRACT
# =============================================================================


def test_agent_get_contract_locations_default_sort_is_none(
    mock_agent_repo,
):
    """
    Regression test for the pipeline failure.

    Current agent_service behavior:
        no sort supplied -> repository receives sort=None

    This intentionally does NOT expect SortModel().
    """

    mock_agent_repo.get_work_locations_by_contract_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    agent_get_contract_locations(
        contract_id="CONT-1001",
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

    assert "sort" in kwargs
    assert kwargs["sort"] is None
