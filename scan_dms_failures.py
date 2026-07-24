"""
Unit tests for the Project Financial V1 Lambda handlers.
"""

import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# IMPORTANT:
# Keep the project_financial import that already works in your file.
#
# For example, your existing import may look similar to:
#
# from handlers.v1 import project_financial
# from src.handlers.v1 import project_financial
# from functions.v1 import project_financial
#
# Replace the next line with your existing working import.
from v1 import project_financial


# ============================================================
# Test data
# ============================================================

PROJECT_FINANCIAL_DATA = SimpleNamespace(
    projId="PROJ-1001",
    custName="ABC Customer",
    projStartDt=date(2026, 1, 1),
    projEndDt=date(2026, 12, 31),
    sProjRptDc="ACTIVE",
    projName="Project Alpha",
    orgId="ORG-001",
    primeContrId="PRIME-001",
    activeFl="Y",
    projTypeDc="FIXED_PRICE",
    projMgrName="John Smith",
)


# ============================================================
# Test helper
# ============================================================

def create_service_response(
    items=None,
    cursor=None,
    has_more=False,
):
    """
    Create the mocked response returned by the
    search_project_financials service function.
    """
    response = MagicMock()

    response.items = items if items is not None else []
    response.cursor = cursor
    response.has_more = has_more

    return response


def get_response_body(response):
    """
    Safely deserialize the Lambda response body.
    """
    body = response.get("body")

    if isinstance(body, str):
        return json.loads(body)

    return body


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_context():
    """
    Create a mock AWS Lambda context.
    """
    context = MagicMock()

    context.function_name = "project-financial-unit-test"
    context.aws_request_id = "unit-test-request-id"
    context.memory_limit_in_mb = 128
    context.get_remaining_time_in_millis.return_value = 30000

    return context


# ============================================================
# Successful search test
# ============================================================

@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
@patch.object(
    project_financial,
    "search_project_financials",
)
def test_search_project_financials_success(
    mock_search_service,
    mock_get_json_body,
    mock_context,
):
    """
    Verify a successful Project Financial search.
    """

    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
        cursor="next-token",
        has_more=True,
    )

    event = {
        "httpMethod": "POST",
        "path": "/v1/project-financials/search",
        "resource": "/v1/project-financials/search",
        "headers": {
            "Content-Type": "application/json",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "requestContext": {
            "requestId": "unit-test-request-id",
            "stage": "test",
            "httpMethod": "POST",
            "resourcePath": "/v1/project-financials/search",
        },
        "body": "{}",
        "isBase64Encoded": False,
    }

    response = project_financial.search_project_financials_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)
    assert response["statusCode"] == 200
    assert "body" in response

    response_body = get_response_body(response)

    assert response_body is not None

    mock_get_json_body.assert_called_once()
    mock_search_service.assert_called_once()


# ============================================================
# Empty request test
# ============================================================

@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
@patch.object(
    project_financial,
    "search_project_financials",
)
def test_search_project_financials_empty(
    mock_search_service,
    mock_get_json_body,
    mock_context,
):
    """
    Verify a search that returns no Project Financial records.
    """

    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[],
        cursor=None,
        has_more=False,
    )

    event = {
        "httpMethod": "POST",
        "path": "/v1/project-financials/search",
        "resource": "/v1/project-financials/search",
        "headers": {
            "Content-Type": "application/json",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "requestContext": {
            "requestId": "unit-test-request-id",
            "stage": "test",
            "httpMethod": "POST",
            "resourcePath": "/v1/project-financials/search",
        },
        "body": "{}",
        "isBase64Encoded": False,
    }

    response = project_financial.search_project_financials_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)
    assert response["statusCode"] == 200
    assert "body" in response

    response_body = get_response_body(response)

    assert response_body is not None

    mock_get_json_body.assert_called_once()
    mock_search_service.assert_called_once()


# ============================================================
# Invalid JSON test
# ============================================================

@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
def test_search_project_financials_invalid_json(
    mock_get_json_body,
    mock_context,
):
    """
    Verify invalid JSON returns HTTP 400.
    """

    mock_get_json_body.side_effect = ValueError(
        "Invalid JSON body provided."
    )

    event = {
        "httpMethod": "POST",
        "path": "/v1/project-financials/search",
        "resource": "/v1/project-financials/search",
        "headers": {
            "Content-Type": "application/json",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "requestContext": {
            "requestId": "unit-test-request-id",
            "stage": "test",
            "httpMethod": "POST",
            "resourcePath": "/v1/project-financials/search",
        },
        "body": "{invalid-json",
        "isBase64Encoded": False,
    }

    response = project_financial.search_project_financials_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)
    assert response["statusCode"] == 400
    assert "body" in response

    response_body = get_response_body(response)
    response_text = json.dumps(response_body)

    assert "Invalid JSON body provided." in response_text

    mock_get_json_body.assert_called_once()


# ============================================================
# Details handler existence test
# ============================================================

def test_get_project_financial_details_handler_exists():
    """
    Verify the Project Financial details handler exists.
    """

    assert hasattr(
        project_financial,
        "get_project_financial_details",
    )

    assert callable(
        project_financial.get_project_financial_details
    )
