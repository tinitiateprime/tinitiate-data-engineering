"""
Unit tests for v1.handlers.irc_census_report
"""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers.irc_census_report import (
    get_irc_census_report_v1,
    list_irc_census_reports_v1,
    search_irc_census_reports_v1,
)


ALLOWED_USER = "HR - Special Use"
LAST_FIRST_NAME = "Price, Kevin T"


def mock_context():
    return SimpleNamespace(
        aws_request_id="test-request-id"
    )


def authorized_request_context():
    return {
        "requestId": "test-request-id",
        "authorizer": {
            "lambda": {
                "userId": ALLOWED_USER
            }
        },
    }


def mock_metadata():
    metadata = MagicMock()

    metadata.cursor = None
    metadata.has_more = False
    metadata.applied_filters = None

    metadata.model_dump.return_value = {
        "cursor": None,
        "hasMore": False,
        "appliedFilters": None,
    }

    return metadata


# =============================================================================
# GET DETAIL - SUCCESS
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportDetailResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "get_irc_census_report_details"
)
def test_get_irc_census_report_v1_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
):
    results = MagicMock()

    results.items = [
        {
            "row_id": 16698,
            "my_id": "X83855",
            "last_first_name": LAST_FIRST_NAME,
        }
    ]

    results.metadata = mock_metadata()

    mock_service.return_value = results

    validated_item = MagicMock()
    mock_inner_schema.model_validate.return_value = validated_item

    outer = MagicMock()

    outer.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "rowId": 16698,
                "myId": "X83855",
                "lastFirstName": LAST_FIRST_NAME,
            }
        ],
    }

    mock_outer_schema.return_value = outer

    event = {
        "pathParameters": {
            "last_first_name": LAST_FIRST_NAME,
        },
        "queryStringParameters": None,
        "requestContext": authorized_request_context(),
    }

    response = get_irc_census_report_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()

    kwargs = mock_service.call_args.kwargs

    assert kwargs["last_first_name"] == LAST_FIRST_NAME
    assert "row_id" not in kwargs

    mock_inner_schema.model_validate.assert_called_once_with(
        results.items[0]
    )


# =============================================================================
# GET DETAIL - MISSING LAST_FIRST_NAME
# =============================================================================

def test_get_irc_census_report_v1_missing_id():
    event = {
        "pathParameters": {},
        "queryStringParameters": None,
        "requestContext": authorized_request_context(),
    }

    response = get_irc_census_report_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 400

    body = (
        response["body"]
        if isinstance(response["body"], dict)
        else json.loads(response["body"])
    )

    assert (
        body["error"]["message"]
        == "last_first_name is required."
    )


# =============================================================================
# GET DETAIL - NOT FOUND
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "get_irc_census_report_details"
)
def test_get_irc_census_report_v1_not_found(
    mock_service,
):
    results = MagicMock()
    results.items = []
    results.metadata = mock_metadata()

    mock_service.return_value = results

    event = {
        "pathParameters": {
            "last_first_name": "Does Not Exist",
        },
        "queryStringParameters": None,
        "requestContext": authorized_request_context(),
    }

    response = get_irc_census_report_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 404

    mock_service.assert_called_once()

    kwargs = mock_service.call_args.kwargs

    assert (
        kwargs["last_first_name"]
        == "Does Not Exist"
    )


# =============================================================================
# LIST - SUCCESS
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportListResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "search_irc_census_reports"
)
def test_list_irc_census_reports_v1_success(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
):
    results = MagicMock()

    results.items = [
        {
            "row_id": 16698,
            "last_first_name": LAST_FIRST_NAME,
        }
    ]

    results.metadata = mock_metadata()

    mock_service.return_value = results

    mock_inner_schema.model_validate.return_value = MagicMock()

    outer = MagicMock()

    outer.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "rowId": 16698,
                "lastFirstName": LAST_FIRST_NAME,
            }
        ],
    }

    mock_outer_schema.return_value = outer

    event = {
        "queryStringParameters": {
            "limit": "10",
        },
        "requestContext": authorized_request_context(),
    }

    response = list_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once()


