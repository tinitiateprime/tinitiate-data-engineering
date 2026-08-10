# tests/unit/domain/services/test_employee_profile_synth_service.py
from unittest.mock import patch

import pytest
from domain.services import employee_profile_synth_service as employee_profile_service
from v1.schemas import PaginationModel


class TestEmployeeProfileSynthService:
    """Test suite for synth employee profile service"""

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_get_all_employees(self, mock_repo):
        """Test getting all synth employees"""
        # Arrange
        mock_repo.get_employee_profiles.return_value = {
            "items": [{"empl_id": "12345", "first_name": "John", "last_name": "Doe"}],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_all_employees()

        # Assert
        assert len(result.items) == 1
        assert result.items[0].empl_id == "12345"
        assert result.items[0].first_name == "John"
        assert result.items[0].last_name == "Doe"
        assert result.metadata.has_more is False
        assert result.metadata.cursor is None

        mock_repo.get_employee_profiles.assert_called_once()

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    @pytest.mark.parametrize("columns", [None, ["first_name", "last_name"]])
    def test_get_employee_by_id(self, mock_repo, columns):
        """Test getting synth employee by ID"""
        # Arrange
        mock_repo.get_employee_profile_by_id.return_value = {
            "items": [{"empl_id": "12345", "first_name": "John", "last_name": "Doe"}],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_employee_by_id("12345", columns=columns)

        # Assert
        assert len(result.items) == 1
        assert result.items[0].empl_id == "12345"
        assert result.items[0].first_name == "John"
        assert result.items[0].last_name == "Doe"
        assert result.metadata.has_more is False
        assert result.metadata.cursor is None

        mock_repo.get_employee_profile_by_id.assert_called_once_with(
            empl_id="12345", columns=columns
        )

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_get_employee_by_id_not_found(self, mock_repo):
        """Test getting synth employee that doesn't exist"""
        # Arrange
        mock_repo.get_employee_profile_by_id.return_value = {
            "items": [],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_employee_by_id("99999")

        # Assert
        assert len(result.items) == 0
        mock_repo.get_employee_profile_by_id.assert_called_once_with(
            empl_id="99999", columns=None
        )

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_get_direct_reports(self, mock_repo):
        """Test getting synth direct reports for a manager"""
        # Arrange
        mock_repo.get_employees_by_manager.return_value = {
            "items": [
                {"empl_id": "11111", "mgr_empl_id": "12345"},
                {"empl_id": "22222", "mgr_empl_id": "12345"},
            ],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_direct_reports("12345")

        # Assert
        assert len(result.items) == 2
        assert result.items[0].empl_id == "11111"
        assert result.items[0].mgr_empl_id == "12345"
        assert result.items[1].empl_id == "22222"
        assert result.items[1].mgr_empl_id == "12345"

        mock_repo.get_employees_by_manager.assert_called_once()

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_get_employees_in_org(self, mock_repo):
        """Test getting synth employees in organization"""
        # Arrange
        mock_repo.get_employees_by_org.return_value = {
            "items": [
                {"empl_id": "11111", "org_id": "01.525.146.10"},
                {"empl_id": "22222", "org_id": "01.525.146.10"},
            ],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_employees_in_org("01.525.146.10")

        # Assert
        assert len(result.items) == 2

        # Check that the repo was called (don't check exact parameters since service sets defaults)
        mock_repo.get_employees_by_org.assert_called_once()

        # Verify the call had the correct org_id
        call_args = mock_repo.get_employees_by_org.call_args
        assert call_args.kwargs["org_id"] == "01.525.146.10"

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_get_employees_by_clearance(self, mock_repo):
        """Test getting synth employees by clearance status"""
        # Arrange
        mock_repo.get_employees_by_clearance.return_value = {
            "items": [{"empl_id": "11111", "clearance_status": "Active"}],
            "page": {"cursor": None, "has_more": False},
        }

        # Act
        result = employee_profile_service.get_employees_by_clearance("Active")

        # Assert
        assert len(result.items) == 1
        assert result.items[0].clearance_status == "Active"

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_service_with_filters(self, mock_repo):
        """Test synth service with simple filters"""
        # Arrange
        mock_repo.get_employee_profiles.return_value = {
            "items": [
                {
                    "empl_id": "12345",
                    "dept_name": "Engineering",
                    "org_id": "01.525.146.10",
                }
            ],
            "page": {"cursor": None, "has_more": False},
        }

        filters = {"dept_name": {"eq": "Engineering"}}

        # Act
        result = employee_profile_service.get_all_employees(filters=filters)

        # Assert
        assert len(result.items) == 1
        assert result.items[0].empl_id == "12345"

        mock_repo.get_employee_profiles.assert_called_once()

    @patch("domain.services.employee_profile_synth_service.employee_profile_repo")
    def test_service_with_pagination(self, mock_repo):
        """Test synth service with pagination metadata and global items count"""
        page_limitation_count = 10
        total_desired_items = 101

        # Arrange: Mock exactly what the repository layer returns when
        # hitting a database that holds 101 records total.
        mock_repo.get_employee_profiles.return_value = {
            # The DB only pulls the requested page limit (10 items)
            "items": [{"empl_id": f"{i:05d}"} for i in range(page_limitation_count)],
            # The DB calculates the overall matching dataset size (101 items)
            "total_count": total_desired_items,
            "page": {"cursor": "abc123", "has_more": True},
        }

        # Act
        result = employee_profile_service.get_all_employees(
            page=PaginationModel(limit=page_limitation_count)
        )

        # Assert
        # Verify this specific response payload only holds the sliced page
        assert len(result.items) == page_limitation_count

        # Verify cursor state
        assert result.metadata.has_more is True
        assert result.metadata.cursor == "abc123"
