"""
Unit tests for v1.handlers.employee_profile_complete.

IMPORTANT:
The EmployeeProfileComplete detail endpoint uses:

    empl_id

NOT:

    employee_key
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import employee_profile_complete


# ============================================================
# HELPERS
# ============================================================

def mock_context():
    context = MagicMock()
    context.aws_request_id = "unit-test-request"
    context.function_name = "employee-profile-complete-test"
    context.memory_limit_in_mb = 128
    context.get_remaining_time_in_millis.return_value = 30000
    return context


def response_body(response):
    body = response.get("body")

    if isinstance(body, str):
        return json.loads(body)

    return body


def make_service_result(
    items=None,
    cursor=None,
    has_more=False,
):
    result = MagicMock()

    result.items = (
        items
        if items is not None
        else [{"empl_id": "EMP-1001"}]
    )

    result.metadata = MagicMock()

    result.metadata.cursor = cursor
    result.metadata.has_more = has_more
    result.metadata.applied_filters = None

    result.metadata.model_dump.return_value = {
        "cursor": cursor,
        "has_more": has_more,
        "applied_filters": None,
    }

    return result


def make_response_model(payload):
    model = MagicMock()
    model.model_dump.return_value = payload
    return model


# ============================================================
# IMPORT / EXISTENCE TESTS
# ============================================================

def test_handler_functions_exist():
    assert callable(
        employee_profile_complete
        .get_employee_profile_complete_v1
    )

    assert callable(
        employee_profile_complete
        .search_employee_profile_completes_v1
    )

    assert callable(
        employee_profile_complete
        .list_employee_profile_completes_v1
    )


# ============================================================
# GET EMPLOYEE PROFILE COMPLETE - SUCCESS
# ============================================================

def test_get_employee_profile_complete_v1_success():
    context = mock_context()

    service_result = make_service_result(
        items=[{"empl_id": "EMP-1001"}]
    )

    final_payload = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "emplId": "EMP-1001",
                "employeeKey": "EMPLOYEE-KEY-001",
            }
        ],
    }

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/EMP-1001",
        "resource": "/v1/employee-profile-complete/EMP-1001",
        "pathParameters": {
            # IMPORTANT
            "empl_id": "EMP-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-detail-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_path_param",
            return_value="EMP-1001",
        ) as mock_path,
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={},
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "get_employee_profile_complete_details",
            return_value=service_result,
        ) as mock_service,
        patch.object(
            employee_profile_complete
            .V1EmployeeProfileCompleteResponseModel,
            "model_validate",
            side_effect=lambda item: item,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteDetailResponseModel",
            return_value=make_response_model(
                final_payload
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200

    mock_path.assert_called_once_with(
        event,
        "empl_id",
    )

    mock_service.assert_called_once()

    service_kwargs = mock_service.call_args.kwargs

    # ============================================
    # MOST IMPORTANT ASSERTIONS
    # ============================================

    assert service_kwargs["empl_id"] == "EMP-1001"

    assert "employee_key" not in service_kwargs


# ============================================================
# GET - MISSING EMPL_ID
# ============================================================

def test_get_employee_profile_complete_v1_missing_id():
    context = mock_context()

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/",
        "resource": "/v1/employee-profile-complete/",
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-detail-missing",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with patch.object(
        employee_profile_complete.LambdaUtils,
        "get_path_param",
        return_value=None,
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 400

    body = response_body(response)

    body_text = json.dumps(body)

    assert "empl_id" in body_text


# ============================================================
# GET - EMPTY EMPL_ID
# ============================================================

def test_get_employee_profile_complete_v1_blank_id():
    context = mock_context()

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/",
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-detail-blank",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with patch.object(
        employee_profile_complete.LambdaUtils,
        "get_path_param",
        return_value="",
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 400


# ============================================================
# GET - NOT FOUND
# ============================================================

def test_get_employee_profile_complete_v1_not_found():
    context = mock_context()

    service_result = make_service_result(
        items=[]
    )

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/EMP-9999",
        "pathParameters": {
            "empl_id": "EMP-9999",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-detail-not-found",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_path_param",
            return_value="EMP-9999",
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={},
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "get_employee_profile_complete_details",
            return_value=service_result,
        ),
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 404


# ============================================================
# GET - QUERY PARAMETERS
# ============================================================

def test_get_employee_profile_complete_v1_query_parameters():
    context = mock_context()

    service_result = make_service_result()

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/EMP-1001",
        "pathParameters": {
            "empl_id": "EMP-1001",
        },
        "queryStringParameters": {
            "limit": "25",
            "cursor": "NEXT-CURSOR",
        },
        "requestContext": {
            "requestId": "test-detail-query",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    final_payload = {
        "metadata": {},
        "data": [],
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_path_param",
            return_value="EMP-1001",
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={
                "limit": "25",
                "cursor": "NEXT-CURSOR",
            },
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=[
                "empl_id",
                "first_name",
            ],
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "get_employee_profile_complete_details",
            return_value=service_result,
        ) as mock_service,
        patch.object(
            employee_profile_complete
            .V1EmployeeProfileCompleteResponseModel,
            "model_validate",
            side_effect=lambda item: item,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteDetailResponseModel",
            return_value=make_response_model(
                final_payload
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200

    kwargs = mock_service.call_args.kwargs

    assert kwargs["empl_id"] == "EMP-1001"
    assert kwargs["limit"] == 25
    assert kwargs["cursor"] == "NEXT-CURSOR"

    assert kwargs["columns"] == [
        "empl_id",
        "first_name",
    ]


# ============================================================
# SEARCH - SUCCESS
# ============================================================

def test_search_employee_profile_completes_v1_success():
    context = mock_context()

    event = {
        "httpMethod": "POST",
        "path": "/v1/employee-profile-complete/search",
        "resource": "/v1/employee-profile-complete/search",
        "headers": {
            "Content-Type": "application/json",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "requestContext": {
            "requestId": "test-search-success",
        },
        "body": "{}",
        "isBase64Encoded": False,
    }

    service_result = make_service_result(
        items=[{"empl_id": "EMP-1001"}]
    )

    final_payload = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "emplId": "EMP-1001",
            }
        ],
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_json_body",
            return_value={
                "filters": {},
                "sort": {},
                "page": {},
            },
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "search_employee_profile_completes",
            return_value=service_result,
        ) as mock_service,
        patch.object(
            employee_profile_complete
            .V1EmployeeProfileCompleteResponseModel,
            "model_validate",
            side_effect=lambda item: item,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteListResponseModel",
            return_value=make_response_model(
                final_payload
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .search_employee_profile_completes_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    kwargs = mock_service.call_args.kwargs

    assert "filters" in kwargs
    assert "sort" in kwargs
    assert "page" in kwargs
    assert "columns" in kwargs


# ============================================================
# SEARCH - INVALID JSON
# ============================================================

def test_search_employee_profile_completes_v1_invalid_json():
    context = mock_context()

    event = {
        "httpMethod": "POST",
        "path": "/v1/employee-profile-complete/search",
        "requestContext": {
            "requestId": "test-invalid-json",
        },
        "body": "{invalid-json",
        "isBase64Encoded": False,
    }

    with patch.object(
        employee_profile_complete.LambdaUtils,
        "get_json_body",
        side_effect=json.JSONDecodeError(
            "Expecting value",
            "{invalid-json",
            0,
        ),
    ):
        response = (
            employee_profile_complete
            .search_employee_profile_completes_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 400


# ============================================================
# SEARCH - EMPTY RESULTS
# ============================================================

def test_search_employee_profile_completes_v1_empty():
    context = mock_context()

    event = {
        "httpMethod": "POST",
        "path": "/v1/employee-profile-complete/search",
        "requestContext": {
            "requestId": "test-search-empty",
        },
        "body": "{}",
        "isBase64Encoded": False,
    }

    service_result = make_service_result(
        items=[]
    )

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_json_body",
            return_value={
                "filters": {},
                "sort": {},
                "page": {},
            },
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "search_employee_profile_completes",
            return_value=service_result,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteListResponseModel",
            return_value=make_response_model(
                {
                    "metadata": {},
                    "data": [],
                }
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .search_employee_profile_completes_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200


# ============================================================
# LIST - SUCCESS
# ============================================================

def test_list_employee_profile_completes_v1_success():
    context = mock_context()

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete",
        "resource": "/v1/employee-profile-complete",
        "pathParameters": None,
        "queryStringParameters": {
            "limit": "10",
        },
        "requestContext": {
            "requestId": "test-list-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    service_result = make_service_result(
        items=[{"empl_id": "EMP-1001"}]
    )

    final_payload = {
        "metadata": {},
        "data": [
            {
                "emplId": "EMP-1001",
            }
        ],
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={
                "limit": "10",
            },
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "search_employee_profile_completes",
            return_value=service_result,
        ) as mock_service,
        patch.object(
            employee_profile_complete
            .V1EmployeeProfileCompleteResponseModel,
            "model_validate",
            side_effect=lambda item: item,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteListResponseModel",
            return_value=make_response_model(
                final_payload
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .list_employee_profile_completes_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()


# ============================================================
# LIST - EMPTY
# ============================================================

def test_list_employee_profile_completes_v1_empty():
    context = mock_context()

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete",
        "pathParameters": None,
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-list-empty",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    service_result = make_service_result(
        items=[]
    )

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={},
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "search_employee_profile_completes",
            return_value=service_result,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteListResponseModel",
            return_value=make_response_model(
                {
                    "metadata": {},
                    "data": [],
                }
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .list_employee_profile_completes_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200


# ============================================================
# REGRESSION - EMPL_ID CONTRACT
# ============================================================

def test_detail_handler_uses_empl_id_not_employee_key():
    """
    Protect the corrected API contract.

    The route is:

        /v1/employee-profile-complete/{empl_id}

    The handler must retrieve "empl_id".
    """

    context = mock_context()

    result = make_service_result(
        items=[]
    )

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/EMP-1001",
        "pathParameters": {
            "empl_id": "EMP-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-empl-id-contract",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_path_param",
            return_value="EMP-1001",
        ) as mock_path,
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={},
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "get_employee_profile_complete_details",
            return_value=result,
        ),
    ):
        employee_profile_complete.get_employee_profile_complete_v1(
            event,
            context,
        )

    mock_path.assert_called_once_with(
        event,
        "empl_id",
    )


# ============================================================
# REGRESSION - SERVICE CALL CONTRACT
# ============================================================

def test_detail_handler_passes_empl_id_to_service():
    context = mock_context()

    service_result = make_service_result(
        items=[{"empl_id": "EMP-1001"}]
    )

    event = {
        "httpMethod": "GET",
        "path": "/v1/employee-profile-complete/EMP-1001",
        "pathParameters": {
            "empl_id": "EMP-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-service-contract",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    with (
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_path_param",
            return_value="EMP-1001",
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_all_query_params",
            return_value={},
        ),
        patch.object(
            employee_profile_complete.LambdaUtils,
            "get_columns_query_parameter",
            return_value=None,
        ),
        patch.object(
            employee_profile_complete,
            "parse_filters_from_query_params",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "get_employee_profile_complete_details",
            return_value=service_result,
        ) as mock_service,
        patch.object(
            employee_profile_complete
            .V1EmployeeProfileCompleteResponseModel,
            "model_validate",
            side_effect=lambda item: item,
        ),
        patch.object(
            employee_profile_complete,
            "V1MetadataModel",
            return_value=MagicMock(),
        ),
        patch.object(
            employee_profile_complete,
            "V1EmployeeProfileCompleteDetailResponseModel",
            return_value=make_response_model(
                {
                    "metadata": {},
                    "data": [],
                }
            ),
        ),
    ):
        response = (
            employee_profile_complete
            .get_employee_profile_complete_v1(
                event,
                context,
            )
        )

    assert response["statusCode"] == 200

    kwargs = mock_service.call_args.kwargs

    assert kwargs["empl_id"] == "EMP-1001"

    # This caused the GitLab failure before.
    assert "employee_key" not in kwargs
