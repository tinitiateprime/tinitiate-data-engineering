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

    event = {
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-invalid-json",
        },
        "body": "{invalid-json",
        "isBase64Encoded": False,
    }

    response = search_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400

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

    event = {
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-missing-proj-id",
        },
        "body": None,
        "isBase64Encoded": False,
    }

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

    event = {
        "pathParameters": {
            "proj_id": "P-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-not-found",
        },
        "body": None,
        "isBase64Encoded": False,
    }

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
    "V1ProjectFinancialResponseModel"
)
@patch(
    "v1.handlers.project_financial."
    "V1ProjectFinancialDetailResponseModel"
)
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
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
    mock_get_path_param.return_value = "P-1001"

    mock_get_query_params.return_value = {
        "limit": "10",
        "cursor": None,
    }

    mock_get_columns.return_value = None

    mock_filters = MagicMock()
    mock_parse_filters.return_value = mock_filters

    mock_item = MagicMock()

    mock_results = MagicMock()
    mock_results.items = [mock_item]
    mock_results.metadata.applied_filters = None

    mock_results.metadata.model_dump.return_value = {
        "cursor": None,
        "has_more": False,
        "applied_filters": None,
    }

    mock_service.return_value = mock_results

    validated_item = MagicMock()
    mock_inner_schema.model_validate.return_value = (
        validated_item
    )

    mock_response = MagicMock()

    mock_response.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "projId": "P-1001",
            }
        ],
    }

    mock_outer_schema.return_value = mock_response

    event = {
        "pathParameters": {
            "proj_id": "P-1001",
        },
        "queryStringParameters": {
            "limit": "10",
        },
        "requestContext": {
            "requestId": "test-get-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_project_financial_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    service_call = mock_service.call_args

    assert service_call.kwargs["proj_id"] == "P-1001"
    assert service_call.kwargs["limit"] == 10
    assert service_call.kwargs["cursor"] is None
    assert service_call.kwargs["columns"] is None

    mock_outer_schema.assert_called_once()


# ============================================================
# LIST PROJECT FINANCIALS - SUCCESS
# ============================================================
@patch(
    "v1.handlers.project_financial."
    "V1ProjectFinancialResponseModel"
)
@patch(
    "v1.handlers.project_financial."
    "V1ProjectFinancialListResponseModel"
)
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
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
    mock_get_query_params.return_value = {
        "limit": "10",
        "cursor": None,
    }

    mock_filters = MagicMock()
    mock_parse_filters.return_value = mock_filters

    mock_item = MagicMock()

    mock_results = MagicMock()
    mock_results.items = [mock_item]

    mock_results.metadata.model_dump.return_value = {
        "cursor": None,
        "has_more": False,
        "applied_filters": None,
    }

    mock_service.return_value = mock_results

    validated_item = MagicMock()
    mock_inner_schema.model_validate.return_value = (
        validated_item
    )

    mock_response = MagicMock()

    mock_response.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [],
    }

    mock_outer_schema.return_value = mock_response

    event = {
        "pathParameters": {},
        "queryStringParameters": {
            "limit": "10",
        },
        "requestContext": {
            "requestId": "test-list-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = list_project_financials_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    service_call = mock_service.call_args

    assert service_call.kwargs["page"].limit == 10

    mock_outer_schema.assert_called_once()

from v1.handlers.project_financial import (
    get_project_financial_v1,
    list_project_financials_v1,
    search_project_financials_v1,
)
import json
from unittest.mock import ANY, MagicMock, patch

import pytest

from v1.handlers import project_financial
from v1.handlers.project_financial import (
    get_project_financial_v1,
    list_project_financials_v1,
    search_project_financials_v1,
)
