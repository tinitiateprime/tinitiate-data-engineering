from unittest.mock import patch

from core.filters import FiltersEnvelope
from domain.services import employee_profile_complete_service as service


# ============================================================================
# SEARCH - existing FiltersEnvelope
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_completes",
)
def test_search_employee_profile_completes_success(
    mock_repo,
):
    existing_filters = FiltersEnvelope(filters={})

    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.search_employee_profile_completes(
        filters=existing_filters,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["filters"] is existing_filters
    assert call_kwargs["sort"] is not None
    assert call_kwargs["page"] is not None


# ============================================================================
# SEARCH - empty result
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_completes",
)
def test_search_employee_profile_completes_empty(
    mock_repo,
):
    existing_filters = FiltersEnvelope(filters={})

    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.search_employee_profile_completes(
        filters=existing_filters,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


# ============================================================================
# SEARCH - dict filters
# Covers missing line 30
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_completes",
)
def test_search_employee_profile_completes_dict_filters(
    mock_repo,
):
    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.search_employee_profile_completes(
        filters={},
    )

    assert result.items == []

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


# ============================================================================
# SEARCH - None filters
# Covers missing line 32
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_completes",
)
def test_search_employee_profile_completes_none_filters(
    mock_repo,
):
    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.search_employee_profile_completes(
        filters=None,
    )

    assert result.items == []

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


# ============================================================================
# DETAIL - success
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_complete_by_id",
)
def test_get_employee_profile_complete_details_success(
    mock_repo,
):
    existing_filters = FiltersEnvelope(filters={})

    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.get_employee_profile_complete_details(
        employee_key="EMP-1001",
        filters=existing_filters,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["employee_key"] == "EMP-1001"
    assert call_kwargs["filters"] is existing_filters


# ============================================================================
# DETAIL - repo returns no rows
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_complete_by_id",
)
def test_get_employee_profile_complete_details_not_found(
    mock_repo,
):
    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.get_employee_profile_complete_details(
        employee_key="EMP-9999",
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()


# ============================================================================
# DETAIL - missing employee key
# Covers missing line 63
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_complete_by_id",
)
def test_get_employee_profile_complete_details_missing_employee_key(
    mock_repo,
):
    result = service.get_employee_profile_complete_details(
        employee_key="",
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None

    mock_repo.assert_not_called()


# ============================================================================
# DETAIL - dict filters
# Covers missing line 69
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_complete_by_id",
)
def test_get_employee_profile_complete_details_dict_filters(
    mock_repo,
):
    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.get_employee_profile_complete_details(
        employee_key="EMP-1001",
        filters={},
    )

    assert result.items == []

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["employee_key"] == "EMP-1001"

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


# ============================================================================
# DETAIL - None filters
# Covers missing line 71
# ============================================================================


@patch.object(
    service.employee_profile_complete_repo,
    "get_employee_profile_complete_by_id",
)
def test_get_employee_profile_complete_details_none_filters(
    mock_repo,
):
    mock_repo.return_value = {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }

    result = service.get_employee_profile_complete_details(
        employee_key="EMP-1001",
        filters=None,
    )

    assert result.items == []

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["employee_key"] == "EMP-1001"

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )



py -m pytest tests\unit\domain\services\test_employee_profile_complete_service.py -v

py -m pytest tests\unit\domain\services\test_employee_profile_complete_service.py -v --cov=domain.services.employee_profile_complete_service --cov-report=term-missing
