"""
Unit tests for EmployeeProfileComplete service.

Important:
The Employee Profile Complete details API uses:

    empl_id

NOT:

    employee_key
"""

from unittest.mock import patch

from domain.models.employee_profile_complete import (
    EmployeeProfileCompleteResponse,
    EmployeeProfileCompleteSearchServiceResponse,
)

from domain.services.employee_profile_complete_service import (
    get_employee_profile_complete_details,
    search_employee_profile_completes,
)

from v1.schemas import (
    FilterGroup,
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# =====================================================================
# SAMPLE DATA
# =====================================================================


def _sample_employee():
    return {
        "employee_key": "EMPLOYEE-KEY-001",
        "email_key": "test@example.com",
        "empl_id": "EMP-1001",
        "my_id": "MY-1001",
        "sotv_employee_id": "SOTV-1001",
        "first_name": "Test",
        "last_name": "Employee",
        "mid_name": None,
        "employee_name": "Test Employee",
        "job_title": "Test Job",
        "org_id": "ORG1",
        "dept_name": "Test Department",
        "location": "Test Location",
        "mgr_name": "Test Manager",
        "mgr_empl_id": "EMP-2001",
        "hire_date": "2026-01-01",
        "clearance_status": "Active",
        "clearance_eligibility": "Secret",
        "sotv_headline": "Test Headline",
        "certifications": {},
        "certification_names": [],
        "certification_count": 0,
        "skills": {},
        "skill_names": [],
        "skill_count": 0,
        "education": {},
        "education_count": 0,
        "languages": [],
        "language_count": 0,
    }


def _repo_response(items=None):
    return {
        "items": items if items is not None else [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# =====================================================================
# SEARCH TESTS
# =====================================================================


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_success(
    mock_repo,
):
    mock_repo.return_value = _repo_response(
        [_sample_employee()]
    )

    result = search_employee_profile_completes(
        filters=None,
        sort=None,
        page=None,
        columns=None,
    )

    assert isinstance(
        result,
        EmployeeProfileCompleteSearchServiceResponse,
    )

    assert len(result.items) == 1

    assert isinstance(
        result.items[0],
        EmployeeProfileCompleteResponse,
    )

    assert result.items[0].empl_id == "EMP-1001"

    mock_repo.assert_called_once()


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_empty(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    result = search_employee_profile_completes(
        filters=None,
        sort=None,
        page=None,
        columns=None,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_dict_filters(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    filters = {
        "org_id": FilterOps(
            eq="ORG1"
        )
    }

    result = search_employee_profile_completes(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result.items == []

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
def test_search_employee_profile_completes_filters_envelope(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    filters = FiltersEnvelope(
        filters={
            "org_id": FilterOps(
                eq="ORG1"
            )
        }
    )

    result = search_employee_profile_completes(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["filters"] is filters


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_none_filters(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    result = search_employee_profile_completes(
        filters=None,
        sort=None,
        page=None,
        columns=None,
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
def test_search_employee_profile_completes_custom_page(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    page = PaginationModel(
        limit=25
    )

    search_employee_profile_completes(
        filters=None,
        sort=None,
        page=page,
        columns=None,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["page"].limit == 25


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo.get_employee_profile_completes"
)
def test_search_employee_profile_completes_columns(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    columns = [
        "empl_id",
        "first_name",
        "last_name",
    ]

    search_employee_profile_completes(
        filters=None,
        sort=None,
        page=None,
        columns=columns,
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["columns"] == columns


# =====================================================================
# GET DETAILS - EMPL_ID
# =====================================================================


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_success(
    mock_repo,
):
    mock_repo.return_value = _repo_response(
        [_sample_employee()]
    )

    result = get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    assert isinstance(
        result,
        EmployeeProfileCompleteSearchServiceResponse,
    )

    assert len(result.items) == 1

    assert result.items[0].empl_id == "EMP-1001"

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    # IMPORTANT
    assert call_kwargs["empl_id"] == "EMP-1001"


def test_get_employee_profile_complete_details_missing_empl_id():
    result = get_employee_profile_complete_details(
        empl_id="",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_not_found(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    result = get_employee_profile_complete_details(
        empl_id="EMP-NOT-FOUND",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-NOT-FOUND"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_dict_filters(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    filters = {
        "org_id": FilterOps(
            eq="ORG1"
        )
    }

    result = get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=filters,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
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
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_none_filters(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    result = get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


# =====================================================================
# RECURSIVE FILTER TEST
# =====================================================================


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_by_id_recursive_filter_branch(
    mock_repo,
):
    """
    Correct recursive filter construction.

    Do NOT use:

        FiltersEnvelope(
            filters=[existing_rule]
        )

    FiltersEnvelope requires FilterGroup for recursive rule lists.
    """

    mock_repo.return_value = _repo_response(
        [_sample_employee()]
    )

    existing_rule = FilterRule(
        field="org_id",
        ops=FilterOps(
            eq="ORG1"
        ),
    )

    existing_group = FilterGroup(
        filters=[
            existing_rule
        ]
    )

    filters = FiltersEnvelope(
        filters=existing_group
    )

    result = get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=filters,
        limit=10,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    assert len(result.items) == 1
    assert result.items[0].empl_id == "EMP-1001"

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    passed_filters = call_kwargs["filters"]

    assert isinstance(
        passed_filters,
        FiltersEnvelope,
    )

    assert isinstance(
        passed_filters.filters,
        FilterGroup,
    )


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_custom_limit(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=None,
        limit=25,
        cursor=None,
        columns=None,
        sort=SortModel(),
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["empl_id"] == "EMP-1001"

    assert call_kwargs["page"].limit == 25


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_cursor(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=None,
        limit=10,
        cursor="TEST-CURSOR",
        columns=None,
        sort=SortModel(),
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["page"].cursor == "TEST-CURSOR"


@patch(
    "domain.services.employee_profile_complete_service."
    "employee_profile_complete_repo."
    "get_employee_profile_complete_by_id"
)
def test_get_employee_profile_complete_details_columns(
    mock_repo,
):
    mock_repo.return_value = _repo_response([])

    columns = [
        "empl_id",
        "first_name",
        "last_name",
    ]

    get_employee_profile_complete_details(
        empl_id="EMP-1001",
        filters=None,
        limit=10,
        cursor=None,
        columns=columns,
        sort=SortModel(),
    )

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["columns"] == columns
