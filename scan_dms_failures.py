# domain/models/project_status_report.py

from datetime import date
from typing import List, Optional

from domain.models.metadata import MetadataModel
from pydantic import BaseModel, ConfigDict


class ProjectStatusReportResponse(BaseModel):
    """
    Single project status history/report record
    from gold.project_status_report_vw.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    # ---------------------------------------------------------
    # Fiscal period
    # ---------------------------------------------------------
    fiscal_year: Optional[str] = None
    period: Optional[int] = None
    sub_pd_no: Optional[int] = None

    # ---------------------------------------------------------
    # Project / organization
    # ---------------------------------------------------------
    company_id: Optional[str] = None
    proj_id: Optional[str] = None
    proj_name: Optional[str] = None
    proj_type_dc: Optional[str] = None
    proj_abbrv_cd: Optional[str] = None
    status: Optional[str] = None
    org_id: Optional[str] = None
    lvl_no: Optional[str] = None

    # ---------------------------------------------------------
    # Project manager / customer
    # ---------------------------------------------------------
    proj_mgr_name: Optional[str] = None
    project_manager_id: Optional[str] = None
    cust_id: Optional[str] = None
    customer_po_id: Optional[str] = None

    # ---------------------------------------------------------
    # Project dates
    # ---------------------------------------------------------
    proj_start_dt: Optional[date] = None
    proj_end_dt: Optional[date] = None

    # ---------------------------------------------------------
    # Contract identifiers
    # ---------------------------------------------------------
    prime_contr_id: Optional[str] = None
    subcontr_id: Optional[str] = None
    task_order_no: Optional[str] = None
    cntr_id: Optional[str] = None

    # ---------------------------------------------------------
    # Contract values
    # ---------------------------------------------------------
    contract_value_total: Optional[float] = None
    contract_value_cost: Optional[float] = None
    contract_value_fee: Optional[float] = None
    contract_value_award_fee: Optional[float] = None

    # ---------------------------------------------------------
    # Funded values
    # ---------------------------------------------------------
    funded_value_total: Optional[float] = None
    funded_value_cost: Optional[float] = None
    funded_value_fee: Optional[float] = None
    funded_value_award_fee: Optional[float] = None

    # ---------------------------------------------------------
    # Account
    # ---------------------------------------------------------
    account_id: Optional[str] = None
    account_org_id: Optional[str] = None

    # ---------------------------------------------------------
    # Sub-period
    # ---------------------------------------------------------
    sub_period_amt: Optional[float] = None
    sub_period_budget_amt: Optional[float] = None
    sub_period_hours: Optional[float] = None
    sub_period_units: Optional[float] = None

    # ---------------------------------------------------------
    # Period
    # ---------------------------------------------------------
    period_budget_amt: Optional[float] = None
    period_incurred_amt: Optional[float] = None
    period_hours: Optional[float] = None
    period_units: Optional[float] = None

    # ---------------------------------------------------------
    # Year-to-date
    # ---------------------------------------------------------
    ytd_budget_amt: Optional[float] = None
    ytd_incurred_amt: Optional[float] = None
    ytd_hours: Optional[float] = None
    ytd_units: Optional[float] = None

    # ---------------------------------------------------------
    # Inception-to-date
    # ---------------------------------------------------------
    itd_budget_amt: Optional[float] = None
    itd_incurred_amt: Optional[float] = None
    itd_hours: Optional[float] = None
    itd_units: Optional[float] = None

    # ---------------------------------------------------------
    # Prior year / variances
    # ---------------------------------------------------------
    prior_year_incurred_amt: Optional[float] = None
    period_variance: Optional[float] = None
    ytd_variance: Optional[float] = None
    itd_variance: Optional[float] = None

    # ---------------------------------------------------------
    # Commitments / billing
    # ---------------------------------------------------------
    open_po_amt: Optional[float] = None
    total_committed: Optional[float] = None
    cumulative_billed: Optional[float] = None
    ar_balance_due: Optional[float] = None
    delivery_amt: Optional[float] = None
    billing_withhold_amt: Optional[float] = None
    billing_withhold_released_amt: Optional[float] = None

    # ---------------------------------------------------------
    # Percentages
    # ---------------------------------------------------------
    itd_percent_spent: Optional[float] = None
    ytd_percent_spent: Optional[float] = None
    period_percent_spent: Optional[float] = None
    percent_of_funded_value: Optional[float] = None
    percent_of_contract_value: Optional[float] = None

    # ---------------------------------------------------------
    # Remaining / available budgets
    # ---------------------------------------------------------
    remaining_funded_budget: Optional[float] = None
    remaining_contract_budget: Optional[float] = None
    available_budget: Optional[float] = None


class ProjectStatusReportSearchServiceResponse(BaseModel):
    """
    Search/service response for project status report history.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[ProjectStatusReportResponse]
    metadata: MetadataModel


from domain.models.project_status_report import (
    ProjectStatusReportResponse,
    ProjectStatusReportSearchServiceResponse,
)


ProjectStatusReportResponse
ProjectStatusReportSearchServiceResponse
