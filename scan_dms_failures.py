from v1.handlers.gl_details import (
    get_gl_details_v1,
    search_gl_details_v1,
)



# ============================================================
# GET GL DETAILS - MISSING PROJECT ID
# ============================================================
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_path_param"
)
def test_get_gl_details_v1_missing_project_id(
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

    response = get_gl_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# GET GL DETAILS - PROJECT ID = SEARCH
# ============================================================
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_path_param"
)
def test_get_gl_details_v1_search_project_id(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = "search"

    event = {
        "pathParameters": {
            "proj_id": "search",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-search-proj-id",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_gl_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 400


# ============================================================
# GET GL DETAILS - NOT FOUND
# ============================================================
@patch(
    "v1.handlers.gl_details."
    "get_gl_details_by_project"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_path_param"
)
def test_get_gl_details_v1_not_found(
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
            "proj_id": "P-1001",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-not-found",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_gl_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 404

    mock_service.assert_called_once_with(
        proj_id="P-1001",
        page=ANY,
        sort=ANY,
        columns=None,
    )


# ============================================================
# GET GL DETAILS - SUCCESS
# ============================================================
@patch(
    "v1.handlers.gl_details."
    "V1GlDetailsResponseModel"
)
@patch(
    "v1.handlers.gl_details."
    "V1GlDetailsListResponseModel"
)
@patch(
    "v1.handlers.gl_details."
    "get_gl_details_by_project"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_columns_query_parameter"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_all_query_params"
)
@patch(
    "v1.handlers.gl_details."
    "LambdaUtils.get_path_param"
)
def test_get_gl_details_v1_success(
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
        "sortField": "time_stamp",
        "sortOrder": "desc",
    }

    mock_get_columns.return_value = None

    mock_item = MagicMock()
    mock_item.model_dump.return_value = {
        "proj_id": "P-1001",
    }

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
            "sortField": "time_stamp",
            "sortOrder": "desc",
        },
        "requestContext": {
            "requestId": "test-get-success",
        },
        "body": None,
        "isBase64Encoded": False,
    }

    response = get_gl_details_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once_with(
        proj_id="P-1001",
        page=ANY,
        sort=ANY,
        columns=None,
    )

    service_call = mock_service.call_args

    assert service_call.kwargs["page"].limit == 10

    assert (
        service_call.kwargs["sort"].field
        == "time_stamp"
    )

    assert (
        service_call.kwargs["sort"].order
        == "desc"
    )

    mock_inner_schema.model_validate.assert_called_once_with(
        mock_item.model_dump.return_value
    )

    mock_outer_schema.assert_called_once()



py -m pytest tests\unit\v1\test_gl_details.py -v --cov=v1.handlers.gl_details --cov-report=term-missing
