"""
Unit tests for db.repositories.employee_profile_repo

Covers:
- generic employee profile search
- dict filters
- explicit sort/page/columns
- pagination / cursor generation
- employee lookup by ID
- manager lookup
- organization lookup
- clearance lookup
- personnel roster
- invalid/blank identifier branches
- empty DB results

Target coverage: 90%+
"""

from unittest.mock import MagicMock, patch

import pytest

from db.repositories import employee_profile_repo
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


# ============================================================================
# Helpers
# ============================================================================


@pytest.fixture
def mock_plan():
    plan = MagicMock()
    plan.sql = "SELECT * FROM gold.employee_profile_vw"
    plan.params = {}
    return plan


def _employee(
    employee_id="E-1001",
    first_name="John",
    last_name="Doe",
):
    return {
        "EMPL_ID": employee_id,
        "FIRST_NAME": first_name,
        "LAST_NAME": last_name,
        "LAST_FIRST_NAME": f"{last_name}, {first_name}",
        "TITLE_DESC": "Engineer",
        "JOB_CODE": "ENG1",
        "S_EMPL_TYPE_CD": "EMP",
        "ORG_ID": "ORG-001",
        "DEPT_NAME": "Engineering",
        "LOC_NAME": "Dallas",
        "LOC_CITY": "Dallas",
        "MGR_NAME": "Manager One",
        "MGR_EMPL_ID": "M-100",
        "HIRE_DATE": "2020-01-01",
        "clearance_status": "Active",
        "clearance_status_date": "2025-01-01",
        "clearance_eligibility": "Eligible",
    }


# ============================================================================
# _format_paginated_response
# ============================================================================


def test_format_paginated_response_no_more():
    items = [
        {
            "EMPL_ID": "E-1001",
            "FIRST_NAME": "John",
            "total_count_hidden": 1,
        }
    ]

    result = employee_profile_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None

    # helper removes hidden count
    assert "total_count_hidden" not in result["items"][0]


@patch("db.repositories.employee_profile_repo.encode_cursor")
def test_format_paginated_response_has_more(mock_encode_cursor):
    mock_encode_cursor.return_value = "encoded-next-cursor"

    items = [
        {"EMPL_ID": f"E-{i}", "total_count_hidden": 11}
        for i in range(11)
    ]

    result = employee_profile_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 10
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "encoded-next-cursor"

    mock_encode_cursor.assert_called_once_with("E-9")

    for item in result["items"]:
        assert "total_count_hidden" not in item


