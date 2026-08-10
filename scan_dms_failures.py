# tests/test_handlers_employee_synth.py
import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from domain.models.metadata import MetadataModel
from v1.handlers import (
    employees_synth as handlers,  # points at the synth handler module
)
from v1.schemas import FiltersEnvelope


def create_mock_service_response(items, cursor=None, has_more=False):
    """Helper to create a properly structured service response mock"""

    # Services now return the generic MetadataModel
    metadata = MetadataModel(
        cursor=cursor,
        has_more=has_more,
        applied_filters=FiltersEnvelope(filters={}),
    )

    # Mock items with model_dump capability
    mock_items = []
    for item in items:
        m = MagicMock()
        m.model_dump.return_value = item
        mock_items.append(m)

    class MockServiceResponse:
        def __init__(self, items, metadata):
            self.items = items
            self.metadata = metadata

    return MockServiceResponse(items=mock_items, metadata=metadata)


@pytest.fixture
def mock_user_record():
    """Provides a single mocked user data record with split names to match assertions."""
    return {
        "EMPL_ID": "111111",
        "MY_ID": "123456",
        "FIRST_NAME": "John",
        "LAST_NAME": "Doe",
        "DEPT_NAME": "Engineering",
        "MGR_EMPL_ID": "00001",
        "ORG_ID": "01.626.N32.10",
        "clearanceStatus": "Active",
    }


@pytest.fixture
def mock_user_list():
    """Provides a list of 5 distinct user records with manager IDs assigned."""
    return [
        {
            "EMPL_ID": "111111",
            "MY_ID": "123456",
            "FIRST_NAME": "John",
            "LAST_NAME": "Doe",
            "DEPT_NAME": "Engineering",
            "MGR_EMPL_ID": "111111",  # Self-managed or reports to upper management
            "ORG_ID": "ORG001",
        },
        {
            "EMPL_ID": "222222",
            "MY_ID": "234567",
            "FIRST_NAME": "Jane",
            "LAST_NAME": "Smith",
            "DEPT_NAME": "Engineering",
            "MGR_EMPL_ID": "11111",
            "ORG_ID": "ORG001",
        },
        {
            "EMPL_ID": "333333",
            "MY_ID": "345678",
            "FIRST_NAME": "Bob",
            "LAST_NAME": "Jones",
            "DEPT_NAME": "HR",
            "MGR_EMPL_ID": "11111",
            "ORG_ID": "ORG002",
        },
        {
            "EMPL_ID": "444444",
            "MY_ID": "456789",
            "FIRST_NAME": "Maria",
            "LAST_NAME": "Garcia",
            "DEPT_NAME": "Engineering",
            "MGR_EMPL_ID": "11111",
            "ORG_ID": "ORG003",
        },
        {
            "EMPL_ID": "555555",
            "MY_ID": "567890",
            "FIRST_NAME": "Alex",
            "LAST_NAME": "Miller",
            "DEPT_NAME": "Marketing",
            "MGR_EMPL_ID": "11111",
            "ORG_ID": "ORG002",
        },
    ]


