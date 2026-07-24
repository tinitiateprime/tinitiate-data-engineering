import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import project_financial


PROJECT_FINANCIAL_DATA = {
    "proj_id": "P-1001",
}


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
        item.model_dump.return_value = row
        result.items.append(item)

    result.metadata = MagicMock()
    result.metadata.model_dump.return_value = {
        "cursor": cursor,
        "has_more": has_more,
        "applied_filters": None,
    }

    return result


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
    """Verify a successful Project Financial search."""

    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
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
    """Verify an empty search returns HTTP 200."""

    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[],
        cursor=None,
        has_more=False,
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

    assert body["data"] == []
    assert body["metadata"]["cursor"] is None
    assert body["metadata"]["hasMore"] is False
    assert body["metadata"]["responseVersion"] == "v1"

    mock_search_service.assert_called_once()


@patch.object(
    project_financial.LambdaUtils,
    "get_json_body",
)
def test_search_project_financials_invalid_json(
    mock_get_json_body,
    mock_context,
):
    """Verify invalid JSON returns HTTP 400."""

    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "{",
        0,
    )

    event = {
        "body": "{",
    }

    response = project_financial.search_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400

    # Do not assume the error message is stored under a particular key.
    # Check the complete serialized response instead.
    assert "Invalid JSON body provided." in response["body"]


# ============================================================
# Details handler test
# ============================================================

def test_get_project_financial_details_handler_exists():
    """
    Verify the details handler exists.

    The current handler function is named:
    get_project_financial_details
    """

    assert hasattr(
        project_financial,
        "get_project_financial_details",
    )

    assert callable(
        project_financial.get_project_financial_details
    )