def test_format_paginated_response_empty():
    result = employee_profile_repo._format_paginated_response(
        items=[],
        limit=10,
    )

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# ============================================================================
# get_employee_profiles
# ============================================================================


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_basic(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    result = employee_profile_repo.get_employee_profiles()

    assert len(result["items"]) == 1
    assert result["items"][0]["EMPL_ID"] == "E-1001"
    assert result["page"]["has_more"] is False

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_with_dict_filter(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    result = employee_profile_repo.get_employee_profiles(
        filters={
            "organizationId": {
                "eq": "ORG-001"
            }
        }
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["ORG_ID"] == "ORG-001"

    args = mock_get_list_plan.call_args.kwargs
    assert isinstance(args["filters"], FiltersEnvelope)


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_with_filter_envelope(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    filters = FiltersEnvelope(filters={})

    result = employee_profile_repo.get_employee_profiles(
        filters=filters
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs
    assert args["filters"] is filters


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_with_sort_page_columns(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    sort = SortModel(
        field="firstName",
        order="desc",
    )

    page = PaginationModel(
        limit=5,
    )

    columns = [
        "employeeId",
        "firstName",
        "lastName",
    ]

    result = employee_profile_repo.get_employee_profiles(
        filters=None,
        sort=sort,
        page=page,
        columns=columns,
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs

    assert args["sort"] is sort
    assert args["page"] is page
    assert args["columns"] == columns

    mock_execute_query.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=5,
    )


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_empty_result(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": []
    }

    result = employee_profile_repo.get_employee_profiles()

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.encode_cursor")
@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profiles_has_more(
    mock_get_list_plan,
    mock_execute_query,
    mock_encode_cursor,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_encode_cursor.return_value = "NEXT"

    # Request limit 2 but DB returns 3.
    page = PaginationModel(limit=2)

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1"),
            _employee("E-2"),
            _employee("E-3"),
        ]
    }

    result = employee_profile_repo.get_employee_profiles(
        page=page
    )

    assert len(result["items"]) == 2
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "NEXT"


# ============================================================================
# get_employee_profile_by_id
# ============================================================================


def test_get_employee_profile_by_id_empty_string():
    result = employee_profile_repo.get_employee_profile_by_id("")

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


def test_get_employee_profile_by_id_whitespace():
    result = employee_profile_repo.get_employee_profile_by_id("   ")

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profile_by_id_found(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee("E-2001")]
    }

    result = employee_profile_repo.get_employee_profile_by_id(
        " E-2001 "
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["EMPL_ID"] == "E-2001"

    args = mock_get_list_plan.call_args.kwargs

    assert isinstance(args["filters"], FiltersEnvelope)
    assert args["page"].limit == 1


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profile_by_id_not_found(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": []
    }

    result = employee_profile_repo.get_employee_profile_by_id(
        "DOES-NOT-EXIST"
    )

    assert result["items"] == []
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employee_profile_by_id_columns(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    columns = ["employeeId", "firstName"]

    employee_profile_repo.get_employee_profile_by_id(
        "E-1001",
        columns=columns,
    )

    args = mock_get_list_plan.call_args.kwargs
    assert args["columns"] == columns


# ============================================================================
# get_employees_by_manager
# ============================================================================


def test_get_employees_by_manager_empty_manager():
    result = employee_profile_repo.get_employees_by_manager("")

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_get_employees_by_manager_whitespace_manager():
    result = employee_profile_repo.get_employees_by_manager("   ")

    assert result["items"] == []
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_manager_success(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    }

    result = employee_profile_repo.get_employees_by_manager(
        "M-100"
    )

    assert len(result["items"]) == 2

    args = mock_get_list_plan.call_args.kwargs
    assert isinstance(args["filters"], FiltersEnvelope)


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_manager_custom_page_sort_columns(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    page = PaginationModel(limit=7)

    sort = SortModel(
        field="firstName",
        order="desc",
    )

    columns = ["employeeId", "firstName"]

    employee_profile_repo.get_employees_by_manager(
        mgr_empl_id="M-100",
        page=page,
        sort=sort,
        columns=columns,
    )

    args = mock_get_list_plan.call_args.kwargs

    assert args["page"] is page
    assert args["sort"] is sort
    assert args["columns"] == columns

    mock_execute_query.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=7,
    )


# ============================================================================
# get_employees_by_org
# ============================================================================


def test_get_employees_by_org_empty_org():
    result = employee_profile_repo.get_employees_by_org("")

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_get_employees_by_org_whitespace_org():
    result = employee_profile_repo.get_employees_by_org(" ")

    assert result["items"] == []
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_org_success(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    }

    result = employee_profile_repo.get_employees_by_org(
        "ORG-001"
    )

    assert len(result["items"]) == 2

    args = mock_get_list_plan.call_args.kwargs
    assert isinstance(args["filters"], FiltersEnvelope)


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_org_custom_arguments(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    page = PaginationModel(limit=3)

    sort = SortModel(
        field="employeeId",
        order="asc",
    )

    columns = [
        "employeeId",
        "organizationId",
    ]

    result = employee_profile_repo.get_employees_by_org(
        org_id="ORG-001",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs

    assert args["page"] is page
    assert args["sort"] is sort
    assert args["columns"] == columns


# ============================================================================
# get_employees_by_clearance
# ============================================================================


def test_get_employees_by_clearance_empty_status():
    result = employee_profile_repo.get_employees_by_clearance("")

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_get_employees_by_clearance_whitespace_status():
    result = employee_profile_repo.get_employees_by_clearance("   ")

    assert result["items"] == []
    assert result["page"]["has_more"] is False


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_clearance_success(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    }

    result = employee_profile_repo.get_employees_by_clearance(
        "Active"
    )

    assert len(result["items"]) == 2

    args = mock_get_list_plan.call_args.kwargs
    assert isinstance(args["filters"], FiltersEnvelope)


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_employees_by_clearance_custom_arguments(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    page = PaginationModel(limit=4)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    columns = [
        "employeeId",
        "clearanceStatus",
    ]

    result = employee_profile_repo.get_employees_by_clearance(
        clearance_status="Active",
        page=page,
        sort=sort,
        columns=columns,
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs

    assert args["page"] is page
    assert args["sort"] is sort
    assert args["columns"] == columns


# ============================================================================
# get_personnel_roster
# ============================================================================


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_defaults(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1001"),
            _employee("E-1002"),
        ]
    }

    result = employee_profile_repo.get_personnel_roster()

    assert len(result["items"]) == 2
    assert result["page"]["has_more"] is False

    args = mock_get_list_plan.call_args.kwargs

    assert isinstance(args["filters"], FiltersEnvelope)

    # get_personnel_roster uses default personnel roster selection.
    assert (
        args["columns"]
        == employee_profile_repo.PERSONNEL_ROSTER_SELECT
    )


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    result = employee_profile_repo.get_personnel_roster(
        filters={
            "employeeId": {
                "eq": "E-1001"
            }
        }
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs
    assert isinstance(args["filters"], FiltersEnvelope)


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_filter_envelope(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    filters = FiltersEnvelope(filters={})

    result = employee_profile_repo.get_personnel_roster(
        filters=filters
    )

    assert len(result["items"]) == 1

    args = mock_get_list_plan.call_args.kwargs
    assert args["filters"] is filters


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_custom_columns(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    columns = [
        "employeeId",
        "firstName",
    ]

    employee_profile_repo.get_personnel_roster(
        columns=columns
    )

    args = mock_get_list_plan.call_args.kwargs
    assert args["columns"] == columns


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_custom_page_and_sort(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = {
        "items": [_employee()]
    }

    page = PaginationModel(limit=25)

    sort = SortModel(
        field="employeeId",
        order="desc",
    )

    employee_profile_repo.get_personnel_roster(
        page=page,
        sort=sort,
    )

    args = mock_get_list_plan.call_args.kwargs

    assert args["page"] is page
    assert args["sort"] is sort

    mock_execute_query.assert_called_once_with(
        mock_plan.sql,
        mock_plan.params,
        limit=25,
    )


@patch("db.repositories.employee_profile_repo.encode_cursor")
@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_pagination_has_more(
    mock_get_list_plan,
    mock_execute_query,
    mock_encode_cursor,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_encode_cursor.return_value = "ROSTER-NEXT"

    page = PaginationModel(limit=2)

    mock_execute_query.return_value = {
        "items": [
            _employee("E-1"),
            _employee("E-2"),
            _employee("E-3"),
        ]
    }

    result = employee_profile_repo.get_personnel_roster(
        page=page
    )

    assert len(result["items"]) == 2
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "ROSTER-NEXT"


@patch("db.repositories.employee_profile_repo.execute_query")
@patch("db.repositories.employee_profile_repo._builder.get_list_plan")
def test_get_personnel_roster_empty(
    mock_get_list_plan,
    mock_execute_query,
    mock_plan,
):
    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = {
        "items": []
    }

    result = employee_profile_repo.get_personnel_roster()

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False
