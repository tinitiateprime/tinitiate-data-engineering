from v1.handlers.po_funding_detail import (
    get_po_funding_detail_v1,
    search_po_funding_detail_v1,
)


# ============================================================
# GET PO FUNDING DETAIL - MISSING PROJECT ID
# ============================================================
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_path_param"
)
def test_get_po_funding_detail_v1_missing_project_id(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = None

    event = {
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-missing-project-id",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_po_funding_detail_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# GET PO FUNDING DETAIL - PROJECT ID = SEARCH
# ============================================================
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_path_param"
)
def test_get_po_funding_detail_v1_search_project_id(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = "search"

    event = {
        "pathParameters": {
            "project_id": "search",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-search-project-id",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_po_funding_detail_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# GET PO FUNDING DETAIL - NOT FOUND
# ============================================================
@patch(
    "v1.handlers.po_funding_detail."
    "get_po_funding_detail_by_project"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_path_param"
)
def test_get_po_funding_detail_v1_not_found(
    mock_get_path_param,
    mock_get_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "P-1001"
    mock_get_query_params.return_value = {}
    mock_get_columns.return_value = None

    mock_results = MagicMock()
    mock_results.items = []

    mock_service.return_value = mock_results

    event = {
        "pathParameters": {
            "project_id": "P-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-not-found",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_po_funding_detail_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 404

    mock_service.assert_called_once_with(
        project_id="P-1001",
        page=ANY,
        sort=ANY,
        columns=None,
    )


# ============================================================
# GET PO FUNDING DETAIL - SUCCESS
# ============================================================
@patch(
    "v1.handlers.po_funding_detail."
    "V1PoFundingDetailResponseModel"
)
@patch(
    "v1.handlers.po_funding_detail."
    "V1PoFundingDetailListResponseModel"
)
@patch(
    "v1.handlers.po_funding_detail."
    "get_po_funding_detail_by_project"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.po_funding_detail."
    "LambdaUtils.get_path_param"
)
def test_get_po_funding_detail_v1_success(
    mock_get_path_param,
    mock_get_query_params,
    mock_get_columns,
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
    mock_context,
):
    mock_get_path_param.return_value = "P-1001"

    mock_get_query_params.return_value = {
        "limit": 10,
        "cursor": None,
        "sortField": "order_date",
        "sortOrder": "desc",
    }

    mock_get_columns.return_value = None

    mock_item = MagicMock()
    mock_item.model_dump.return_value = {
        "project_id": "P-1001",
        "order_date": "2026-08-20",
    }

    mock_results = MagicMock()
    mock_results.items = [
        mock_item,
    ]

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
                "projectId": "P-1001",
            }
        ],
    }

    mock_outer_schema.return_value = mock_response

    event = {
        "pathParameters": {
            "project_id": "P-1001",
        },
        "queryStringParameters": {
            "limit": "10",
            "sortField": "order_date",
            "sortOrder": "desc",
        },
        "requestContext": {
            "requestId": "test-get-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_po_funding_detail_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once_with(
        project_id="P-1001",
        page=ANY,
        sort=ANY,
        columns=None,
    )

    service_call = mock_service.call_args

    assert service_call.kwargs[
        "page"
    ].limit == 10

    assert service_call.kwargs[
        "sort"
    ].field == "order_date"

    assert service_call.kwargs[
        "sort"
    ].order == "desc"

    mock_inner_schema.model_validate.assert_called_once_with(
        mock_item.model_dump.return_value
    )

    mock_outer_schema.assert_called_once()
