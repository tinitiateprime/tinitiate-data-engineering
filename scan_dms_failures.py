# main-function/tests/unit/domain/services/test_project_financial_service.py

from unittest.mock import ANY, patch

import pytest

from domain.models import ProjectFinancialResponse
from domain.services.project_financial_service import (
    get_project_financial_details,
    search_project_financials,
)
from v1.schemas import (
    FilterOps,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_project_financial_repo():
    """
    Mock the repository imported inside project_financial_service.
    """
    with patch(
        "domain.services.project_financial_service.project_financial_repo"
    ) as mock_repo:
        yield mock_repo


@pytest.fixture
def sample_project_financial_dict():
    """
    Sample record representing data returned by
    gold.project_financials_source_vw.
    """
    return {
        "proj_id": "P-1001",
        "cust_name": "Test Customer",
        "proj_start_dt": "2026-01-01",
        "proj_end_dt": "2026-12-31",
        "s_proj_rpt_dc": "ACTIVE",
        "proj_name": "Test Project",
        "org_id": "ORG-100",
        "prime_contr_id": "CONT-100",
        "active_fl": "Y",
        "proj_type_dc": "FIXED_PRICE",
        "proj_mgr_name": "Test Manager",
        "lvl_no": 1,
        "value_total_amount": 100000.00,
        "project_value_cost": 70000.00,
        "project_value_fee": 30000.00,
        "proj_f_tot_amt": 100000.00,
        "cost_funded": 65000.00,
        "fee_funded": 25000.00,
        "total_billed": 50000.00,
        "billed_cost": 35000.00,
        "billed_fee": 15000.00,
        "open_billing_detail_amt": 5000.00,
        "open_commit_amt": 10000.00,
    }


# ---------------------------------------------------------------------------
# search_project_financials tests
# ---------------------------------------------------------------------------

def test_search_project_financials_success(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify search_project_financials normalizes filters,
    invokes the repository, converts rows to Pydantic models,
    and returns pagination metadata.
    """

    expected_proj_id = "P-1001"
    sample_project_financial_dict["proj_id"] = expected_proj_id

    mock_project_financial_repo.get_project_financials.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": "next-token",
            "has_more": True,
        },
    }

    result = search_project_financials(
        filters={
            "proj_name": {
                "eq": "Test Project",
            }
        },
        page=PaginationModel(limit=10),
    )

    # Verify repository arguments
    kwargs = (
        mock_project_financial_repo
        .get_project_financials
        .call_args
        .kwargs
    )

    assert isinstance(kwargs["filters"], FiltersEnvelope)
    assert kwargs["filters"].filters["proj_name"].eq == "Test Project"

    assert isinstance(kwargs["page"], PaginationModel)
    assert kwargs["page"].limit == 10

    assert isinstance(kwargs["sort"], SortModel)
    assert kwargs["columns"] is None

    # Verify returned service models
    assert len(result.items) == 1
    assert isinstance(result.items[0], ProjectFinancialResponse)
    assert result.items[0].proj_id == expected_proj_id
    assert result.items[0].proj_name == "Test Project"

    # Verify metadata
    assert result.metadata.has_more is True
    assert result.metadata.cursor == "next-token"


def test_search_project_financials_with_envelope(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify an existing FiltersEnvelope is passed directly
    to the repository.
    """

    mock_project_financial_repo.get_project_financials.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    filters = FiltersEnvelope(
        filters={
            "proj_name": FilterOps(
                eq="Test Project",
            )
        }
    )

    result = search_project_financials(
        filters=filters,
    )

    mock_project_financial_repo.get_project_financials.assert_called_once_with(
        filters=filters,
        sort=ANY,
        page=ANY,
        columns=None,
    )

    assert len(result.items) == 1
    assert result.metadata.applied_filters == filters


def test_search_project_financials_empty(
    mock_project_financial_repo,
):
    """
    Verify the service returns an empty response when
    the repository returns no records.
    """

    mock_project_financial_repo.get_project_financials.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = search_project_financials(
        filters={
            "active_fl": {
                "eq": "Y",
            }
        },
        page=PaginationModel(limit=10),
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_search_project_financials_no_filters(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify None filters are converted into an empty
    FiltersEnvelope and metadata.applied_filters is None.
    """

    mock_project_financial_repo.get_project_financials.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = search_project_financials(
        filters=None,
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financials
        .call_args
        .kwargs
    )

    assert isinstance(kwargs["filters"], FiltersEnvelope)
    assert kwargs["filters"].filters == {}

    assert result.metadata.applied_filters is None


def test_search_project_financials_custom_columns(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify selected columns are passed to the repository.
    """

    mock_project_financial_repo.get_project_financials.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    columns = [
        "proj_id",
        "proj_name",
        "cust_name",
    ]

    search_project_financials(
        filters=None,
        columns=columns,
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financials
        .call_args
        .kwargs
    )

    assert kwargs["columns"] == columns


# ---------------------------------------------------------------------------
# get_project_financial_details tests
# ---------------------------------------------------------------------------

def test_get_project_financial_details_success(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify retrieval of project financial records by proj_id.
    """

    expected_proj_id = "P-1001"
    sample_project_financial_dict["proj_id"] = expected_proj_id

    second_record = sample_project_financial_dict.copy()
    second_record["proj_name"] = "Test Project - Detail 2"

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [
            sample_project_financial_dict,
            second_record,
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_project_financial_details(
        expected_proj_id
    )

    mock_project_financial_repo.get_project_financial_by_id.assert_called_once_with(
        proj_id=expected_proj_id,
        filters=ANY,
        page=ANY,
        columns=None,
        sort=None,
    )

    assert len(result.items) == 2
    assert all(
        isinstance(item, ProjectFinancialResponse)
        for item in result.items
    )

    assert result.items[0].proj_id == expected_proj_id
    assert result.items[1].proj_id == expected_proj_id
    assert result.metadata.has_more is False


def test_get_project_financial_details_found(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify a valid proj_id returns a validated response.
    """

    expected_proj_id = "P-1001"
    sample_project_financial_dict["proj_id"] = expected_proj_id

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_project_financial_details(
        expected_proj_id
    )

    assert len(result.items) == 1
    assert isinstance(
        result.items[0],
        ProjectFinancialResponse,
    )
    assert result.items[0].proj_id == expected_proj_id

    mock_project_financial_repo.get_project_financial_by_id.assert_called_once_with(
        proj_id=expected_proj_id,
        filters=ANY,
        page=ANY,
        columns=None,
        sort=None,
    )


def test_get_project_financial_details_not_found(
    mock_project_financial_repo,
):
    """
    Verify an unknown proj_id returns an empty response.
    """

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_project_financial_details(
        "NON-EXISTENT"
    )

    assert len(result.items) == 0
    assert result.items == []
    assert result.metadata.has_more is False


def test_get_project_financial_details_invalid_id(
    mock_project_financial_repo,
):
    """
    Verify an empty proj_id returns immediately without
    invoking the repository.
    """

    result = get_project_financial_details("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_project_financial_repo.get_project_financial_by_id.assert_not_called()


def test_get_project_financial_details_filters_normalization(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify filter normalization for dictionary, None,
    and FiltersEnvelope inputs.
    """

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    # Dictionary filter
    get_project_financial_details(
        "P-1001",
        filters={
            "proj_name": {
                "eq": "Test Project",
            }
        },
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financial_by_id
        .call_args
        .kwargs
    )

    assert isinstance(kwargs["filters"], FiltersEnvelope)
    assert (
        kwargs["filters"]
        .filters["proj_name"]
        .eq
        == "Test Project"
    )

    # None filter
    result = get_project_financial_details(
        "P-1001",
        filters=None,
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financial_by_id
        .call_args
        .kwargs
    )

    assert kwargs["filters"].filters == {}
    assert result.metadata.applied_filters is None

    # Existing envelope
    envelope = FiltersEnvelope(
        filters={
            "active_fl": FilterOps(
                eq="Y",
            )
        }
    )

    get_project_financial_details(
        "P-1001",
        filters=envelope,
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financial_by_id
        .call_args
        .kwargs
    )

    assert kwargs["filters"] == envelope


def test_get_project_financial_details_metadata_has_more_default(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify has_more defaults to False when missing from
    the repository response.
    """

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": "xyz",
        },
    }

    result = get_project_financial_details(
        "P-1001"
    )

    assert result.metadata.has_more is False
    assert result.metadata.cursor == "xyz"


def test_get_project_financial_details_pagination_and_columns(
    mock_project_financial_repo,
    sample_project_financial_dict,
):
    """
    Verify limit, cursor, columns and sort are passed
    to the repository.
    """

    mock_project_financial_repo.get_project_financial_by_id.return_value = {
        "items": [sample_project_financial_dict],
        "page": {
            "cursor": "next-cursor",
            "has_more": True,
        },
    }

    sort = SortModel(
        field="proj_name",
        order="asc",
    )

    columns = [
        "proj_id",
        "proj_name",
    ]

    result = get_project_financial_details(
        proj_id="P-1001",
        filters=None,
        limit=25,
        cursor="current-cursor",
        columns=columns,
        sort=sort,
    )

    kwargs = (
        mock_project_financial_repo
        .get_project_financial_by_id
        .call_args
        .kwargs
    )

    assert kwargs["proj_id"] == "P-1001"

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )
    assert kwargs["page"].limit == 25
    assert kwargs["page"].cursor == "current-cursor"

    assert kwargs["columns"] == columns
    assert kwargs["sort"] == sort

    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True
