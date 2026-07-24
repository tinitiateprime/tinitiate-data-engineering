# main-function/tests/unit/v1/test_project_financial.py

import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers.project_financial import (
    get_project_financial_details_v1,
    search_project_financials_v1,
)


PROJECT_FINANCIAL_DATA = {
    "proj_id": "P-1001",
    "cust_name": "Test Customer",
    "proj_start_dt": "2026-01-01",
    "proj_end_dt": "2026-12-31",
    "s_proj_rpt_dc": "ACTIVE",
    "proj_name": "Test Project",
    "org_id": "ORG-100",
    "prime_contr_id": "CONT-100",
    "active_fl": "Y",
    "proj_type_dc": "FIXED_PRICE",
    "proj_mgr_name": "Test Manager",
    "lvl_no": 1,
    "value_total_amount": 100000.0,
    "project_value_cost": 70000.0,
    "project_value_fee": 30000.0,
    "proj_f_tot_amt": 100000.0,
    "cost_funded": 65000.0,
    "fee_funded": 25000.0,
    "total_billed": 50000.0,
    "billed_cost": 35000.0,
    "billed_fee": 15000.0,
    "open_billing_detail_amt": 5000.0,
    "open_commit_amt": 10000.0,
}


def make_mock_result(items_data):
    """Mock the response returned by the service."""
    result = MagicMock()

    result.items = []
    for row in items_data:
        item = MagicMock()
        item.model_dump.return_value = row
        result.items.append(item)

    result.metadata = MagicMock()
    result.metadata.model_dump.return_value = {
        "cursor": None,
        "has_more": False,
        "applied_filters": None,
    }

    return result


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.aws_request_id = "test-request-id"
    return context


# ---------------------------------------------------------------------------
# Search handler
# ---------------------------------------------------------------------------

@patch("v1.handlers.project_financial.search_project_financials")
@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_search_project_financials_v1_success(
    mock_get_body,
    mock_service,
    mock_context,
):
    mock_get_body.return_value = {
        "filters": {
            "proj_id": {
                "eq": "P-1001",
            }
        },
        "page": {
            "limit": 10,
        },
    }

    mock_service.return_value = make_mock_result(
        [PROJECT_FINANCIAL_DATA]
    )

    response = search_project_financials_v1(
        {"body": "{}"},
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body["data"]) == 1
    assert body["data"][0]["projId"] == "P-1001"
    assert body["data"][0]["projName"] == "Test Project"
    assert body["metadata"]["responseVersion"] == "v1"


@patch("v1.handlers.project_financial.search_project_financials")
@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_search_project_financials_v1_empty_returns_200(
    mock_get_body,
    mock_service,
    mock_context,
):
    mock_get_body.return_value = {}
    mock_service.return_value = make_mock_result([])

    response = search_project_financials_v1(
        {"body": "{}"},
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["data"] == []
    assert body["metadata"]["hasMore"] is False


@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_search_project_financials_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "document",
        0,
    )

    response = search_project_financials_v1(
        {"body": "{"},
        mock_context,
    )

    assert response["statusCode"] == 400
    assert "Invalid JSON" in response["body"]


# ---------------------------------------------------------------------------
# Details handler
# ---------------------------------------------------------------------------

@patch("v1.handlers.project_financial.get_project_financial_details")
@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_get_project_financial_details_v1_success(
    mock_get_body,
    mock_service,
    mock_context,
):
    mock_get_body.return_value = {}
    mock_service.return_value = make_mock_result(
        [PROJECT_FINANCIAL_DATA]
    )

    event = {
        "pathParameters": {
            "proj_id": "P-1001",
        },
        "body": "{}",
    }

    response = get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body["data"]) == 1
    assert body["data"][0]["projId"] == "P-1001"
    assert body["data"][0]["totalBilled"] == 50000.0


@patch("v1.handlers.project_financial.get_project_financial_details")
@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_get_project_financial_details_v1_not_found(
    mock_get_body,
    mock_service,
    mock_context,
):
    mock_get_body.return_value = {}
    mock_service.return_value = make_mock_result([])

    event = {
        "pathParameters": {
            "proj_id": "NON-EXISTENT",
        },
        "body": "{}",
    }

    response = get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["data"] == []


@patch("v1.handlers.project_financial.LambdaUtils.get_json_body")
def test_get_project_financial_details_v1_invalid_json(
    mock_get_body,
    mock_context,
):
    mock_get_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "document",
        0,
    )

    event = {
        "pathParameters": {
            "proj_id": "P-1001",
        },
        "body": "{",
    }

    response = get_project_financial_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400
    assert "Invalid JSON" in response["body"]
