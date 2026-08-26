"""
Unit tests for db.repositories.employee_profile_complete_repo.

IMPORTANT:
The employee lookup key for get_employee_profile_complete_by_id()
is empl_id, NOT employee_key.
"""

from unittest.mock import MagicMock, patch

import pytest

from db.repositories import employee_profile_complete_repo
from v1.schemas import (
    FilterOps,
    FilterRule,
    FiltersEnvelope,
    PaginationModel,
    SortModel,
)


# ============================================================
# Helpers
# ============================================================

def _make_query_result(items=None):
    return {
        "items": items or []
    }


def _sample_employee():
    return {
        "employee_key": "EMPLOYEE-KEY-001",
        "email_key": "test_email_key",
        "empl_id": "EMP-1001",
        "my_id": "test_my_id",
        "sotv_employee_id": "test_sotv_employee_id",
        "first_name": "John",
        "last_name": "Doe",
        "mid_name": "A",
        "employee_name": "Doe, John",
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


# ============================================================
# QuerySpec tests
# ============================================================

def test_employee_profile_complete_view_spec():
    spec = employee_profile_complete_repo.EMPLOYEEPROFILECOMPLETE_VIEW_SPEC

    assert spec.table == "gold.employee_profile_complete_vw"

    # Pagination can continue to use employee_key.
    # This is separate from the employee lookup parameter.
    assert spec.logical_id_field == "employee_key"

    # But empl_id must exist as a real queryable column.
    assert "empl_id" in spec.column_map
    assert spec.column_map["empl_id"]["col"] == "empl_id"

    assert "empl_id" in spec.allowed_sort_fields
    assert "empl_id" in spec.default_select


# ============================================================
# _format_paginated_response
# ============================================================

def test_format_paginated_response_empty():
    result = employee_profile_complete_repo._format_paginated_response(
        items=[],
        limit=10,
    )

    assert result["items"] == []
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


def test_format_paginated_response_under_limit():
    items = [_sample_employee()]

    result = employee_profile_complete_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 1
    assert result["page"]["cursor"] is None
    assert result["page"]["has_more"] is False


@patch(
    "db.repositories.employee_profile_complete_repo.encode_cursor"
)
def test_format_paginated_response_has_more(mock_encode_cursor):
    mock_encode_cursor.return_value = "NEXT-CURSOR"

    items = []

    for i in range(11):
        item = _sample_employee()
        item["employee_key"] = f"KEY-{i}"
        item["empl_id"] = f"EMP-{i}"
        items.append(item)

    result = employee_profile_complete_repo._format_paginated_response(
        items=items,
        limit=10,
    )

    assert len(result["items"]) == 10
    assert result["page"]["has_more"] is True
    assert result["page"]["cursor"] == "NEXT-CURSOR"

    # Cursor still uses employee_key because logical_id_field is
    # employee_key in the repository QuerySpec.
    mock_encode_cursor.assert_called_once_with("KEY-9")


def test_format_paginated_response_removes_hidden_count():
    item = _sample_employee()
    item["total_count_hidden"] = 99

    result = employee_profile_complete_repo._format_paginated_response(
        items=[item],
        limit=10,
    )

    assert "total_count_hidden" not in result["items"][0]


# ============================================================
# get_employee_profile_completes
# ============================================================

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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT * FROM gold.employee_profile_complete_vw"
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = _make_query_result(
        [_sample_employee()]
    )

    filters = FiltersEnvelope(filters={})
    sort = SortModel()
    page = PaginationModel(limit=10)

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=filters,
        sort=sort,
        page=page,
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
def test_get_employee_profile_completes_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = _make_query_result([])

    filters = {
        "empl_id": FilterOps(eq="EMP-1001")
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
def test_get_employee_profile_completes_none_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = _make_query_result([])

    result = employee_profile_complete_repo.get_employee_profile_completes(
        filters=None,
        sort=None,
        page=None,
        columns=None,
    )

    assert result["items"] == []

    call_kwargs = mock_get_list_plan.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )

    assert isinstance(
        call_kwargs["page"],
        PaginationModel,
    )

    assert isinstance(
        call_kwargs["sort"],
        SortModel,
    )


# ============================================================
# get_employee_profile_complete_by_id
#
# IMPORTANT:
# empl_id is the lookup argument.
# employee_key must NOT be passed as the function argument.
# ============================================================

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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan

    mock_execute_query.return_value = _make_query_result(
        [_sample_employee()]
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

    call_kwargs = mock_get_list_plan.call_args.kwargs

    filters = call_kwargs["filters"]

    assert isinstance(filters, FiltersEnvelope)


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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = _make_query_result([])

    filters = {
        "org_id": FilterOps(eq="ORG1")
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


# ============================================================
# Verify empl_id is injected into dictionary filters
# ============================================================

@patch(
    "db.repositories.employee_profile_complete_repo.execute_query"
)
@patch.object(
    employee_profile_complete_repo._builder,
    "get_list_plan",
)
def test_get_employee_profile_complete_by_id_injects_empl_id(
    mock_get_list_plan,
    mock_execute_query,
):
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = _make_query_result([])

    filters = {}

    employee_profile_complete_repo.get_employee_profile_complete_by_id(
        empl_id="EMP-1001",
        filters=filters,
        page=PaginationModel(limit=10),
        columns=None,
        sort=SortModel(),
    )

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    # This is the important test:
    # lookup filtering is based on empl_id.
    filter_data = validated_filters.filters

    assert "empl_id" in filter_data


# ============================================================
# Recursive FiltersEnvelope branch
# ============================================================

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
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT ..."
    mock_plan.params = []

    mock_get_list_plan.return_value = mock_plan
    mock_execute_query.return_value = _make_query_result([])

    existing_rule = FilterRule(
        field="org_id",
        ops=FilterOps(eq="ORG1"),
    )

    filters = FiltersEnvelope(
        filters=[existing_rule]
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

    call_kwargs = mock_get_list_plan.call_args.kwargs
    validated_filters = call_kwargs["filters"]

    assert isinstance(
        validated_filters,
        FiltersEnvelope,
    )

    # Existing filter + automatically injected empl_id filter.
    assert len(validated_filters.filters) >= 2

    empl_rules = [
        rule
        for rule in validated_filters.filters
        if getattr(rule, "field", None) == "empl_id"
    ]

    assert len(empl_rules) == 1


# ============================================================
# Explicitly protect against the old employee_key API contract
# ============================================================

def test_get_employee_profile_complete_by_id_uses_empl_id_parameter():
    """
    Regression test.

    The repository lookup API must use `empl_id`.
    `employee_key` is a returned/view field and pagination key,
    but is NOT the argument for this lookup function.
    """

    import inspect

    signature = inspect.signature(
        employee_profile_complete_repo
        .get_employee_profile_complete_by_id
    )

    assert "empl_id" in signature.parameters
    assert "employee_key" not in signature.parameters
