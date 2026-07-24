from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import V1BaseResponseModel
from .metadata import V1MetadataModel


class V1ProjectFinancialResponseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    proj_id: str = Field(alias="projId")
    cust_name: Optional[str] = Field(default=None, alias="custName")
    proj_start_dt: Optional[str] = Field(default=None, alias="projStartDt")
    proj_end_dt: Optional[str] = Field(default=None, alias="projEndDt")
    s_proj_rpt_dc: Optional[str] = Field(default=None, alias="sProjRptDc")
    proj_name: Optional[str] = Field(default=None, alias="projName")
    org_id: Optional[str] = Field(default=None, alias="orgId")
    prime_contr_id: Optional[str] = Field(default=None, alias="primeContrId")
    active_fl: Optional[str] = Field(default=None, alias="activeFl")
    proj_type_dc: Optional[str] = Field(default=None, alias="projTypeDc")
    proj_mgr_name: Optional[str] = Field(default=None, alias="projMgrName")
    lvl_no: Optional[int] = Field(default=None, alias="lvlNo")

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
    cost_funded: Optional[float] = Field(default=None, alias="costFunded")
    fee_funded: Optional[float] = Field(default=None, alias="feeFunded")
    total_billed: Optional[float] = Field(default=None, alias="totalBilled")
    billed_cost: Optional[float] = Field(default=None, alias="billedCost")
    billed_fee: Optional[float] = Field(default=None, alias="billedFee")
    open_billing_detail_amt: Optional[float] = Field(
        default=None,
        alias="openBillingDetailAmt",
    )
    open_commit_amt: Optional[float] = Field(
        default=None,
        alias="openCommitAmt",
    )


class V1ProjectFinancialListResponseModel(V1BaseResponseModel):
    data: List[V1ProjectFinancialResponseModel]
    metadata: V1MetadataModel


class V1ProjectFinancialDetailResponseModel(V1BaseResponseModel):
    data: List[V1ProjectFinancialResponseModel]
    metadata: V1MetadataModel
