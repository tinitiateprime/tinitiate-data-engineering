"""
Unit tests for domain.services.employee_profile_service.

Covers:
- _empty_response
- get_all_employees
- get_employee_by_id
- get_direct_reports
- get_employees_in_org
- get_employees_by_clearance
- get_personnel_roster
- default pagination/sorting
- explicit pagination/sorting
- dictionary filter conversion
- FiltersEnvelope passthrough
- empty parameter branches
- empty repository results
- metadata propagation
"""

from unittest.mock import patch

import pytest

from core.filters import FiltersEnvelope, SortModel
from core.pagination import PaginationModel
from domain.services import employee_profile_service


# ============================================================================
# Sample data
# ============================================================================


def _employee(
    employee_id="E-1001",
    first_name="John",
    last_name="Doe",
):
    """
    Valid EmployeeProfileResponse payload.

    Aliases are used because EmployeeProfileResponse is configured with
    populate_by_name=True.
    """
    return {
        "employeeId": employee_id,
        "firstName": first_name,
        "lastName": last_name,
        "lastFirstName": f"{last_name}, {first_name}",
        "titleDescription": "Software Engineer",
        "jobCode": "ENG-01",
        "employmentType": "EMP",
        "organizationId": "ORG-001",
        "departmentName": "Engineering",
        "locationName": "Dallas",
        "locationCity": "Dallas",
        "managerName": "Jane Manager",
        "managerEmployeeId": "M-100",
        "hireDate": "2020-01-01",
        "clearanceStatus": "Active",
        "clearanceStatusDate": "2025-01-01",
        "clearanceEligibility": "Eligible",
    }


def _repo_result(
    items=None,
    cursor=None,
    has_more=False,
):
    return {
        "items": items if items is not None else [],
        "page": {
            "cursor": cursor,
            "has_more": has_more,
        },
    }


# ============================================================================
# _empty_response
# ============================================================================


def test_empty_response():
    result = employee_profile_service._empty_response()

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None


# ============================================================================
# get_all_employees
# ============================================================================


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    result = employee_profile_service.get_all_employees()

    assert len(result.items) == 1
    assert result.items[0].empl_id == "E-1001"

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_empty(mock_repo):
    mock_repo.return_value = _repo_result(items=[])

    result = employee_profile_service.get_all_employees()

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_with_dict_filters(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    result = employee_profile_service.get_all_employees(
        filters={}
    )

    assert len(result.items) == 1

    kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_with_filters_envelope(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    filters = FiltersEnvelope(filters={})

    result = employee_profile_service.get_all_employees(
        filters=filters
    )

    assert len(result.items) == 1

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["filters"] is filters


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_custom_page_sort_columns(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor="NEXT-CURSOR",
        has_more=True,
    )

    page = PaginationModel(limit=5)

    sort = SortModel(
        field="firstName",
        order="desc",
    )

    columns = [
        "employeeId",
        "firstName",
        "lastName",
    ]

    result = employee_profile_service.get_all_employees(
        filters=None,
        sort=sort,
        page=page,
        columns=columns,
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "NEXT-CURSOR"
    assert result.metadata.has_more is True

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["sort"] is sort
    assert kwargs["page"] is page
    assert kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_default_page_and_sort(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    employee_profile_service.get_all_employees()

    kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    assert kwargs["sort"].field == "lastName"
    assert kwargs["sort"].order == "asc"


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profiles"
)
def test_get_all_employees_multiple_items(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[
            _employee("E-1001", "John", "Doe"),
            _employee("E-1002", "Jane", "Smith"),
        ]
    )

    result = employee_profile_service.get_all_employees()

    assert len(result.items) == 2

    assert result.items[0].empl_id == "E-1001"
    assert result.items[1].empl_id == "E-1002"


# ============================================================================
# get_employee_by_id
# ============================================================================


def test_get_employee_by_id_empty_id():
    result = employee_profile_service.get_employee_by_id("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_get_employee_by_id_none_id():
    result = employee_profile_service.get_employee_by_id(None)

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profile_by_id"
)
def test_get_employee_by_id_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee("E-2001")]
    )

    result = employee_profile_service.get_employee_by_id(
        "E-2001"
    )

    assert len(result.items) == 1
    assert result.items[0].empl_id == "E-2001"

    mock_repo.assert_called_once_with(
        empl_id="E-2001",
        columns=None,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profile_by_id"
)
def test_get_employee_by_id_with_columns(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    columns = [
        "employeeId",
        "firstName",
    ]

    result = employee_profile_service.get_employee_by_id(
        "E-1001",
        columns=columns,
    )

    assert len(result.items) == 1

    mock_repo.assert_called_once_with(
        empl_id="E-1001",
        columns=columns,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profile_by_id"
)
def test_get_employee_by_id_not_found(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[]
    )

    result = employee_profile_service.get_employee_by_id(
        "NOT-FOUND"
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employee_profile_by_id"
)
def test_get_employee_by_id_metadata(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor=None,
        has_more=False,
    )

    result = employee_profile_service.get_employee_by_id(
        "E-1001"
    )

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    assert result.metadata.applied_filters is not None


# ============================================================================
# get_direct_reports
# ============================================================================


def test_get_direct_reports_empty_manager_id():
    result = employee_profile_service.get_direct_reports("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_get_direct_reports_none_manager_id():
    result = employee_profile_service.get_direct_reports(None)

    assert result.items == []
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_manager"
)
def test_get_direct_reports_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    )

    result = employee_profile_service.get_direct_reports(
        "M-100"
    )

    assert len(result.items) == 2

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["mgr_empl_id"] == "M-100"

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_manager"
)
def test_get_direct_reports_custom_page_sort_columns(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor="NEXT",
        has_more=True,
    )

    page = PaginationModel(limit=5)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    columns = [
        "employeeId",
        "firstName",
    ]

    result = employee_profile_service.get_direct_reports(
        mgr_empl_id="M-100",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert len(result.items) == 1
    assert result.metadata.cursor == "NEXT"
    assert result.metadata.has_more is True

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["mgr_empl_id"] == "M-100"
    assert kwargs["page"] is page
    assert kwargs["sort"] is sort
    assert kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_manager"
)
def test_get_direct_reports_empty_result(mock_repo):
    mock_repo.return_value = _repo_result(items=[])

    result = employee_profile_service.get_direct_reports(
        "M-100"
    )

    assert result.items == []
    assert result.metadata.has_more is False


