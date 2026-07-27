"""
V1 response schemas for the Project Financial API.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.filters import FilterContext
from .base import V1MetadataModel


# ---------------------------------------------------------------------------
# Allowed fields & operators, sort fields, and filter aliases
# ---------------------------------------------------------------------------
PROJECTFINANCIAL_FILTER_CONTEXT = FilterContext(
    allowed_fields={
        "proj_id": {"operators": {"eq", "in", "contains"}},
        "cust_name": {"operators": {"eq", "in", "contains"}},
        "proj_start_dt": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "proj_end_dt": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "s_proj_rpt_dc": {"operators": {"eq", "in"}},
        "proj_name": {"operators": {"eq", "in", "contains"}},
        "org_id": {"operators": {"eq", "in"}},
        "prime_contr_id": {"operators": {"eq", "in"}},
        "active_fl": {"operators": {"eq", "in"}},
        "proj_type_dc": {"operators": {"eq", "in"}},
        "proj_mgr_name": {"operators": {"eq", "in", "contains"}},
        "lvl_no": {"operators": {"eq", "in"}},
        "value_total_amount": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "project_value_cost": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "project_value_fee": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "proj_f_tot_amt": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "cost_funded": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "fee_funded": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "total_billed": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "billed_cost": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "billed_fee": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "open_billing_detail_amt": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
        "open_commit_amt": {"operators": {"eq", "gt", "gte", "lt", "lte", "between"}},
    },
    allowed_sort_fields={
        "proj_id",
        "cust_name",
        "proj_start_dt",
        "proj_end_dt",
        "s_proj_rpt_dc",
        "proj_name",
        "org_id",
        "prime_contr_id",
        "proj_type_dc",
        "proj_mgr_name",
        "lvl_no",
        "value_total_amount",
        "project_value_cost",
        "project_value_fee",
        "proj_f_tot_amt",
        "cost_funded",
        "fee_funded",
        "total_billed",
        "billed_cost",
        "billed_fee",
        "open_billing_detail_amt",
        "open_commit_amt",
    },
    filter_aliases={
        "projId": "proj_id",
        "custName": "cust_name",
        "projStartDt": "proj_start_dt",
        "projEndDt": "proj_end_dt",
        "sProjRptDc": "s_proj_rpt_dc",
        "projName": "proj_name",
        "orgId": "org_id",
        "primeContrId": "prime_contr_id",
        "activeFl": "active_fl",
        "projTypeDc": "proj_type_dc",
        "projMgrName": "proj_mgr_name",
        "lvlNo": "lvl_no",
        "valueTotalAmount": "value_total_amount",
        "projectValueCost": "project_value_cost",
        "projectValueFee": "project_value_fee",
        "projFTotAmt": "proj_f_tot_amt",
        "costFunded": "cost_funded",
        "feeFunded": "fee_funded",
        "totalBilled": "total_billed",
        "billedCost": "billed_cost",
        "billedFee": "billed_fee",
        "openBillingDetailAmt": "open_billing_detail_amt",
        "openCommitAmt": "open_commit_amt",
    },
)

# Legacy support for individual constants pointing to the new FilterContext
PROJECTFINANCIAL_ALLOWED_FILTER_FIELDS = PROJECTFINANCIAL_FILTER_CONTEXT.allowed_fields
PROJECTFINANCIAL_ALLOWED_SORT_FIELDS = PROJECTFINANCIAL_FILTER_CONTEXT.allowed_sort_fields
PROJECTFINANCIAL_FILTER_ALIASES = PROJECTFINANCIAL_FILTER_CONTEXT.filter_aliases


class V1ProjectFinancialResponseModel(BaseModel):
    """
    Public V1 response model for one Project Financial record.

    Python/database fields use snake_case.
    API responses use camelCase aliases.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    proj_id: str = Field(alias="projId")
    cust_name: Optional[str] = Field(default=None, alias="custName")

    proj_start_dt: Optional[date] = Field(
        default=None,
        alias="projStartDt",
    )
    proj_end_dt: Optional[date] = Field(
        default=None,
        alias="projEndDt",
    )
    s_proj_rpt_dc: Optional[str] = Field(
        default=None,
        alias="sProjRptDc",
    )
    proj_name: Optional[str] = Field(
        default=None,
        alias="projName",
    )
    org_id: Optional[str] = Field(
        default=None,
        alias="orgId",
    )
    prime_contr_id: Optional[str] = Field(
        default=None,
        alias="primeContrId",
    )
    active_fl: Optional[str] = Field(
        default=None,
        alias="activeFl",
    )
    proj_type_dc: Optional[str] = Field(
        default=None,
        alias="projTypeDc",
    )
    proj_mgr_name: Optional[str] = Field(
        default=None,
        alias="projMgrName",
    )
    lvl_no: Optional[int] = Field(
        default=None,
        alias="lvlNo",
    )

    value_total_amount: Optional[float] = Field(
        default=None,
        alias="valueTotalAmount",
    )
    project_value_cost: Optional[float] = Field(
        default=None,
        alias="projectValueCost",
    )
    project_value_fee: Optional[float] = Field(
        default=None,
        alias="projectValueFee",
    )
    proj_f_tot_amt: Optional[float] = Field(
        default=None,
        alias="projFTotAmt",
    )
    cost_funded: Optional[float] = Field(
        default=None,
        alias="costFunded",
    )
    fee_funded: Optional[float] = Field(
        default=None,
        alias="feeFunded",
    )
    total_billed: Optional[float] = Field(
        default=None,
        alias="totalBilled",
    )
    billed_cost: Optional[float] = Field(
        default=None,
        alias="billedCost",
    )
    billed_fee: Optional[float] = Field(
        default=None,
        alias="billedFee",
    )
    open_billing_detail_amt: Optional[float] = Field(
        default=None,
        alias="openBillingDetailAmt",
    )
    open_commit_amt: Optional[float] = Field(
        default=None,
        alias="openCommitAmt",
    )


class V1ProjectFinancialListResponseModel(BaseModel):
    """
    Response returned by the Project Financial search endpoint.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    data: List[V1ProjectFinancialResponseModel]
    metadata: V1MetadataModel


class V1ProjectFinancialDetailResponseModel(BaseModel):
    """
    Response returned by the Project Financial details endpoint.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    data: List[V1ProjectFinancialResponseModel]
    metadata: V1MetadataModel


# Reusable context for project_financial filtering and sorting (standard name)
project_financial_filter_context = PROJECTFINANCIAL_FILTER_CONTEXT
