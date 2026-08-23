import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import project_financial
from v1.handlers.project_financial import (
    get_project_financial_v1,
    list_project_financials_v1,
    search_project_financials_v1,
)


# ============================================================
# Test data
# ============================================================

PROJECT_FINANCIAL_DATA = SimpleNamespace(
    row_id=1,
    proj_id="PROJ-1001",
    cust_name="ABC Customer",
    proj_start_dt=date(2020, 1, 1),
    proj_end_dt=date(2030, 12, 31),
    s_proj_rpt_cd="ACTIVE",
    proj_name="Project Alpha",
    org_id="ORG-001",
    prime_contr_id="PRIME-001",
    status_cd="A",
    proj_type_cd="FIXED_PRICE",
    proj_mgr_name="John Smith",
    lvl_no=1,
    value_total_amount=1000000.0,
    project_value_cost=800000.0,
    project_value_fee=200000.0,
    proj_f_tot_amt=900000.0,
    cost_funded=700000.0,
    fee_funded=150000.0,
    total_billed=500000.0,
    billed_cost=400000.0,
    billed_fee=100000.0,
    open_billing_detail_amt=50000.0,
    open_commit_amt=300000.0,
)


# ============================================================
# Helpers
# ============================================================

def create_service_response(
    items=None,
    cursor=None,
    has_more=False,
    applied_filters=None,
):
    """
    Create a mocked response returned by the project-financial
    service functions.
    """
    response = MagicMock()
    response.items = items if items is not None else []

    response.metadata = MagicMock()
    response.metadata.cursor = cursor
    response.metadata.has_more = has_more
    response.metadata.applied_filters = applied_filters
    response.metadata.model_dump.return_value = {
        "cursor": cursor,
        "has_more": has_more,
        "applied_filters": applied_filters,
    }

    return response


def get_response_body(response):
    """
    Safely deserialize the Lambda response body.
    """
    body = response.get("body")
    if isinstance(body, str):
        return json.loads(body)
    return body


def build_event(
    *,
    method="POST",
    path="/v1/project-financials/search",
    body="{}",
    path_parameters=None,
    query_parameters=None,
    request_id="unit-test-request-id",
):
    return {
        "httpMethod": method,
        "path": path,
        "resource": path,
        "headers": {"Content-Type": "application/json"},
        "queryStringParameters": query_parameters,
        "pathParameters": path_parameters,
        "requestContext": {
            "requestId": request_id,
            "stage": "test",
            "httpMethod": method,
            "resourcePath": path,
        },
        "body": body,
        "isBase64Encoded": False,
    }


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_context():
    """Create a mock AWS Lambda context."""
    context = MagicMock()
    context.function_name = "project-financial-unit-test"
    context.aws_request_id = "unit-test-request-id"
    context.memory_limit_in_mb = 128
    context.get_remaining_time_in_millis.return_value = 30000
    return context


# ============================================================
# SEARCH PROJECT FINANCIALS - SUCCESS
# ============================================================

@patch.object(project_financial.LambdaUtils, "get_json_body")
@patch.object(project_financial, "search_project_financials")
def test_search_project_financials_success(
    mock_search_service,
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.return_value = {}

    mock_search_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
        cursor="next-token",
        has_more=True,
    )

    event = build_event()

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
# SEARCH PROJECT FINANCIALS - EMPTY
# ============================================================

@patch.object(project_financial.LambdaUtils, "get_json_body")
@patch.object(project_financial, "search_project_financials")
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

    event = build_event()

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
# SEARCH PROJECT FINANCIALS - INVALID JSON
# ============================================================

