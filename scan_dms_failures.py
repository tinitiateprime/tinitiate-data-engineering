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
