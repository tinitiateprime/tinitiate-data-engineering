def test_get_project_info_v1_search_project_id(mock_context):
    event = {
        "pathParameters": {
            "proj_id": "search",
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-search-as-project-id",
        },
    }

    response = get_project_info_v1(event, mock_context)

    assert response["statusCode"] == 400
