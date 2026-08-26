import json
from unittest.mock import MagicMock, patch

import pytest

from v1.handlers import agent
from v1.schemas import FilterOps, FiltersEnvelope


# =============================================================================
# Test data
# =============================================================================


AGENT_ITEM = {
    "contract_id": "CONT-1001",
    "award_number": "AWD-1001",
    "order_number": "ORD-1001",
    "mod_number": "MOD-01",
    "places": "Dallas, TX",
    "project_name": "Test Project",
    "program_manager_name": "Test Manager",
    "status": "ACTIVE",
}


# =============================================================================
# Test helpers
# =============================================================================


class MockMetadata:
    """
    Lightweight metadata object used by the mocked service response.
    """

    def __init__(
        self,
        cursor=None,
        has_more=False,
        applied_filters=None,
    ):
        self.cursor = cursor
        self.has_more = has_more
        self.applied_filters = applied_filters

    def model_dump(self):
        return {
            "cursor": self.cursor,
            "has_more": self.has_more,
            "applied_filters": self.applied_filters,
        }


class MockServiceResponse:
    """
    Lightweight replacement for the response returned by
    agent_get_contract_locations().
    """

    def __init__(
        self,
        items=None,
        cursor=None,
        has_more=False,
        applied_filters=None,
    ):
        self.items = items if items is not None else []

        self.metadata = MockMetadata(
            cursor=cursor,
            has_more=has_more,
            applied_filters=applied_filters,
        )


def build_event(
    contract_id="CONT-1001",
    query_params=None,
):
    """
    Build an API Gateway event for the Agent contract-location endpoint.
    """

    path_parameters = {}

    if contract_id is not None:
        path_parameters["contractId"] = contract_id

    return {
        "httpMethod": "GET",
        "path": (
            f"/v1/agent/work_locations_vw/{contract_id}"
            if contract_id
            else "/v1/agent/work_locations_vw/"
        ),
        "resource": "/v1/agent/work_locations_vw/{contractId}",
        "headers": {
            "Content-Type": "application/json",
        },
        "queryStringParameters": query_params,
        "pathParameters": path_parameters,
        "requestContext": {
            "requestId": "unit-test-request-id",
            "stage": "test",
            "httpMethod": "GET",
            "resourcePath": (
                "/v1/agent/work_locations_vw/{contractId}"
            ),
        },
        "body": None,
        "isBase64Encoded": False,
    }


def get_response_body(response):
    """
    Safely deserialize Lambda response body.
    """

    body = response.get("body")

    if isinstance(body, str):
        return json.loads(body)

    return body


def build_filters():
    """
    Return a real FiltersEnvelope.

    V1MetadataModel requires applied_filters to be an actual
    FiltersEnvelope or valid dictionary. Using MagicMock here causes
    Pydantic validation failures.
    """

    return FiltersEnvelope(
        filters={
            "status": FilterOps(
                eq="ACTIVE",
            )
        }
    )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_context():
    """
    Create a mock AWS Lambda context.
    """

    context = MagicMock()

    context.function_name = "agent-unit-test"
    context.aws_request_id = "unit-test-request-id"
    context.memory_limit_in_mb = 128
    context.get_remaining_time_in_millis.return_value = 30000

    return context


# =============================================================================
# Successful request
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_success(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "10",
        "cursor": "next-token",
    }

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = None

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
        cursor="next-token",
        has_more=True,
    )

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "10",
            "cursor": "next-token",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)
    assert response["statusCode"] == 200
    assert "body" in response

    body = get_response_body(response)

    assert body is not None

    mock_service.assert_called_once_with(
        contract_id="CONT-1001",
        filters=None,
        limit=10,
        cursor="next-token",
        columns=None,
    )


# =============================================================================
# Default limit
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_default_limit(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "CONT-1001"
    mock_get_all_query_params.return_value = {}

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = None

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
    )

    event = build_event(
        contract_id="CONT-1001",
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    kwargs = mock_service.call_args.kwargs

    assert kwargs["contract_id"] == "CONT-1001"
    assert kwargs["limit"] == agent.settings.DEFAULT_PAGE_SIZE
    assert kwargs["cursor"] is None
    assert kwargs["columns"] is None


# =============================================================================
# Custom columns
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_custom_columns(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    columns = [
        "contract_id",
        "project_name",
        "status",
    ]

    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "10",
    }

    mock_get_columns.return_value = columns
    mock_parse_filters.return_value = None

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
    )

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "10",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    kwargs = mock_service.call_args.kwargs

    assert kwargs["columns"] == columns


