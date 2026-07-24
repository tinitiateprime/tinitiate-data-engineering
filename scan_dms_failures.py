import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import project_financial


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
    Create a mocked Project Financial service response.
    """

    result = MagicMock()

    result.items = []

    for row in items or []:
        item = MagicMock()

        # The handler serializes service models using model_dump().
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
    """
    Verify successful Project Financial search.
    """

    # Keep the body empty first.
    # This avoids failing handler validation for filter configuration.
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

    row = body["data"][0]

    assert row["projId"] == "P-1001"
    assert row["custName"] == "Test Customer"
    assert row["projName"] == "Test Project"
    assert row["totalBilled"] == 50000.0
    assert row["openCommitAmt"] == 10000.0

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
    """
    Verify an empty search returns HTTP 200 and an empty data list.
    """

    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[],
        cursor=None,
        has_more=False,
    )

    response = project_financial.search_project_financials_v1(
        {
            "body": "{}",
        },
        mock_context,
    )

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["data"] == []
    assert body["metadata"]["cursor"] is None
    assert body["metadata"]["hasMore"] is False
    assert body["metadata"]["responseVersion"] == "v1"


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

    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "{",
        0,
    )

    response = project_financial.search_project_financials_v1(
        {
            "body": "{",
        },
        mock_context,
    )

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["message"] == "Invalid JSON body provided."
    assert body["details"] == {}


# ============================================================
# Details handler tests
# ============================================================

def test_get_project_financial_details_handler_exists():
    """
    Verify the details handler is available under its actual name.
    """

    assert hasattr(
        project_financial,
        "get_project_financial_details",
    )

    assert callable(
        project_financial.get_project_financial_details
    )
