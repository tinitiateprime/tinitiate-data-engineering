# domain/services/__init__.py

from .agent_service import agent_get_contract_locations
from .contract_service import get_contract_details, search_contracts
from .employee_profile_service import (
    get_all_employees,
    get_direct_reports,
    get_employee_by_id,
    get_employees_by_clearance,
    get_employees_in_org,
    get_personnel_roster,
)
from .employee_training_service import (
    get_all_training,
    get_training_by_employee,
    get_training_by_org,
    get_training_by_status,
    get_training_by_type,
)
from .health_service import HealthService
from .project_status_service import get_project_status_details
from .project_forecasts_service import get_project_forecasts

# Add this block
from .project_financial_service import (
    get_project_financial_details,
    search_project_financials,
)


__all__ = [
    "search_contracts",
    "get_contract_details",
    "HealthService",
    "get_project_status_details",
    "get_all_employees",
    "get_employee_by_id",
    "get_direct_reports",
    "get_employees_in_org",
    "get_employees_by_clearance",
    "get_all_training",
    "get_training_by_employee",
    "get_training_by_status",
    "get_training_by_org",
    "get_training_by_type",
    "agent_get_contract_locations",
    "get_personnel_roster",
    "get_project_forecasts",

    # Add these two entries
    "get_project_financial_details",
    "search_project_financials",
]
