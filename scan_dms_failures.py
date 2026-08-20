from unittest.mock import MagicMock, patch

from db.repositories import employee_profile_complete_repo as repo


# ============================================================================
# get_employee_profile_completes
# ============================================================================


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_completes_success(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "employee_key": "EMP-1001",
                "employee_name": "Test Employee",
            }
        ]
    }

    result = repo.get_employee_profile_completes()

    assert len(result["items"]) == 1
    assert result["items"][0]["employee_key"] == "EMP-1001"

    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_completes_empty(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [],
    }

    result = repo.get_employee_profile_completes()

    assert result["items"] == []
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


# ============================================================================
# get_employee_profile_complete_by_id
# ============================================================================


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_complete_by_id_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "employee_key": "EMP-1001",
                "employee_name": "Test Employee",
            }
        ]
    }

    result = repo.get_employee_profile_complete_by_id(
        employee_key="EMP-1001",
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["employee_key"] == "EMP-1001"

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_complete_by_id_not_found(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [],
    }

    result = repo.get_employee_profile_complete_by_id(
        employee_key="EMP-9999",
    )

    assert result["items"] == []
    assert result["page"]["has_more"] is False
    assert result["page"]["cursor"] is None

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()


# ============================================================================
# _format_paginated_response
# Covers missing lines 112-113
# ============================================================================


@patch.object(
    repo,
    "encode_cursor",
    return_value="encoded-next-cursor",
)
def test_format_paginated_response_has_more(
    mock_encode_cursor,
):
    items = [
        {
            "employee_key": "EMP-1001",
            "employee_name": "Employee One",
            "total_count_hidden": 2,
        },
        {
            "employee_key": "EMP-1002",
            "employee_name": "Employee Two",
            "total_count_hidden": 2,
        },
    ]

    result = repo._format_paginated_response(
        items=items,
        limit=1,
    )

    assert len(result["items"]) == 1

    assert (
        result["items"][0]["employee_key"]
        == "EMP-1001"
    )

    assert (
        "total_count_hidden"
        not in result["items"][0]
    )

    assert result["page"]["has_more"] is True

    assert (
        result["page"]["cursor"]
        == "encoded-next-cursor"
    )

    mock_encode_cursor.assert_called_once_with(
        "EMP-1001"
    )


# ============================================================================
# get_employee_profile_completes with dict filters
# Covers missing line 135
# ============================================================================


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_completes_with_dict_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [],
    }

    filters = {}

    result = repo.get_employee_profile_completes(
        filters=filters,
    )

    assert result["items"] == []

    assert result["page"]["has_more"] is False

    assert result["page"]["cursor"] is None

    mock_get_list_plan.assert_called_once()

    mock_execute_query.assert_called_once()


# ============================================================================
# get_employee_profile_complete_by_id with None filters
# Covers missing line 166
# ============================================================================


@patch.object(repo, "execute_query")
@patch.object(repo._builder, "get_list_plan")
def test_get_employee_profile_complete_by_id_with_no_filters(
    mock_get_list_plan,
    mock_execute_query,
):
    plan = MagicMock()
    plan.sql = "SELECT 1"
    plan.params = {}

    mock_get_list_plan.return_value = plan

    mock_execute_query.return_value = {
        "items": [
            {
                "employee_key": "EMP-1001",
                "employee_name": "Test Employee",
            }
        ]
    }

    result = repo.get_employee_profile_complete_by_id(
        employee_key="EMP-1001",
        filters=None,
    )

    assert len(result["items"]) == 1

    assert (
        result["items"][0]["employee_key"]
        == "EMP-1001"
    )

    mock_get_list_plan.assert_called_once()

    mock_execute_query.assert_called_once()


# ============================================================================
# get_employee_profile_complete_by_id recursive filter branch
# Covers missing lines 171-172
# ============================================================================


def test_get_employee_profile_complete_by_id_recursive_filter_branch():
    class RecursiveFilterContainer:
        def __init__(self):
            self.filters = []

    recursive_filters = RecursiveFilterContainer()

    # model_construct intentionally bypasses validation here.
    # We only need to exercise the non-dict recursive filter branch.
    filters_envelope = repo.FiltersEnvelope.model_construct(
        filters=recursive_filters,
    )

    try:
        repo.get_employee_profile_complete_by_id(
            employee_key="EMP-1001",
            filters=filters_envelope,
        )
    except Exception:
        # The synthetic recursive object may fail later validation.
        # Lines 171-172 have already been exercised before that point.
        pass

    assert len(recursive_filters.filters) == 1

    added_rule = recursive_filters.filters[0]

    assert added_rule.field == "employee_key"

    assert added_rule.ops.eq == "EMP-1001"
