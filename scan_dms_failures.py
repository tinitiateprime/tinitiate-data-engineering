"""
Unit tests for db.repositories.employee_profile_complete_repo.

Important:
- Employee detail lookup uses empl_id.
- employee_key is NOT used as the lookup argument.
- FiltersEnvelope recursive filters must use FilterGroup.
"""

from unittest.mock import MagicMock, patch

import pytest

from db.repositories import employee_profile_complete_repo

from v1.schemas import (
    FilterGroup,
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# =====================================================================
# TEST DATA
# =====================================================================

EMPLOYEE_DATA = {
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


# =====================================================================
# HELPERS
# =====================================================================


def _make_query_result(items=None):
    """
    Return the same general structure expected from execute_query().
    """
    return {
        "items": items if items is not None else [],
    }


def _make_plan():
    """
    Create a fake builder plan.
    """
    plan = MagicMock()
    plan.sql = "SELECT * FROM gold.employee_profile_complete_vw"
    plan.params = []
    return plan


# =====================================================================
# VIEW SPEC TESTS
# =====================================================================


def test_employee_profile_complete_view_spec_exists():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert spec is not None
    assert spec.table == "gold.employee_profile_complete_vw"


def test_employee_profile_complete_logical_id():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert spec.logical_id_field == "employee_key"


def test_employee_profile_complete_empl_id_exists():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert "empl_id" in spec.column_map


def test_employee_profile_complete_default_select_contains_empl_id():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert "empl_id" in spec.default_select


def test_employee_profile_complete_allowed_sort_fields():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert "empl_id" in spec.allowed_sort_fields
    assert "employee_key" in spec.allowed_sort_fields


# =====================================================================
# FORMAT PAGINATED RESPONSE
# =====================================================================


def test_format_paginated_response_empty():
    result = employee_profile_complete_repo._format_paginated_response(
        items=[],
        limit=10,
    )

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_format_paginated_response_no_more():
    items = [
        {
            "employee_key": "EMPLOYEE-KEY-001",
            "empl_id": "EMP-1001",
        }
    ]

    result = employee_profile_complete_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch(
    "db.repositories.employee_profile_complete_repo.encode_cursor",
    return_value="NEXT-CURSOR",
)
def test_format_paginated_response_has_more(mock_encode_cursor):
    items = []

    for i in range(11):
        items.append(
            {
                "employee_key": f"KEY-{i}",
                "empl_id": f"EMP-{i}",
            }
        )

    result = employee_profile_complete_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 10
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "NEXT-CURSOR"

    mock_encode_cursor.assert_called_once()


def test_format_paginated_response_removes_hidden_count():
    items = [
        {
            "employee_key": "EMPLOYEE-KEY-001",
            "empl_id": "EMP-1001",
            "total_count_hidden": 100,
        }
    ]

    result = employee_profile_complete_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert "total_count_hidden" not in result["items"][0]


# =====================================================================
# GET EMPLOYEE PROFILE COMPLETES
# =====================================================================


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_completes_success(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result(
        [EMPLOYEE_DATA.copy()]
    )

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=None,
        sort=None,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["empl_id"] == "EMP-1001"

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_completes_empty(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=None,
        sort=None,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_completes_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    filters = {
        "org_id": FilterOps(eq="ORG1"),
    }

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result["items"] == []

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_completes_filters_envelope(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    filters = FiltersEnvelope(
        filters={
            "org_id": FilterOps(eq="ORG1"),
        }
    )

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result["items"] == []

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert call_kwargs["filters"] is filters


# =====================================================================
# GET EMPLOYEE PROFILE COMPLETE BY EMPL_ID
# =====================================================================


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_success(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result(
        [EMPLOYEE_DATA.copy()]
    )

    result = (
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id(
            empl_id="EMP-1001",
            filters=None,
            page=PaginationModel(limit=10),
            columns=None,
            sort=SortModel(),
        )
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["empl_id"] == "EMP-1001"

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_not_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    result = (
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id(
            empl_id="EMP-NOT-FOUND",
            filters=None,
            page=PaginationModel(limit=10),
            columns=None,
            sort=SortModel(),
        )
    )

    assert result["items"] == []


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_none_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    result = (
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id(
            empl_id="EMP-1001",
            filters=None,
            page=PaginationModel(limit=10),
            columns=None,
            sort=SortModel(),
        )
    )

    assert result["items"] == []

    call_kwargs = mock_get_list_plan.call_args.kwargs

    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    filters = {
        "org_id": FilterOps(eq="ORG1"),
    }

    result = (
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id(
            empl_id="EMP-1001",
            filters=filters,
            page=PaginationModel(limit=10),
            columns=None,
            sort=SortModel(),
        )
    )

    assert result["items"] == []

    call_kwargs = mock_get_list_plan.call_args.kwargs

    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    assert "empl_id" in validated_filters.filters

    assert (
        validated_filters.filters["empl_id"].eq
        == "EMP-1001"
    )


# =====================================================================
# IMPORTANT FIX:
# RECURSIVE FILTER BRANCH
# =====================================================================


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_recursive_filter_branch(
    mock_get_list_plan,
    mock_execute_query,
):
    """
    Exercise the branch where filters.filters is a FilterGroup.

    WRONG:
        FiltersEnvelope(filters=[FilterRule(...)])
    because FiltersEnvelope does not accept list[FilterRule].

    CORRECT:
        FiltersEnvelope(
            filters=FilterGroup(
                filters=[FilterRule(...)]
            )
        )
    """

    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    existing_rule = FilterRule(
        field="org_id",
        ops=FilterOps(eq="ORG1"),
    )

    existing_group = FilterGroup(
        filters=[existing_rule]
    )

    filters = FiltersEnvelope(
        filters=existing_group
    )

    result = (
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id(
            empl_id="EMP-1001",
            filters=filters,
            page=PaginationModel(limit=10),
            columns=None,
            sort=SortModel(),
        )
    )

    assert result["items"] == []

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()

    call_kwargs = mock_get_list_plan.call_args.kwargs

    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    assert isinstance(
        validated_filters.filters,
        FilterGroup,
    )

    rules = validated_filters.filters.filters

    # Existing filter must remain.
    assert any(
        rule.field == "org_id"
        for rule in rules
    )

    # empl_id must be injected.
    assert any(
        rule.field == "empl_id"
        for rule in rules
    )

    empl_rule = next(
        rule
        for rule in rules
        if rule.field == "empl_id"
    )

    assert empl_rule.ops.eq == "EMP-1001"


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_columns(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    columns = [
        "empl_id",
        "first_name",
        "last_name",
    ]

    employee_profile_complete_repo.get_employee_profile_complete_by_id(
        empl_id="EMP-1001",
        filters=None,
        page=PaginationModel(limit=10),
        columns=columns,
        sort=SortModel(),
    )

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert call_kwargs["columns"] == columns


@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_pagination(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = _make_plan()

    mock_get_list_plan.return_value = plan
    mock_execute_query.return_value = _make_query_result([])

    page = PaginationModel(
        limit=25,
    )

    employee_profile_complete_repo.get_employee_profile_complete_by_id(
        empl_id="EMP-1001",
        filters=None,
        page=page,
        columns=None,
        sort=SortModel(),
    )

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert call_kwargs["page"].limit == 25