# =============================================================================
# Filters
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_filters(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    """
    Verify a real FiltersEnvelope is sent to the service.
    """

    filters_envelope = build_filters()

    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "10",
        "status": "ACTIVE",
    }

    mock_get_columns.return_value = None

    mock_parse_filters.return_value = filters_envelope

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
    )

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "10",
            "status": "ACTIVE",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_parse_filters.assert_called_once()

    kwargs = mock_service.call_args.kwargs

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    assert kwargs["filters"] == filters_envelope

    assert (
        kwargs["filters"]
        .filters["status"]
        .eq
        == "ACTIVE"
    )


# =============================================================================
# Applied filters metadata
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_sets_applied_filters(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    """
    Verify parsed FiltersEnvelope is copied into metadata.
    """

    filters_envelope = build_filters()

    mock_get_path_param.return_value = "CONT-1001"
    mock_get_all_query_params.return_value = {}

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = filters_envelope

    service_response = MockServiceResponse(
        items=[AGENT_ITEM],
    )

    mock_service.return_value = service_response

    event = build_event(
        contract_id="CONT-1001",
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    assert isinstance(
        service_response.metadata.applied_filters,
        FiltersEnvelope,
    )

    assert (
        service_response.metadata.applied_filters
        == filters_envelope
    )


# =============================================================================
# Not found
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_not_found(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "CONT-9999"
    mock_get_all_query_params.return_value = {}

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = None

    mock_service.return_value = MockServiceResponse(
        items=[],
        cursor=None,
        has_more=False,
    )

    event = build_event(
        contract_id="CONT-9999",
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)

    assert response["statusCode"] in (
        404,
        400,
    )

    assert "body" in response


# =============================================================================
# Missing contract ID
# =============================================================================


@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
def test_get_agent_contract_locations_v1_missing_contract_id(
    mock_get_path_param,
    mock_context,
):
    mock_get_path_param.return_value = None

    event = build_event(
        contract_id=None,
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)
    assert response["statusCode"] == 400

    body = get_response_body(response)

    assert body is not None

    body_text = json.dumps(body)

    assert "Contract ID is required" in body_text


# =============================================================================
# Invalid limit
# =============================================================================


@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
def test_get_agent_contract_locations_v1_invalid_limit(
    mock_get_path_param,
    mock_get_all_query_params,
    mock_context,
):
    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "NOT-A-NUMBER",
    }

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "NOT-A-NUMBER",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response is not None
    assert isinstance(response, dict)

    assert response["statusCode"] == 400


# =============================================================================
# Cursor handling
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_cursor(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "25",
        "cursor": "cursor-token-123",
    }

    mock_get_columns.return_value = None
    mock_parse_filters.return_value = None

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
        cursor="next-cursor",
        has_more=True,
    )

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "25",
            "cursor": "cursor-token-123",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    kwargs = mock_service.call_args.kwargs

    assert kwargs["cursor"] == "cursor-token-123"
    assert kwargs["limit"] == 25


# =============================================================================
# Service argument verification
# =============================================================================


@patch.object(
    agent,
    "agent_get_contract_locations",
)
@patch.object(
    agent.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    agent.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    agent.LambdaUtils,
    "get_path_param",
)
@patch.object(
    agent,
    "parse_filters_from_query_params",
)
def test_get_agent_contract_locations_v1_service_arguments(
    mock_parse_filters,
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_context,
):
    """
    Verify every handler argument reaches the service correctly.
    """

    # IMPORTANT:
    # Must be a real FiltersEnvelope, not MagicMock.
    filters = build_filters()

    columns = [
        "contract_id",
        "award_number",
        "project_name",
    ]

    mock_get_path_param.return_value = "CONT-1001"

    mock_get_all_query_params.return_value = {
        "limit": "15",
        "cursor": "abc123",
    }

    mock_get_columns.return_value = columns
    mock_parse_filters.return_value = filters

    mock_service.return_value = MockServiceResponse(
        items=[AGENT_ITEM],
    )

    event = build_event(
        contract_id="CONT-1001",
        query_params={
            "limit": "15",
            "cursor": "abc123",
        },
    )

    response = agent.get_agent_contract_locations_v1(
        event,
        mock_context,
    )

    assert response["statusCode"] == 200

    mock_service.assert_called_once_with(
        contract_id="CONT-1001",
        filters=filters,
        limit=15,
        cursor="abc123",
        columns=columns,
    )
