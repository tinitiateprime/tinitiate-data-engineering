"""
API Route Handlers for v1.

Organized by functional domain.
Importing these modules ensures they register their routes with the central router.
"""

from .agent import get_agent_contract_locations_v1

from .auth import (
    get_okta_login_url_v1,
    handle_okta_login_callback_v1,
    logout_handler_v1,
)

from .contract_master import (
    get_contract_master_v1,
    list_contract_master_v1,
    search_contract_master_v1,
)

from .contract_program_manager import (
    get_contract_program_managers_v1,
    search_contract_program_managers_v1,
)

from .contract_analysis import (
    get_contract_analysis_v1,
    search_contract_analysis_v1,
)

from .clm_tcv import (
    get_clm_contract_v1,
    list_clm_contracts_v1,
    search_clm_contracts_v1,
)

from .employee_profile_complete import (
    get_employee_profile_complete_v1,
    list_employee_profile_completes_v1,
    search_employee_profile_completes_v1,
)

from .contracts import (
    get_contract_v1,
    list_contracts_v1,
    search_contracts_v1,
)

from .employees import (
    get_certifications_by_org_blank_v1,
    get_certifications_by_org_v1,
    get_certifications_by_status_blank_v1,
    get_certifications_by_status_v1,
    get_employee_certifications_blank_v1,
    get_employee_certifications_v1,
    get_employee_direct_reports_blank_v1,
    get_employee_direct_reports_v1,
    get_employee_profile_blank_v1,
    get_employee_profile_v1,
    get_employee_training_blank_v1,
    get_employee_training_v1,
    get_employees_by_clearance_blank_v1,
    get_employees_by_clearance_v1,
    get_employees_by_org_v1,
    get_org_blank_v1,
    get_personnel_roster_v1,
    get_training_by_org_blank_v1,
    get_training_by_org_v1,
    get_training_by_status_blank_v1,
    get_training_by_status_v1,
    get_training_by_type_blank_v1,
    get_training_by_type_v1,
    search_employee_certifications_v1,
    search_employee_profiles_v1,
    search_employee_training_v1,
)

from .project_financial import (
    get_project_financial_v1,
    list_project_financials_v1,
    search_project_financials_v1,
)

from .contract_modifications import (
    get_contract_modifications_v1,
    search_contract_modifications_v1,
)

from .health import handle as handle_health
from .health import handle_deep_health

from .projects import get_project_status_v1

from .project_forecasts import search_project_forecasts_v1

from .project_master import (
    get_project_master_v1,
    list_project_master_v1,
    search_project_master_v1,
)

from .ar_history import (
    get_ar_history_v1,
    search_ar_history_v1,
)

from .unburdened_nonlabor import (
    get_unburdened_nonlabor_v1,
    search_unburdened_nonlabor_v1,
)

from .timesheet_history import (
    get_timesheet_history_by_employee_v1,
    get_timesheet_history_by_project_v1,
    search_timesheet_history_v1,
)

from .voucher_history import (
    get_voucher_history_v1,
    search_voucher_history_v1,
)

from .po_funding_detail import (
    get_po_funding_detail_v1,
    search_po_funding_detail_v1,
)

from .real_time_commitment import (
    get_real_time_commitments_v1,
    search_real_time_commitments_v1,
)

from .gl_details import (
    get_gl_details_v1,
    search_gl_details_v1,
)

from .non_labor_detail import (
    get_non_labor_detail_v1,
    search_non_labor_detail_v1,
)

from .financials_updated import (
    get_financials_updated_v1,
    search_financials_updated_v1,
)

from .po_open_commitment import (
    get_po_open_commitments_v1,
    search_po_open_commitments_v1,
)

from .period_target_cost_revenue import (
    get_period_target_cost_revenue_v1,
    search_period_target_cost_revenue_v1,
)

from .project_status_report import (
    get_project_status_history_v1,
    search_project_status_history_v1,
)

from .project_modifications import (
    get_project_modifications_v1,
    search_project_modifications_v1,
)

from .project_info import (
    get_project_info_v1,
    search_project_info_v1,
)

from .project_status_detail import (
    get_project_status_detail_v1,
    search_project_status_detail_v1,
)

__all__ = [
    "logout_handler_v1",
    "get_okta_login_url_v1",
    "handle_okta_login_callback_v1",
    "get_contract_v1",
    "search_contracts_v1",
    "list_contracts_v1",
    "search_employee_profiles_v1",
    "get_employee_direct_reports_blank_v1",
    "get_employee_direct_reports_v1",
    "get_org_blank_v1",
    "get_employees_by_org_v1",
    "get_personnel_roster_v1",
    "get_employees_by_clearance_blank_v1",
    "get_employees_by_clearance_v1",
    "get_employee_profile_blank_v1",
    "get_employee_profile_v1",
    "search_employee_training_v1",
    "get_training_by_status_blank_v1",
    "get_training_by_status_v1",
    "get_training_by_org_blank_v1",
    "get_training_by_org_v1",
    "get_training_by_type_blank_v1",
    "get_training_by_type_v1",
    "get_employee_training_blank_v1",
    "get_employee_training_v1",
    "search_employee_certifications_v1",
    "get_employee_certifications_blank_v1",
    "get_employee_certifications_v1",
    "get_certifications_by_status_blank_v1",
    "get_certifications_by_status_v1",
    "get_certifications_by_org_blank_v1",
    "get_certifications_by_org_v1",
    "get_project_status_v1",
    "handle_health",
    "handle_deep_health",
    "get_agent_contract_locations_v1",
    "search_project_forecasts_v1",
    "get_project_financial_v1",
    "search_project_financials_v1",
    "list_project_financials_v1",
    "get_project_master_v1",
    "search_project_master_v1",
    "list_project_master_v1",
    "get_contract_master_v1",
    "search_contract_master_v1",
    "list_contract_master_v1",
    "get_contract_modifications_v1",
    "search_contract_modifications_v1",
    "get_contract_program_managers_v1",
    "search_contract_program_managers_v1",
    "get_contract_analysis_v1",
    "search_contract_analysis_v1",
    "get_clm_contract_v1",
    "search_clm_contracts_v1",
    "list_clm_contracts_v1",
    "get_ar_history_v1",
    "search_ar_history_v1",
    "get_unburdened_nonlabor_v1",
    "search_unburdened_nonlabor_v1",
    "get_timesheet_history_by_employee_v1",
    "get_timesheet_history_by_project_v1",
    "search_timesheet_history_v1",
    "get_voucher_history_v1",
    "search_voucher_history_v1",
    "get_po_funding_detail_v1",
    "search_po_funding_detail_v1",
    "get_real_time_commitments_v1",
    "search_real_time_commitments_v1",
    "get_gl_details_v1",
    "search_gl_details_v1",
    "get_non_labor_detail_v1",
    "search_non_labor_detail_v1",
    "get_financials_updated_v1",
    "search_financials_updated_v1",
    "get_po_open_commitments_v1",
    "search_po_open_commitments_v1",
    "get_period_target_cost_revenue_v1",
    "search_period_target_cost_revenue_v1",
    "get_project_status_history_v1",
    "search_project_status_history_v1",
    "get_project_modifications_v1",
    "search_project_modifications_v1",
    "get_project_info_v1",
    "search_project_info_v1",
    "get_project_status_detail_v1",
    "search_project_status_detail_v1",
    "get_employee_profile_complete_v1",
    "search_employee_profile_completes_v1",
    "list_employee_profile_completes_v1",
]
