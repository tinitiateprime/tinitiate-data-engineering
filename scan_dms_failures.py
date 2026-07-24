import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import project_financial


@pytest.fixture
def mock_context():
    """Create a mock AWS Lambda context."""
    context = MagicMock()
    context.aws_request_id = "test-request-id"
    context.function_name = "project-financial-test"
    return context


def create_service_response(
    items=None,
    cursor=None,
    has_more=False,
):
    """
    Create a mock response matching the object returned by
    project_financial_service.
    """
    result = MagicMock()

    result.items = []

    for row in items or []:
        item = MagicMock()

        # Handler calls model_dump() on each Pydantic response item.
        item.model_dump.return_value = row
        result.items.append(item)

    result.metadata = MagicMock()
    result.metadata.model_dump.return_value = {
        "cursor": cursor,
        "has_more": has_more,
        "applied_filters": None,
    }

    return result


PROJECT_FINANCIAL_ROW = {
    "proj_id": "P-1001",
    "cust_name": "Test Customer",
    "proj_name": "Test Project",
    "active_fl": "Y",
    "total_billed": 50000.00,
    "open_commit_amt": 10000.00,
}


# ============================================================
# Search handler tests
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
    mock_get_json_body.return_value = {
        "filters": {
            "active_fl": {
                "eq": "Y",
            }
        },
        "page": {
            "limit": 10,
        },
    }

    mock_search_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_ROW],
        cursor="next-token",
        has_more=True,
    )

    event = {
        "body": "{}",
    }

    response = project_financial.search_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body["data"]) == 1
    assert body["data"][0]["projId"] == "P-1001"
    assert body["data"][0]["projName"] == "Test Project"
    assert body["data"][0]["totalBilled"] == 50000.00

    assert body["metadata"]["cursor"] == "next-token"
    assert body["metadata"]["hasMore"] is True
    assert body["metadata"]["responseVersion"] == "v1"

    mock_search_service.assert_called_once()


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
    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[],
        cursor=None,
        has_more=False,
    )

    response = project_financial.search_project_financials_v1(
        {"body": "{}"},
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["data"] == []
    assert body["metadata"]["cursor"] is None
    assert body["metadata"]["hasMore"] is False


@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
def test_search_project_financials_invalid_json(
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "{",
        0,
    )

    response = project_financial.search_project_financials_v1(
        {"body": "{"},
        mock_context,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "Invalid JSON" in body["error"]


# ============================================================
# Project financial details handler tests
# ============================================================

@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
@patch.object(
    project_financial,
    "get_project_financial_details",
)
def test_get_project_financial_details_success(
    mock_details_service,
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.return_value = {
        "limit": 10,
    }

    mock_details_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_ROW],
        cursor=None,
        has_more=False,
    )

    event = {
        "pathParameters": {
            "proj_id": "P-1001",
        },
        "body": "{}",
    }

    response = project_financial.get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body["data"]) == 1
    assert body["data"][0]["projId"] == "P-1001"
    assert body["data"][0]["custName"] == "Test Customer"
    assert body["metadata"]["hasMore"] is False

    mock_details_service.assert_called_once()


@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
@patch.object(
    project_financial,
    "get_project_financial_details",
)
def test_get_project_financial_details_empty(
    mock_details_service,
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.return_value = {}

    mock_details_service.return_value = create_service_response(
        items=[],
        cursor=None,
        has_more=False,
    )

    event = {
        "pathParameters": {
            "proj_id": "NOT-FOUND",
        },
        "body": "{}",
    }

    response = project_financial.get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["data"] == []
    assert body["metadata"]["hasMore"] is False


@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
def test_get_project_financial_details_missing_project_id(
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.return_value = {}

    event = {
        "pathParameters": {},
        "body": "{}",
    }

    response = project_financial.get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "proj_id is required" in body["error"]
