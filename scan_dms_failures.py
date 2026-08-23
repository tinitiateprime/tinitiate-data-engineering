"""
Unit tests for v1.handlers.employees.

Covers:
- Employee profile search
- Personnel roster
- Direct reports
- Employees by organization
- Employees by clearance
- Employee profile by ID
- Employee training search
- Training by status
- Training by organization
- Training by type
- Training by employee
- Employee certifications search
- Certifications by status
- Certifications by organization
- Certifications by employee
- Blank/missing path parameter routes
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import employees


# ============================================================
# Sample Data
# ============================================================

PROFILE_DATA = {
    "empl_id": "123456",
    "first_name": "John",
    "last_name": "Doe",
    "last_first_name": "Doe, John",
    "title_desc": "Engineer",
    "job_code": "E1",
    "s_empl_type_cd": "F",
    "org_id": "01",
    "dept_name": "Engineering",
    "loc_name": "HQ",
    "loc_city": "New York",
    "mgr_name": "Jane Boss",
    "mgr_empl_id": "54321",
    "hire_date": "2020-01-01",
    "email_addr": "john.doe@example.com",
    "clearance_status": "Active",
    "clearance_status_date": "2023-01-01",
    "clearance_eligibility": "Secret",
}


TRAINING_DATA = {
    "empl_id": "123456",
    "last_first_name": "Doe, John",
    "org_id": "01",
    "record_type": "Certification",
    "title": "AWS",
    "completed_date": "2023-01-15",
    "expiration_date": "2026-01-15",
    "status": "Active",
}


CERTIFICATION_DATA = {
    "empl_id": "123456",
    "last_first_name": "Doe, John",
    "org_id": "01",
    "record_type": "Certification",
    "title": "AWS Certified",
    "completed_date": "2023-01-15",
    "expiration_date": "2026-01-15",
    "status": "CURRENT",
}


# ============================================================
# Helpers
# ============================================================


def make_mock_result(items_data):
    """
    Helper to create a mocked service response.

    Handler code expects:

        results.items
        results.metadata.model_dump()
        item.model_dump()
    """

    result = MagicMock()

    items = []

    for item_data in items_data:
        item = MagicMock()
        item.model_dump.return_value = item_data
        items.append(item)

    result.items = items

    result.metadata = MagicMock()
    result.metadata.model_dump.return_value = {
        "cursor": None,
        "has_more": False,
        "applied_filters": None,
    }

    return result


def response_body(response):
    """
    Safely convert Lambda response body into a Python object.
    """

    body = response.get("body")

    if isinstance(body, str):
        return json.loads(body)

    return body


@pytest.fixture
def mock_context():
    """
    Mock AWS Lambda context.
    """

    ctx = MagicMock()
    ctx.aws_request_id = "test-id"
    return ctx


# ============================================================
# Search Employee Profiles
# ============================================================


@patch("v1.handlers.employees.get_all_employees")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_profiles_v1_success(
    mock_get_body,
    mock_get_all,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {
            "orgId": {
                "eq": "01",
            }
        },
        "sort": {
            "field": "lastName",
            "order": "asc",
        },
        "page": {
            "limit": 10,
        },
        "columns": [
            "employeeId",
            "firstName",
        ],
    }

    mock_get_all.return_value = make_mock_result([PROFILE_DATA])

    res = employees.search_employee_profiles_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert body is not None
    assert "data" in body
    assert len(body["data"]) == 1


@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_profiles_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "msg",
        "doc",
        0,
    )

    res = employees.search_employee_profiles_v1(
        {
            "body": "{",
        },
        mock_context,
    )

    assert res["statusCode"] == 400
    assert "Invalid JSON" in res["body"]


@patch("v1.handlers.employees.get_all_employees")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_profiles_v1_not_found(
    mock_get_body,
    mock_get_all,
    mock_context,
):
    mock_get_body.return_value = {}

    mock_get_all.return_value = make_mock_result([])

    res = employees.search_employee_profiles_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 404


@patch("v1.handlers.employees.get_all_employees")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_profiles_v1_empty_filters(
    mock_get_body,
    mock_get_all,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {},
        "sort": {},
        "page": {},
    }

    mock_get_all.return_value = make_mock_result([PROFILE_DATA])

    res = employees.search_employee_profiles_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Personnel Roster
# ============================================================


@patch("v1.handlers.employees.get_personnel_roster")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_success(
    mock_get_body,
    mock_roster,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {
            "employeeId": {
                "in": [
                    "123456",
                ]
            }
        },
        "sort": {
            "field": "lastName",
        },
        "page": {
            "limit": 10,
        },
        "columns": [
            "employeeId",
            "lastName",
        ],
    }

    mock_roster.return_value = make_mock_result([PROFILE_DATA])

    res = employees.get_personnel_roster_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert "data" in body
    assert len(body["data"]) == 1


@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "msg",
        "doc",
        0,
    )

    res = employees.get_personnel_roster_v1(
        {
            "body": "{",
        },
        mock_context,
    )

    assert res["statusCode"] == 400
    assert "Invalid JSON" in res["body"]


@patch("v1.handlers.employees.get_personnel_roster")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_empty_returns_200(
    mock_get_body,
    mock_roster,
    mock_context,
):
    """
    Personnel roster is a bulk-sync style endpoint.

    Empty result should return 200 + []
    instead of 404.
    """

    mock_get_body.return_value = {}

    mock_roster.return_value = make_mock_result([])

    res = employees.get_personnel_roster_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert body["data"] == []


@patch("v1.handlers.employees.get_personnel_roster")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_dict_filters(
    mock_get_body,
    mock_roster,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {
            "employeeId": {
                "eq": "123456",
            }
        }
    }

    mock_roster.return_value = make_mock_result([PROFILE_DATA])

    res = employees.get_personnel_roster_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_personnel_roster")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_default_sort_page(
    mock_get_body,
    mock_roster,
    mock_context,
):
    mock_get_body.return_value = {}

    mock_roster.return_value = make_mock_result([PROFILE_DATA])

    res = employees.get_personnel_roster_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_personnel_roster")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_get_personnel_roster_v1_custom_page_sort_columns(
    mock_get_body,
    mock_roster,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {},
        "page": {
            "limit": 25,
        },
        "sort": {
            "field": "lastName",
            "order": "desc",
        },
        "columns": [
            "employeeId",
            "lastName",
        ],
    }

    mock_roster.return_value = make_mock_result([PROFILE_DATA])

    res = employees.get_personnel_roster_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Blank Route Handlers
# ============================================================


@pytest.mark.parametrize(
    "handler",
    [
        employees.get_employee_direct_reports_blank_v1,
        employees.get_org_blank_v1,
        employees.get_employees_by_clearance_blank_v1,
        employees.get_employee_profile_blank_v1,
        employees.get_training_by_status_blank_v1,
        employees.get_training_by_org_blank_v1,
        employees.get_training_by_type_blank_v1,
        employees.get_employee_training_blank_v1,
    ],
)
def test_blank_handlers(
    handler,
    mock_context,
):
    res = handler(
        {},
        mock_context,
    )

    assert res["statusCode"] == 400

    body = str(res["body"])

    assert (
        "Missing" in body
        or "missing" in body
        or "required" in body
    )


# ============================================================
# Employee Direct Reports
# ============================================================


@patch("v1.handlers.employees.get_direct_reports")
def test_get_employee_direct_reports_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "mgr_empl_id": "999999",
        },
        "queryStringParameters": {
            "limit": "5",
        },
    }

    res = employees.get_employee_direct_reports_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert len(body["data"]) == 1


def test_get_employee_direct_reports_v1_missing_id(
    mock_context,
):
    res = employees.get_employee_direct_reports_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_direct_reports")
def test_get_employee_direct_reports_v1_not_found(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "mgr_empl_id": "999",
        }
    }

    res = employees.get_employee_direct_reports_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 404


@patch("v1.handlers.employees.get_direct_reports")
def test_get_employee_direct_reports_v1_custom_query(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "mgr_empl_id": "999999",
        },
        "queryStringParameters": {
            "limit": "5",
            "cursor": "NEXT",
            "sortField": "LAST_NAME",
            "sortOrder": "desc",
            "columns": "employeeId,lastName",
        },
    }

    res = employees.get_employee_direct_reports_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Employees by Organization
# ============================================================


@patch("v1.handlers.employees.get_employees_in_org")
def test_get_employees_by_org_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        }
    }

    res = employees.get_employees_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


def test_get_employees_by_org_v1_missing_id(
    mock_context,
):
    res = employees.get_employees_by_org_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_employees_in_org")
def test_get_employees_by_org_v1_not_found(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        }
    }

    res = employees.get_employees_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 404


@patch("v1.handlers.employees.get_employees_in_org")
def test_get_employees_by_org_v1_custom_arguments(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        },
        "queryStringParameters": {
            "limit": "5",
            "cursor": "NEXT",
            "sortField": "LAST_NAME",
            "sortOrder": "desc",
        },
    }

    res = employees.get_employees_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Employees by Clearance
# ============================================================


@patch("v1.handlers.employees.get_employees_by_clearance")
def test_get_employees_by_clearance_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "status": "ACTIVE",
        }
    }

    res = employees.get_employees_by_clearance_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


def test_get_employees_by_clearance_v1_missing_status(
    mock_context,
):
    res = employees.get_employees_by_clearance_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_employees_by_clearance")
def test_get_employees_by_clearance_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "status": "ACTIVE",
        }
    }

    res = employees.get_employees_by_clearance_v1(
        event,
        mock_context,
    )

    body = response_body(res)

    assert res["statusCode"] == 200
    assert body["data"] == []


@patch("v1.handlers.employees.get_employees_by_clearance")
def test_get_employees_by_clearance_v1_custom_arguments(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "status": "ACTIVE",
        },
        "queryStringParameters": {
            "limit": "5",
            "cursor": "NEXT",
            "sortField": "LAST_NAME",
            "sortOrder": "desc",
        },
    }

    res = employees.get_employees_by_clearance_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Employee Profile by ID
# ============================================================


@patch("v1.handlers.employees.get_employee_by_id")
def test_get_employee_profile_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([PROFILE_DATA])

    event = {
        "pathParameters": {
            "empl_id": "111123",
        }
    }

    res = employees.get_employee_profile_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


def test_get_employee_profile_v1_missing_id(
    mock_context,
):
    res = employees.get_employee_profile_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_employee_by_id")
def test_get_employee_profile_v1_not_found(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "empl_id": "111123",
        }
    }

    res = employees.get_employee_profile_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 404


def test_get_employee_profile_v1_search_word(
    mock_context,
):
    event = {
        "pathParameters": {
            "empl_id": "search",
        }
    }

    res = employees.get_employee_profile_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 400


# ============================================================
# Employee Training Search
# ============================================================


@patch("v1.handlers.employees.get_all_training")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_training_v1_success(
    mock_get_body,
    mock_get_all,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {},
        "sort": {},
        "page": {},
    }

    mock_get_all.return_value = make_mock_result(
        [TRAINING_DATA]
    )

    res = employees.search_employee_training_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_training_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "msg",
        "doc",
        0,
    )

    res = employees.search_employee_training_v1(
        {
            "body": "{",
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_all_training")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_training_v1_empty(
    mock_get_body,
    mock_get_all,
    mock_context,
):
    mock_get_body.return_value = {}

    mock_get_all.return_value = make_mock_result([])

    res = employees.search_employee_training_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert body["data"] == []


# ============================================================
# Training Missing Parameter Tests
# ============================================================


@pytest.mark.parametrize(
    "handler,path_param,value",
    [
        (
            employees.get_training_by_status_v1,
            "status",
            "ACTIVE",
        ),
        (
            employees.get_training_by_org_v1,
            "org_id",
            "ORG1",
        ),
        (
            employees.get_training_by_type_v1,
            "record_type",
            "CERT",
        ),
        (
            employees.get_employee_training_v1,
            "empl_id",
            "123",
        ),
    ],
)
@patch("v1.handlers.employees.LambdaUtils.get_path_param")
def test_get_training_variations_missing_id(
    mock_get_path_param,
    handler,
    path_param,
    value,
    mock_context,
):
    mock_get_path_param.return_value = None

    res = handler(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


# ============================================================
# Training by Status
# ============================================================


@patch("v1.handlers.employees.get_training_by_status")
def test_get_training_by_status_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result(
        [TRAINING_DATA]
    )

    event = {
        "pathParameters": {
            "status": "ACTIVE",
        }
    }

    res = employees.get_training_by_status_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_training_by_status")
def test_get_training_by_status_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "status": "ACTIVE",
        }
    }

    res = employees.get_training_by_status_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200

    body = response_body(res)

    assert body["data"] == []


# ============================================================
# Training by Organization
# ============================================================


@patch("v1.handlers.employees.get_training_by_org")
def test_get_training_by_org_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result(
        [TRAINING_DATA]
    )

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        }
    }

    res = employees.get_training_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_training_by_org")
def test_get_training_by_org_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        }
    }

    res = employees.get_training_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Training by Type
# ============================================================


@patch("v1.handlers.employees.get_training_by_type")
def test_get_training_by_type_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result(
        [TRAINING_DATA]
    )

    event = {
        "pathParameters": {
            "record_type": "CERT",
        }
    }

    res = employees.get_training_by_type_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_training_by_type")
def test_get_training_by_type_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "record_type": "CERT",
        }
    }

    res = employees.get_training_by_type_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Training by Employee
# ============================================================


@patch("v1.handlers.employees.get_training_by_employee")
def test_get_employee_training_v1_success(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result(
        [TRAINING_DATA]
    )

    event = {
        "pathParameters": {
            "empl_id": "123456",
        }
    }

    res = employees.get_employee_training_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_training_by_employee")
def test_get_employee_training_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "empl_id": "123456",
        }
    }

    res = employees.get_employee_training_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Employee Certifications Search
# ============================================================


@patch("v1.handlers.employees.get_all_certifications")
@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_certifications_v1_empty(
    mock_get_body,
    mock_service,
    mock_context,
):
    """
    Empty certification search still executes the complete
    handler response-generation path without depending on the
    exact certification item schema.
    """

    mock_get_body.return_value = {
        "filters": {},
        "sort": {},
        "page": {},
    }

    mock_service.return_value = make_mock_result([])

    res = employees.search_employee_certifications_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.LambdaUtils.get_json_body")
def test_search_employee_certifications_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "msg",
        "doc",
        0,
    )

    res = employees.search_employee_certifications_v1(
        {
            "body": "{",
        },
        mock_context,
    )

    assert res["statusCode"] == 400


# ============================================================
# Certification Blank Routes
# ============================================================


@pytest.mark.parametrize(
    "handler",
    [
        employees.get_certifications_by_status_blank_v1,
        employees.get_certifications_by_org_blank_v1,
        employees.get_employee_certifications_blank_v1,
    ],
)
def test_certification_blank_handlers(
    handler,
    mock_context,
):
    res = handler(
        {},
        mock_context,
    )

    assert res["statusCode"] == 400


# ============================================================
# Certifications by Status
# ============================================================


def test_get_certifications_by_status_v1_missing_status(
    mock_context,
):
    res = employees.get_certifications_by_status_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_certifications_by_status")
def test_get_certifications_by_status_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "status": "CURRENT",
        }
    }

    res = employees.get_certifications_by_status_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_certifications_by_status")
def test_get_certifications_by_status_v1_query_args(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "status": "CURRENT",
        },
        "queryStringParameters": {
            "limit": "5",
            "cursor": "NEXT",
            "sortField": "expiration_date",
            "sortOrder": "desc",
        },
    }

    res = employees.get_certifications_by_status_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Certifications by Organization
# ============================================================


def test_get_certifications_by_org_v1_missing_org(
    mock_context,
):
    res = employees.get_certifications_by_org_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_certifications_by_org")
def test_get_certifications_by_org_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        }
    }

    res = employees.get_certifications_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_certifications_by_org")
def test_get_certifications_by_org_v1_query_args(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "org_id": "ORG1",
        },
        "queryStringParameters": {
            "limit": "10",
            "cursor": "NEXT",
            "sortField": "employee_name",
            "sortOrder": "asc",
        },
    }

    res = employees.get_certifications_by_org_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


# ============================================================
# Certifications by Employee
# ============================================================


def test_get_employee_certifications_v1_missing_employee(
    mock_context,
):
    res = employees.get_employee_certifications_v1(
        {
            "pathParameters": {},
        },
        mock_context,
    )

    assert res["statusCode"] == 400


@patch("v1.handlers.employees.get_certifications_by_employee")
def test_get_employee_certifications_v1_empty(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "empl_id": "123456",
        }
    }

    res = employees.get_employee_certifications_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200


@patch("v1.handlers.employees.get_certifications_by_employee")
def test_get_employee_certifications_v1_query_args(
    mock_service,
    mock_context,
):
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "empl_id": "123456",
        },
        "queryStringParameters": {
            "limit": "10",
            "cursor": "NEXT",
            "sortField": "expiration_date",
            "sortOrder": "asc",
        },
    }

    res = employees.get_employee_certifications_v1(
        event,
        mock_context,
    )

    assert res["statusCode"] == 200

