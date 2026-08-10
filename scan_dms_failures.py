# tests/unit/db/test_employee_profile_synth_repo.py
from unittest.mock import Mock, patch

import pytest
from db.repositories import employee_profile_synth_repo
from v1.schemas import FilterOps, FiltersEnvelope, PaginationModel, SortModel


class TestEmployeeProfileSynthRepo:
    """Test suite for synth employee profile repository"""

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employee_profiles_basic(self, mock_execute):
        """Test basic synth employee profile search"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {
                    "EMPL_ID": "12345",
                    "FIRST_NAME": "John",
                    "LAST_NAME": "Doe",
                    "DEPT_NAME": "Engineering",
                    "ORG_ID": "MT-CTO",
                }
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employee_profiles(
            filters=FiltersEnvelope(filters={}), page=PaginationModel(limit=10)
        )

        # Assert
        assert len(result["items"]) == 1
        assert result["items"][0]["EMPL_ID"] == "12345"
        assert result["items"][0]["FIRST_NAME"] == "John"
        mock_execute.assert_called_once()

        # Confirm this repo always routes to the synth database
        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employee_profiles_with_dept_filter(self, mock_execute):
        """Test synth employee search with department filter"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {"employeeId": "12345", "departmentName": "Engineering"},
                {"employeeId": "67890", "departmentName": "Engineering"},
            ]
        }

        filters = FiltersEnvelope(
            filters={"departmentName": FilterOps(eq="Engineering")}
        )

        # Act
        result = employee_profile_synth_repo.get_employee_profiles(
            filters=filters, page=PaginationModel(limit=10)
        )

        # Assert
        assert len(result["items"]) == 2
        assert all(
            item["departmentName"] == "Engineering" for item in result["items"]
        )

        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employee_by_id(self, mock_execute):
        """Test getting single synth employee by ID"""
        # Arrange
        mock_execute.return_value = {
            "items": [{"EMPL_ID": "12345", "FIRST_NAME": "John", "LAST_NAME": "Doe"}]
        }

        # Act
        result = employee_profile_synth_repo.get_employee_profile_by_id("12345")

        # Assert
        assert len(result["items"]) == 1
        assert result["items"][0]["EMPL_ID"] == "12345"

        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employee_by_id_not_found(self, mock_execute):
        """Test getting synth employee that doesn't exist"""
        # Arrange
        mock_execute.return_value = {"items": []}

        # Act
        result = employee_profile_synth_repo.get_employee_profile_by_id("99999")

        # Assert
        assert len(result["items"]) == 0
        assert result["page"]["has_more"] is False

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employees_by_manager(self, mock_execute):
        """Test getting direct reports for a manager in synth"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {"EMPL_ID": "11111", "MGR_EMPL_ID": "12345"},
                {"EMPL_ID": "22222", "MGR_EMPL_ID": "12345"},
                {"EMPL_ID": "33333", "MGR_EMPL_ID": "12345"},
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employees_by_manager("12345")

        # Assert
        assert len(result["items"]) == 3
        assert all(item["MGR_EMPL_ID"] == "12345" for item in result["items"])

        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employees_by_org(self, mock_execute):
        """Test getting synth employees by organization"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {"EMPL_ID": "11111", "ORG_ID": "MT-CTO"},
                {"EMPL_ID": "22222", "ORG_ID": "MT-CTO"},
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employees_by_org("MT-CTO")

        # Assert
        assert len(result["items"]) == 2
        assert all(item["ORG_ID"] == "MT-CTO" for item in result["items"])

        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_get_employees_by_clearance(self, mock_execute):
        """Test getting synth employees by clearance status"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {"EMPL_ID": "11111", "clearance_status": "Active"},
                {"EMPL_ID": "22222", "clearance_status": "Active"},
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employees_by_clearance("Active")

        # Assert
        assert len(result["items"]) == 2
        assert all(
            item["clearance_status"] == "Active" for item in result["items"]
        )

        _, call_kwargs = mock_execute.call_args
        assert call_kwargs.get("db_key") == "synth"

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_pagination_has_more(self, mock_execute):
        """Test pagination with has_more flag on synth data"""
        # Arrange - Return limit+1 items to trigger has_more
        mock_execute.return_value = {
            "items": [
                {"EMPL_ID": f"{i:05d}"} for i in range(11)  # 11 items for limit=10
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employee_profiles(
            page=PaginationModel(limit=10)
        )

        # Assert
        assert len(result["items"]) == 10  # Should trim to limit
        assert result["page"]["has_more"] is True
        assert result["page"]["cursor"] is not None

    @patch("db.repositories.employee_profile_synth_repo.execute_query")
    def test_sorting(self, mock_execute):
        """Test sorting by last name on synth data"""
        # Arrange
        mock_execute.return_value = {
            "items": [
                {"EMPL_ID": "1", "LAST_NAME": "Adams"},
                {"EMPL_ID": "2", "LAST_NAME": "Baker"},
                {"EMPL_ID": "3", "LAST_NAME": "Carter"},
            ]
        }

        # Act
        result = employee_profile_synth_repo.get_employee_profiles(
            sort=SortModel(field="LAST_NAME", order="asc"),
            page=PaginationModel(limit=10),
        )

        # Assert
        assert result["items"][0]["LAST_NAME"] == "Adams"
        assert result["items"][2]["LAST_NAME"] == "Carter"