# =============================================================================
# LIST - DEFAULT QUERY PARAMETERS
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportListResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "search_irc_census_reports"
)
def test_list_irc_census_reports_v1_default_query_params(
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
):
    results = MagicMock()
    results.items = []
    results.metadata = mock_metadata()

    mock_service.return_value = results

    outer = MagicMock()

    outer.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [],
    }

    mock_outer_schema.return_value = outer

    event = {
        "queryStringParameters": None,
        "requestContext": authorized_request_context(),
    }

    response = list_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 200
    mock_service.assert_called_once()


# =============================================================================
# SEARCH - SUCCESS
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportListResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "search_irc_census_reports"
)
@patch(
    "v1.handlers.irc_census_report."
    "LambdaUtils.get_json_body"
)
def test_search_irc_census_reports_v1_success(
    mock_json_body,
    mock_service,
    mock_outer_schema,
    mock_inner_schema,
):
    mock_json_body.return_value = {
        "filters": {},
        "sort": {},
        "page": {
            "limit": 10
        },
    }

    results = MagicMock()

    results.items = [
        {
            "row_id": 16698,
            "last_first_name": LAST_FIRST_NAME,
        }
    ]

    results.metadata = mock_metadata()

    mock_service.return_value = results

    mock_inner_schema.model_validate.return_value = MagicMock()

    outer = MagicMock()

    outer.model_dump.return_value = {
        "metadata": {
            "cursor": None,
            "hasMore": False,
        },
        "data": [
            {
                "rowId": 16698,
                "lastFirstName": LAST_FIRST_NAME,
            }
        ],
    }

    mock_outer_schema.return_value = outer

    event = {
        "requestContext": authorized_request_context(),
        "body": "{}",
        "isBase64Encoded": False,
    }

    response = search_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 200
    mock_service.assert_called_once()


# =============================================================================
# SEARCH - INVALID JSON
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "LambdaUtils.get_json_body"
)
def test_search_irc_census_reports_v1_invalid_json(
    mock_get_json_body,
):
    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Expecting value",
        "",
        0,
    )

    event = {
        "requestContext": authorized_request_context(),
        "body": "{invalid-json",
        "isBase64Encoded": False,
    }

    response = search_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 400


# =============================================================================
# AUTHORIZATION
# =============================================================================

def test_get_irc_census_report_v1_forbidden():
    event = {
        "pathParameters": {
            "last_first_name": LAST_FIRST_NAME,
        },
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-forbidden",
            "authorizer": {
                "lambda": {
                    "userId": "someone-else"
                }
            },
        },
    }

    response = get_irc_census_report_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 403


def test_list_irc_census_reports_v1_forbidden():
    event = {
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-list-forbidden",
            "authorizer": {
                "lambda": {
                    "userId": "someone-else"
                }
            },
        },
    }

    response = list_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 403


# =============================================================================
# AUTHORIZATION FALLBACK
# =============================================================================

@patch(
    "v1.handlers.irc_census_report."
    "V1IrcCensusReportListResponseModel"
)
@patch(
    "v1.handlers.irc_census_report."
    "search_irc_census_reports"
)
def test_list_irc_census_reports_authorizer_direct_userid(
    mock_service,
    mock_outer_schema,
):
    """
    Covers the fallback where userId is directly under authorizer,
    rather than authorizer.lambda.
    """

    results = MagicMock()
    results.items = []
    results.metadata = mock_metadata()

    mock_service.return_value = results

    outer = MagicMock()

    outer.model_dump.return_value = {
        "metadata": {},
        "data": [],
    }

    mock_outer_schema.return_value = outer

    event = {
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "direct-userid",
            "authorizer": {
                "userId": ALLOWED_USER,
            },
        },
    }

    response = list_irc_census_reports_v1(
        event,
        mock_context(),
    )

    assert response["statusCode"] == 200