# ============================================================================
# get_employees_in_org
# ============================================================================


def test_get_employees_in_org_empty_org():
    result = employee_profile_service.get_employees_in_org("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_get_employees_in_org_none_org():
    result = employee_profile_service.get_employees_in_org(None)

    assert result.items == []
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_org"
)
def test_get_employees_in_org_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    )

    result = employee_profile_service.get_employees_in_org(
        "ORG-001"
    )

    assert len(result.items) == 2

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["org_id"] == "ORG-001"

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_org"
)
def test_get_employees_in_org_custom_arguments(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor="ORG-NEXT",
        has_more=True,
    )

    page = PaginationModel(limit=7)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    columns = [
        "employeeId",
        "organizationId",
    ]

    result = employee_profile_service.get_employees_in_org(
        org_id="ORG-001",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "ORG-NEXT"
    assert result.metadata.has_more is True

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["org_id"] == "ORG-001"
    assert kwargs["page"] is page
    assert kwargs["sort"] is sort
    assert kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_org"
)
def test_get_employees_in_org_empty_result(mock_repo):
    mock_repo.return_value = _repo_result(items=[])

    result = employee_profile_service.get_employees_in_org(
        "ORG-001"
    )

    assert result.items == []


# ============================================================================
# get_employees_by_clearance
# ============================================================================


def test_get_employees_by_clearance_empty_status():
    result = (
        employee_profile_service
        .get_employees_by_clearance("")
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_get_employees_by_clearance_none_status():
    result = (
        employee_profile_service
        .get_employees_by_clearance(None)
    )

    assert result.items == []
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_clearance"
)
def test_get_employees_by_clearance_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    )

    result = (
        employee_profile_service
        .get_employees_by_clearance("Active")
    )

    assert len(result.items) == 2

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["clearance_status"] == "Active"

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_clearance"
)
def test_get_employees_by_clearance_custom_arguments(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor="CLEARANCE-NEXT",
        has_more=True,
    )

    page = PaginationModel(limit=3)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    columns = [
        "employeeId",
        "clearanceStatus",
    ]

    result = (
        employee_profile_service
        .get_employees_by_clearance(
            clearance_status="Active",
            page=page,
            sort=sort,
            columns=columns,
        )
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "CLEARANCE-NEXT"
    assert result.metadata.has_more is True

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["clearance_status"] == "Active"
    assert kwargs["page"] is page
    assert kwargs["sort"] is sort
    assert kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_employees_by_clearance"
)
def test_get_employees_by_clearance_empty_result(
    mock_repo,
):
    mock_repo.return_value = _repo_result(items=[])

    result = (
        employee_profile_service
        .get_employees_by_clearance("Active")
    )

    assert result.items == []


# ============================================================================
# get_personnel_roster
# ============================================================================


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_success(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    )

    result = employee_profile_service.get_personnel_roster()

    assert len(result.items) == 2

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_empty(mock_repo):
    mock_repo.return_value = _repo_result(items=[])

    result = employee_profile_service.get_personnel_roster()

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_dict_filters(mock_repo):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    result = employee_profile_service.get_personnel_roster(
        filters={}
    )

    assert len(result.items) == 1

    kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_filters_envelope(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    filters = FiltersEnvelope(filters={})

    result = employee_profile_service.get_personnel_roster(
        filters=filters
    )

    assert len(result.items) == 1

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["filters"] is filters


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_custom_page_sort_columns(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()],
        cursor="ROSTER-NEXT",
        has_more=True,
    )

    page = PaginationModel(limit=10)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    columns = [
        "employeeId",
        "firstName",
        "lastName",
    ]

    result = employee_profile_service.get_personnel_roster(
        filters=None,
        sort=sort,
        page=page,
        columns=columns,
    )

    assert len(result.items) == 1

    assert result.metadata.cursor == "ROSTER-NEXT"
    assert result.metadata.has_more is True

    kwargs = mock_repo.call_args.kwargs

    assert kwargs["sort"] is sort
    assert kwargs["page"] is page
    assert kwargs["columns"] == columns


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_default_sort_page(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    employee_profile_service.get_personnel_roster()

    kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    assert kwargs["sort"].field == "lastName"
    assert kwargs["sort"].order == "asc"


@patch(
    "domain.services.employee_profile_service."
    "employee_profile_repo.get_personnel_roster"
)
def test_get_personnel_roster_metadata_filters(
    mock_repo,
):
    mock_repo.return_value = _repo_result(
        items=[_employee()]
    )

    filters = FiltersEnvelope(filters={})

    result = employee_profile_service.get_personnel_roster(
        filters=filters
    )

    assert result.metadata is not None
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