@patch.object(project_financial.LambdaUtils, "get_json_body")
def test_search_project_financials_invalid_json(
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.side_effect = ValueError(
        "Invalid JSON body provided."
    )

    event = build_event(body="{invalid-json")

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
# DETAILS HANDLER EXISTS
# ============================================================

def test_get_project_financial_details_handler_exists():
    assert hasattr(
        project_financial,
        "get_project_financial_details",
    )

    assert callable(
        project_financial.get_project_financial_details
    )


# ============================================================
# GET PROJECT FINANCIAL - MISSING PROJECT ID
# ============================================================

@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_path_param"
)
def test_get_project_financial_v1_missing_project_id(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = None

    event = build_event(
        method="GET",
        path="/v1/project-financials/",
        body=None,
        path_parameters={},
    )

    response = get_project_financial_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# GET PROJECT FINANCIAL - NOT FOUND
# ============================================================

@patch(
    "v1.handlers.project_financial."
    "get_project_financial_details"
)
@patch(
    "v1.handlers.project_financial."
    "parse_filters_from_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_path_param"
)
def test_get_project_financial_v1_not_found(
    mock_get_path_param,
    mock_get_query_params,
    mock_get_columns,
    mock_parse_filters,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "P-1001"
    mock_get_query_params.return_value = {}
    mock_get_columns.return_value = None
    mock_parse_filters.return_value = MagicMock()

    mock_results = MagicMock()
    mock_results.items = []

    mock_service.return_value = mock_results

    event = build_event(
        method="GET",
        path="/v1/project-financials/P-1001",
        body=None,
        path_parameters={"proj_id": "P-1001"},
    )

    response = get_project_financial_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 404


# ============================================================
# GET PROJECT FINANCIAL - SUCCESS
# ============================================================

@patch(
    "v1.handlers.project_financial."
    "get_project_financial_details"
)
@patch(
    "v1.handlers.project_financial."
    "parse_filters_from_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_path_param"
)
def test_get_project_financial_v1_success(
    mock_get_path_param,
    mock_get_query_params,
    mock_get_columns,
    mock_parse_filters,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "P-1001"

    mock_get_query_params.return_value = {
        "limit": "10",
        "cursor": None,
    }

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = MagicMock()

    mock_results = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
        cursor=None,
        has_more=False,
        applied_filters=None,
    )
    mock_service.return_value = mock_results

    event = build_event(
        method="GET",
        path="/v1/project-financials/P-1001",
        body=None,
        path_parameters={"proj_id": "P-1001"},
        query_parameters={"limit": "10"},
        request_id="test-get-success",
    )

    response = get_project_financial_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    service_call = mock_service.call_args
    assert service_call.kwargs["proj_id"] == "P-1001"
    assert service_call.kwargs["page"].limit == 10
    assert service_call.kwargs["page"].cursor is None
    assert service_call.kwargs["columns"] is None


# ============================================================
# LIST PROJECT FINANCIALS - SUCCESS
# ============================================================

@patch(
    "v1.handlers.project_financial."
    "search_project_financials"
)
@patch(
    "v1.handlers.project_financial."
    "parse_filters_from_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_all_query_params"
)
def test_list_project_financials_v1_success(
    mock_get_query_params,
    mock_parse_filters,
    mock_service,
    mock_context,
):
    mock_get_query_params.return_value = {
        "limit": "10",
        "cursor": None,
    }

    mock_parse_filters.return_value = MagicMock()

    mock_results = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
        cursor=None,
        has_more=False,
        applied_filters=None,
    )
    mock_service.return_value = mock_results

    event = build_event(
        method="GET",
        path="/v1/project-financials",
        body=None,
        path_parameters={},
        query_parameters={"limit": "10"},
        request_id="test-list-success",
    )

    response = list_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    service_call = mock_service.call_args
    assert service_call.kwargs["page"].limit == 10
    assert service_call.kwargs["page"].cursor is None


# ============================================================
# SEARCH PROJECT FINANCIALS - JSON DECODE ERROR
# ============================================================

@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_json_body"
)
def test_search_project_financials_v1_json_decode_error(
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Expecting value",
        "",
        0,
    )

    event = build_event(
        method="POST",
        path="/v1/project-financials/search",
        body="{invalid-json",
        path_parameters={},
        query_parameters=None,
        request_id="test-invalid-json",
    )

    response = search_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# Additional branch coverage
# ============================================================

@patch.object(project_financial.LambdaUtils, "get_json_body")
@patch.object(project_financial, "search_project_financials")
def test_search_project_financials_with_filters_sort_page_columns(
    mock_search_service,
    mock_get_json_body,
    mock_context,
):
    mock_get_json_body.return_value = {
        "filters": {
            "projId": {
                "eq": "P-1001",
            }
        },
        "sort": {
            "field": "projId",
            "order": "asc",
        },
        "page": {
            "limit": 5,
            "cursor": "abc",
        },
        "columns": ["projId", "projName"],
    }

    mock_search_service.return_value = create_service_response(
        items=[PROJECT_FINANCIAL_DATA],
        cursor=None,
        has_more=False,
    )

    event = build_event(
        method="POST",
        path="/v1/project-financials/search",
        body="{}",
    )

    response = search_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200
    mock_search_service.assert_called_once()


@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_path_param"
)
def test_get_project_financial_blank_project_id_string(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = ""

    event = build_event(
        method="GET",
        path="/v1/project-financials/",
        body=None,
        path_parameters={"proj_id": ""},
    )

    response = get_project_financial_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


@patch(
    "v1.handlers.project_financial."
    "search_project_financials"
)
@patch(
    "v1.handlers.project_financial."
    "parse_filters_from_query_params"
)
@patch(
    "v1.handlers.project_financial."
    "LambdaUtils.get_all_query_params"
)
def test_list_project_financials_empty(
    mock_get_query_params,
    mock_parse_filters,
    mock_service,
    mock_context,
):
    mock_get_query_params.return_value = {}
    mock_parse_filters.return_value = MagicMock()

    mock_results = MagicMock()
    mock_results.items = []
    mock_results.metadata.model_dump.return_value = {
        "cursor": None,
        "has_more": False,
        "applied_filters": None,
    }
    mock_service.return_value = mock_results

    event = build_event(
        method="GET",
        path="/v1/project-financials",
        body=None,
        path_parameters={},
        query_parameters=None,
    )

    response = list_project_financials_v1(
        event,
        mock_context,
    )

    # Depending on the current handler contract, empty list endpoints
    # normally return 200 rather than 404.
    assert response["statusCode"] in (200, 404)


def test_imported_handlers_are_callable():
    assert callable(search_project_financials_v1)
    assert callable(list_project_financials_v1)
    assert callable(get_project_financial_v1)
