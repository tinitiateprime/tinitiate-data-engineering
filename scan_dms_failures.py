from unittest.mock import MagicMock, ANY

import pytest

from core.filters import FiltersEnvelope, FilterOps, SortModel
from core.pagination import PaginationModel

from domain.services.po_funding_detail_service import (
    search_po_funding_detail,
    get_po_funding_detail_by_project,
)


# ============================================================
# SAMPLE DATA
# ============================================================

@pytest.fixture
def sample_po_funding_detail_dict():
    return {
        "project_id": "P-1001",
        "vendor_name": "Test Vendor",
        "proj_start_dt": "2026-01-01",
        "proj_end_dt": "2026-12-31",
        "po_id": "0000000014",
        "po_release_no": 0,
        "po_line_no": 1,
        "vendor_id": "V007031",
        "order_date": "2012-08-16T00:00:00",
        "po_line_desc": "Test PO Line",
        "po_text": "Test PO Text",
        "ordered_qty": 10,
        "po_line_total_amt": 1000.00,
        "vouchered_amt": 500.00,
        "remaining": 500.00,
    }


# ============================================================
# MOCK REPOSITORY
# ============================================================

@pytest.fixture
def mock_po_funding_detail_repo(monkeypatch):
    repo = MagicMock()

    monkeypatch.setattr(
        "domain.services.po_funding_detail_service.po_funding_detail_repo",
        repo,
    )

    return repo


# ============================================================
# SEARCH TESTS
# ============================================================

def test_search_po_funding_detail_no_filters(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify search works when filters=None.
    """

    mock_po_funding_detail_repo.get_po_funding_detail.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = search_po_funding_detail(
        filters=None,
    )

    assert len(result.items) == 1
    assert result.items[0].project_id == "P-1001"
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_po_funding_detail_repo.get_po_funding_detail.assert_called_once()

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail
        .call_args
        .kwargs
    )

    # None remains valid based on current service implementation
    assert kwargs["filters"] is None

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )


def test_search_po_funding_detail_with_dict_filters(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify dictionary filters are converted to FiltersEnvelope.
    """

    mock_po_funding_detail_repo.get_po_funding_detail.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    filters = {
        "vendor_name": {
            "eq": "Test Vendor",
        }
    }

    result = search_po_funding_detail(
        filters=filters,
    )

    assert len(result.items) == 1

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail
        .call_args
        .kwargs
    )

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )


def test_search_po_funding_detail_with_existing_envelope(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify existing FiltersEnvelope is passed through.
    """

    mock_po_funding_detail_repo.get_po_funding_detail.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    filters = FiltersEnvelope(
        filters={
            "vendor_name": FilterOps(
                eq="Test Vendor"
            )
        }
    )

    result = search_po_funding_detail(
        filters=filters,
    )

    assert len(result.items) == 1

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail
        .call_args
        .kwargs
    )

    assert kwargs["filters"] == filters


def test_search_po_funding_detail_empty(
    mock_po_funding_detail_repo,
):
    """
    Verify empty repository response.
    """

    mock_po_funding_detail_repo.get_po_funding_detail.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = search_po_funding_detail()

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_search_po_funding_detail_pagination_and_columns(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify pagination, columns and sort are passed to repository.
    """

    mock_po_funding_detail_repo.get_po_funding_detail.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": "next-cursor",
            "has_more": True,
        },
    }

    page = PaginationModel(
        limit=25,
        cursor="current-cursor",
    )

    sort = SortModel(
        field="vendor_name",
        order="asc",
    )

    columns = [
        "project_id",
        "vendor_name",
    ]

    result = search_po_funding_detail(
        filters=None,
        page=page,
        sort=sort,
        columns=columns,
    )

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail
        .call_args
        .kwargs
    )

    assert kwargs["page"] == page
    assert kwargs["sort"] == sort
    assert kwargs["columns"] == columns

    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True


# ============================================================
# GET BY PROJECT TESTS
# ============================================================

def test_get_po_funding_detail_by_project_success(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify retrieval of PO Funding Detail records by project_id.
    """

    expected_project_id = "P-1001"

    sample_po_funding_detail_dict["project_id"] = (
        expected_project_id
    )

    second_record = sample_po_funding_detail_dict.copy()
    second_record["vendor_name"] = "Test Vendor - Detail 2"

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.return_value = {
        "items": [
            sample_po_funding_detail_dict,
            second_record,
        ],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_po_funding_detail_by_project(
        expected_project_id,
    )

    assert len(result.items) == 2
    assert result.items[0].project_id == "P-1001"
    assert result.items[1].vendor_name == "Test Vendor - Detail 2"

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.assert_called_once()

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail_by_project_id
        .call_args
        .kwargs
    )

    assert kwargs["project_id"] == expected_project_id

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    assert kwargs["columns"] is None


def test_get_po_funding_detail_by_project_not_found(
    mock_po_funding_detail_repo,
):
    """
    Verify unknown project_id returns empty response.
    """

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_po_funding_detail_by_project(
        "NON-EXISTENT",
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_get_po_funding_detail_by_project_empty_project_id(
    mock_po_funding_detail_repo,
):
    """
    Verify blank project_id returns empty response
    without calling repository.
    """

    result = get_po_funding_detail_by_project(
        "",
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.assert_not_called()


def test_get_po_funding_detail_by_project_pagination_and_columns(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify page, sort and columns are passed to repository.

    IMPORTANT:
    The current service takes page=PaginationModel,
    not limit/cursor arguments directly.
    """

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": "next-cursor",
            "has_more": True,
        },
    }

    page = PaginationModel(
        limit=25,
        cursor="current-cursor",
    )

    sort = SortModel(
        field="vendor_name",
        order="asc",
    )

    columns = [
        "project_id",
        "vendor_name",
    ]

    result = get_po_funding_detail_by_project(
        project_id="P-1001",
        page=page,
        sort=sort,
        columns=columns,
    )

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.assert_called_once_with(
        project_id="P-1001",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True


def test_get_po_funding_detail_by_project_default_page_and_sort(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify service creates default page and default sort.
    """

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = get_po_funding_detail_by_project(
        project_id="P-1001",
    )

    assert len(result.items) == 1

    kwargs = (
        mock_po_funding_detail_repo
        .get_po_funding_detail_by_project_id
        .call_args
        .kwargs
    )

    assert kwargs["project_id"] == "P-1001"

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    # Your service defaults to:
    # SortModel(field="order_date", order="desc")
    assert kwargs["sort"].field == "order_date"
    assert kwargs["sort"].order == "desc"

    assert kwargs["columns"] is None


def test_get_po_funding_detail_by_project_metadata_has_more_default(
    mock_po_funding_detail_repo,
    sample_po_funding_detail_dict,
):
    """
    Verify has_more defaults to False if repository
    doesn't return it.
    """

    mock_po_funding_detail_repo.get_po_funding_detail_by_project_id.return_value = {
        "items": [sample_po_funding_detail_dict],
        "page": {
            "cursor": "xyz",
        },
    }

    result = get_po_funding_detail_by_project(
        "P-1001",
    )

    assert result.metadata.cursor == "xyz"
    assert result.metadata.has_more is False
