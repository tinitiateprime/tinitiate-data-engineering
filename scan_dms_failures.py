"""
Unit tests for domain.services.employee_profile_complete_service.

IMPORTANT:
Employee detail lookup uses `empl_id`.
Do NOT use `employee_key` as the lookup argument.

employee_key is still a field in the returned data and can still be used
internally for pagination/keyset purposes where applicable.
"""

from unittest.mock import MagicMock, patch

import pytest

from domain.services import employee_profile_complete_service

from v1.schemas import (
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ============================================================
# TEST DATA
# ============================================================

EMPLOYEE_DATA = {
    "employee_key": "EMPLOYEE-KEY-001",
    "email_key": "test_email_key",
    "empl_id": "EMP-1001",
    "my_id": "test_my_id",
    "sotv_employee_id": "test_sotv_employee_id",
    "first_name": "John",
    "last_name": "Doe",
    "mid_name": "A",
    "employee_name": "John Doe",
    "job_title": "Engineer",
    "org_id": "ORG1",
    "dept_name": "Engineering",
    "location": "New York",
    "mgr_name": "Jane Doe",
    "mgr_empl_id": "EMP-2001",
    "hire_date": "2026-01-01",
    "clearance_status": "ACTIVE",
    "clearance_eligibility": "SECRET",
    "sotv_headline": "Engineer",
    "certifications": {"test": "value"},
    "certification_names": ["AWS"],
    "certification_count": 1,
    "skills": {"Python": "Advanced"},
    "skill_names": ["Python"],
    "skill_count": 1,
    "education": {"degree": "BS"},
    "education_count": 1,
    "languages": ["English"],
    "language_count": 1,
}


# ============================================================
# HELPERS
# ============================================================

def make_repo_result(
    items=None,
    cursor=None,
    has_more=False,
):
    """
    Create the dictionary returned by the repository layer.
    """

    return {
        "items": items or [],
        "page": {
            "cursor": cursor,
            "has_more": has_more,
        },
    }


# ============================================================
# SEARCH EMPLOYEE PROFILE COMPLETES
# ============================================================

@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_success(mock_repo):
    """
    Search returns employee data successfully.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA],
        cursor=None,
        has_more=False,
    )

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes()
    )

    assert result is not None
    assert len(result.items) == 1

    assert result.items[0].empl_id == "EMP-1001"

    mock_repo.assert_called_once()


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_empty(mock_repo):
    """
    Search with no matching employees should return an empty list.
    """

    mock_repo.return_value = make_repo_result(
        items=[],
        cursor=None,
        has_more=False,
    )

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes()
    )

    assert result is not None
    assert result.items == []

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_with_filters(mock_repo):
    """
    Dictionary filters should be converted to FiltersEnvelope.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA]
    )

    filters = {
        "empl_id": {
            "eq": "EMP-1001"
        }
    }

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes(
            filters=filters,
        )
    )

    assert len(result.items) == 1

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_filters_none(mock_repo):
    """
    filters=None should become an empty FiltersEnvelope.
    """

    mock_repo.return_value = make_repo_result(items=[])

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes(
            filters=None,
        )
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_filters_envelope(mock_repo):
    """
    Existing FiltersEnvelope should pass through.
    """

    mock_repo.return_value = make_repo_result(items=[])

    filters = FiltersEnvelope(filters={})

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes(
            filters=filters,
        )
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["filters"] is filters


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_page_defaults(mock_repo):
    """
    Default page must be created when page is not supplied.
    """

    mock_repo.return_value = make_repo_result(items=[])

    employee_profile_complete_service.search_employee_profile_completes()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["page"],
        PaginationModel,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_sort_defaults(mock_repo):
    """
    Default sort must be empl_id ASC based on current service.
    """

    mock_repo.return_value = make_repo_result(items=[])

    employee_profile_complete_service.search_employee_profile_completes()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["sort"],
        SortModel,
    )

    assert call_kwargs["sort"].field == "empl_id"
    assert call_kwargs["sort"].order == "asc"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_custom_page(mock_repo):
    """
    Custom PaginationModel should pass through.
    """

    mock_repo.return_value = make_repo_result(items=[])

    page = PaginationModel(
        limit=25,
        cursor="TEST-CURSOR",
    )

    employee_profile_complete_service.search_employee_profile_completes(
        page=page,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["page"] is page
    assert call_kwargs["page"].limit == 25
    assert call_kwargs["page"].cursor == "TEST-CURSOR"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_custom_sort(mock_repo):
    """
    Custom sorting should pass through.
    """

    mock_repo.return_value = make_repo_result(items=[])

    sort = SortModel(
        field="last_name",
        order="desc",
    )

    employee_profile_complete_service.search_employee_profile_completes(
        sort=sort,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["sort"] is sort
    assert call_kwargs["sort"].field == "last_name"
    assert call_kwargs["sort"].order == "desc"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_columns(mock_repo):
    """
    Selected columns should be forwarded to repository.
    """

    mock_repo.return_value = make_repo_result(items=[])

    columns = [
        "empl_id",
        "first_name",
        "last_name",
    ]

    employee_profile_complete_service.search_employee_profile_completes(
        columns=columns,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_metadata(mock_repo):
    """
    Repository pagination metadata should be returned.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA],
        cursor="NEXT-CURSOR",
        has_more=True,
    )

    result = (
        employee_profile_complete_service
        .search_employee_profile_completes()
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "NEXT-CURSOR"
    assert result.metadata.has_more is True


# ============================================================
# GET EMPLOYEE PROFILE COMPLETE DETAILS
#
# IMPORTANT:
#
# Correct:
#
# get_employee_profile_complete_details(
#     empl_id="EMP-1001"
# )
#
# WRONG:
#
# get_employee_profile_complete_details(
#     employee_key="EMPLOYEE-KEY-001"
# )
#
# ============================================================

@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_success(mock_repo):
    """
    Detail lookup must use empl_id.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA],
        cursor=None,
        has_more=False,
    )

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="EMP-1001",
        )
    )

    assert result is not None

    assert len(result.items) == 1

    assert result.items[0].empl_id == "EMP-1001"

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    # THIS IS THE IMPORTANT ASSERTION
    assert call_kwargs["empl_id"] == "EMP-1001"

    # employee_key must NOT be used as repo argument
    assert "employee_key" not in call_kwargs


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_not_found(mock_repo):
    """
    Valid empl_id with no matching DB row returns empty items.
    """

    mock_repo.return_value = make_repo_result(
        items=[],
        cursor=None,
        has_more=False,
    )

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="EMP-9999",
        )
    )

    assert result is not None
    assert result.items == []

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-9999"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_missing_id(mock_repo):
    """
    Missing empl_id should return empty response without calling repo.
    """

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="",
        )
    )

    assert result is not None
    assert result.items == []

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_not_called()


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_none_id(mock_repo):
    """
    None empl_id should return empty response.
    """

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id=None,
        )
    )

    assert result.items == []

    mock_repo.assert_not_called()


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_with_dict_filters(
    mock_repo,
):
    """
    Dictionary filters must become FiltersEnvelope.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA],
    )

    filters = {
        "org_id": {
            "eq": "ORG1"
        }
    }

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="EMP-1001",
            filters=filters,
        )
    )

    assert len(result.items) == 1

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_none_filters(
    mock_repo,
):
    """
    filters=None must become an empty FiltersEnvelope.
    """

    mock_repo.return_value = make_repo_result(items=[])

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="EMP-1001",
            filters=None,
        )
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_filters_envelope(
    mock_repo,
):
    """
    Existing FiltersEnvelope should pass through.
    """

    mock_repo.return_value = make_repo_result(items=[])

    filters = FiltersEnvelope(filters={})

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=filters,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"
    assert call_kwargs["filters"] is filters


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_limit(
    mock_repo,
):
    """
    Limit should be converted into PaginationModel.
    """

    mock_repo.return_value = make_repo_result(items=[])

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
        limit=25,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["page"],
        PaginationModel,
    )

    assert call_kwargs["page"].limit == 25


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_cursor(
    mock_repo,
):
    """
    Cursor should be passed through PaginationModel.
    """

    mock_repo.return_value = make_repo_result(items=[])

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
        limit=10,
        cursor="NEXT-CURSOR",
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["page"].limit == 10
    assert call_kwargs["page"].cursor == "NEXT-CURSOR"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_columns(
    mock_repo,
):
    """
    Selected columns should be forwarded.
    """

    mock_repo.return_value = make_repo_result(items=[])

    columns = [
        "empl_id",
        "first_name",
        "last_name",
    ]

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
        columns=columns,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"
    assert call_kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_sort(
    mock_repo,
):
    """
    Sort should pass through to repo.
    """

    mock_repo.return_value = make_repo_result(items=[])

    sort = SortModel(
        field="empl_id",
        order="asc",
    )

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
        sort=sort,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"
    assert call_kwargs["sort"] is sort


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_metadata(
    mock_repo,
):
    """
    Pagination metadata should be mapped correctly.
    """

    mock_repo.return_value = make_repo_result(
        items=[EMPLOYEE_DATA],
        cursor="NEXT-CURSOR",
        has_more=True,
    )

    result = (
        employee_profile_complete_service
        .get_employee_profile_complete_details(
            empl_id="EMP-1001",
        )
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "NEXT-CURSOR"
    assert result.metadata.has_more is True


# ============================================================
# REGRESSION TEST
# ============================================================

def test_get_employee_profile_complete_details_signature_uses_empl_id():
    """
    Regression protection for the GitLab issue.

    Service contract must be:

        get_employee_profile_complete_details(
            empl_id=...
        )

    NOT:

        get_employee_profile_complete_details(
            employee_key=...
        )
    """

    import inspect

    signature = inspect.signature(
        employee_profile_complete_service
        .get_employee_profile_complete_details
    )

    assert "empl_id" in signature.parameters

    assert "employee_key" not in signature.parameters


# ============================================================
# REPOSITORY CALL CONTRACT
# ============================================================

@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_complete_by_id"
)
def test_detail_service_passes_empl_id_to_repo(mock_repo):
    """
    Explicitly verify the service -> repository contract.
    """

    mock_repo.return_value = make_repo_result(items=[])

    employee_profile_complete_service.get_employee_profile_complete_details(
        empl_id="EMP-1001",
    )

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    assert "employee_key" not in call_kwargs