class TestEmployeeProfileSynthHandlers:
    """Test suite for synth employee profile handlers"""

    @patch("v1.handlers.employees_synth.get_all_employees")
    def test_search_employee_profiles_synth_success(
        self, mock_service, create_mock_event, mock_context, mock_user_record
    ):
        """Test successful synth employee profile search"""
        # Arrange
        request_id = "test-search-synth-123"
        mock_service.return_value = create_mock_service_response(
            items=[mock_user_record],
            cursor=None,
            has_more=False,
        )

        event = create_mock_event(
            route="/v1/employees/synth/profiles/search",
            method="POST",
            body={
                "filters": {"DEPT_NAME": {"eq": mock_user_record["DEPT_NAME"]}},
            },
            request_id=request_id,
        )
        context = mock_context(request_id)

        # Act
        response = handlers.search_employee_profiles_synth_v1(event, context)
        body = json.loads(response["body"])

        # Assert
        assert response["statusCode"] == 200
        assert len(body["data"]) == 1
        assert body["data"][0]["employeeId"] == mock_user_record["EMPL_ID"]
        assert body["data"][0]["firstName"] == mock_user_record["FIRST_NAME"]
        assert body["data"][0]["lastName"] == mock_user_record["LAST_NAME"]

    @patch("v1.handlers.employees_synth.get_employee_by_id")
    def test_get_employee_profile_synth_by_id_success(
        self, mock_service, mock_user_record
    ):
        """Test getting synth employee by ID"""
        # Arrange
        items = [mock_user_record]
        mock_service.return_value = create_mock_service_response(items)

        event = {
            "pathParameters": {"empl_id": mock_user_record["EMPL_ID"]},
            "queryStringParameters": {},
        }

        # Act
        response = handlers.get_employee_profile_synth_v1(event, Mock())
        body = json.loads(response["body"])

        # Assert
        assert response["statusCode"] == 200
        assert len(body["data"]) == 1
        assert body["data"][0]["employeeId"] == mock_user_record["EMPL_ID"]
        assert body["metadata"]["responseVersion"] == "v1"

    @patch("v1.handlers.employees_synth.get_employee_by_id")
    def test_get_employee_profile_synth_not_found(self, mock_service):
        """Test getting synth employee that doesn't exist"""
        # Arrange
        mock_service.return_value = create_mock_service_response([])

        event = {"pathParameters": {"empl_id": "999999"}, "queryStringParameters": {}}
        context = Mock()

        # Act
        response = handlers.get_employee_profile_synth_v1(event, context)

        # Assert - Should return 404
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert "Employee with ID 999999 not found" in body["error"]["message"]

    @patch("v1.handlers.employees_synth.get_direct_reports")
    def test_get_direct_reports_synth_success(self, mock_service, mock_user_list):
        """Test getting synth direct reports for a manager"""
        # Arrange
        items = mock_user_list
        mock_service.return_value = create_mock_service_response(items)

        event = {
            "pathParameters": {"mgr_empl_id": mock_user_list[0]["MGR_EMPL_ID"]},
            "queryStringParameters": {},
        }

        # Act
        response = handlers.get_employee_direct_reports_synth_v1(event, Mock())
        body = json.loads(response["body"])

        # Assert
        assert response["statusCode"] == 200
        assert len(body["data"]) == len(mock_user_list)
        assert body["metadata"]["responseVersion"] == "v1"

    @patch("v1.handlers.employees_synth.get_employees_in_org")
    def test_get_employees_by_org_synth_success(self, mock_service, mock_user_record):
        """Test getting synth employees by organization"""
        # Arrange
        items = [mock_user_record]
        mock_service.return_value = create_mock_service_response(items)

        event = {
            "pathParameters": {"org_id": mock_user_record["ORG_ID"]},
            "queryStringParameters": {},
        }

        # Act
        response = handlers.get_employees_by_org_synth_v1(event, Mock())
        body = json.loads(response["body"])

        # Assert
        assert response["statusCode"] == 200
        assert body["data"][0]["orgId"] == mock_user_record["ORG_ID"]
        assert body["metadata"]["responseVersion"] == "v1"

    @patch("v1.handlers.employees_synth.get_employees_by_clearance")
    def test_get_employees_by_clearance_synth_success(
        self, mock_service, mock_user_record
    ):
        """Test getting synth employees by clearance status"""
        # Arrange
        items = [mock_user_record]
        mock_service.return_value = create_mock_service_response(items)

        event = {
            "pathParameters": {"status": mock_user_record["clearanceStatus"]},
            "queryStringParameters": {},
        }
        context = Mock()

        # Act
        response = handlers.get_employees_by_clearance_synth_v1(event, context)
        body = json.loads(response["body"])

        # Assert
        assert response["statusCode"] == 200
        assert (
            body["data"][0]["clearanceStatus"] == mock_user_record["clearanceStatus"]
        )
        assert body["metadata"]["responseVersion"] == "v1"
