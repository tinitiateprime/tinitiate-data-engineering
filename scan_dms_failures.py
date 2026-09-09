"""
V1 schema for IRC Census Report.

Supports:
- Filtering
- Sorting
- API aliases
- PostgreSQL/MV uppercase column names
- Internal lowercase repository column names
"""

from datetime import date
from typing import List, Optional

from core.filters import FilterContext
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .base import V1BaseResponseModel, V1MetadataModel


# =============================================================================
# FILTER CONTEXT
# =============================================================================

IRCCENSUSREPORT_FILTER_CONTEXT = FilterContext(
    allowed_fields={
        "my_id": {
            "operators": {"eq", "in", "contains"},
        },
        "last_first_name": {
            "operators": {"eq", "in", "contains"},
        },
        "prir_name": {
            "operators": {"eq", "in", "contains"},
        },
        "s_empl_status_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "hire_dt": {
            "operators": {"eq", "gt", "gte", "lt", "lte", "between"},
        },
        "reh_dt": {
            "operators": {"eq", "gt", "gte", "lt", "lte", "between"},
        },
        "term_dt": {
            "operators": {"eq", "gt", "gte", "lt", "lte", "between"},
        },
        "seniority_dt": {
            "operators": {"eq", "gt", "gte", "lt", "lte", "between"},
        },
        "term_reason_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "taxble_entity_id": {
            "operators": {"eq", "in", "contains"},
        },
        "locator_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "empl_class_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "pto_accrl_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "bu_name": {
            "operators": {"eq", "in", "contains"},
        },
        "dept_num": {
            "operators": {"eq", "in", "contains"},
        },
        "detl_job_cd": {
            "operators": {"eq", "in", "contains"},
        },
        "title_desc": {
            "operators": {"eq", "in", "contains"},
        },
        "mgr_name": {
            "operators": {"eq", "in", "contains"},
        },
    },

    allowed_sort_fields={
        "row_id",
        "my_id",
        "last_first_name",
        "prir_name",
        "s_empl_status_cd",
        "hire_dt",
        "reh_dt",
        "term_dt",
        "seniority_dt",
        "term_reason_cd",
        "taxble_entity_id",
        "locator_cd",
        "empl_class_cd",
        "pto_accrl_cd",
        "bu_name",
        "dept_num",
        "detl_job_cd",
        "title_desc",
        "mgr_name",
    },

    filter_aliases={
        "myId": "my_id",
        "lastFirstName": "last_first_name",
        "prirName": "prir_name",
        "sEmplStatusCd": "s_empl_status_cd",
        "hireDt": "hire_dt",
        "rehDt": "reh_dt",
        "termDt": "term_dt",
        "seniorityDt": "seniority_dt",
        "termReasonCd": "term_reason_cd",
        "taxbleEntityId": "taxble_entity_id",
        "locatorCd": "locator_cd",
        "emplClassCd": "empl_class_cd",
        "ptoAccrlCd": "pto_accrl_cd",
        "buName": "bu_name",
        "deptNum": "dept_num",
        "detlJobCd": "detl_job_cd",
        "titleDesc": "title_desc",
        "mgrName": "mgr_name",
    },
)


# =============================================================================
# LEGACY SUPPORT
# =============================================================================

IRCCENSUSREPORTS_ALLOWED_FILTER_FIELDS = (
    IRCCENSUSREPORT_FILTER_CONTEXT.allowed_fields
)

IRCCENSUSREPORTS_ALLOWED_SORT_FIELDS = (
    IRCCENSUSREPORT_FILTER_CONTEXT.allowed_sort_fields
)

IRCCENSUSREPORTS_FILTER_ALIASES = (
    IRCCENSUSREPORT_FILTER_CONTEXT.filter_aliases
)


# =============================================================================
# RESPONSE MODEL
# =============================================================================

class V1IrcCensusReportResponseModel(BaseModel):
    """
    External API representation of an IRC Census Report.

    The materialized view may return uppercase PostgreSQL column names
    such as LAST_FIRST_NAME while the repository may return lowercase
    names such as last_first_name.

    AliasChoices allows both forms.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    # -------------------------------------------------------------------------
    # Surrogate row identifier
    # PostgreSQL MV column: row_id
    # -------------------------------------------------------------------------
    row_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "row_id",
            "ROW_ID",
            "rowid",
            "rowId",
        ),
        serialization_alias="rowId",
        description="Surrogate key used for deterministic pagination.",
    )

    # -------------------------------------------------------------------------
    # MY_ID
    # -------------------------------------------------------------------------
    my_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "my_id",
            "MY_ID",
            "myId",
        ),
        serialization_alias="myId",
    )

    # -------------------------------------------------------------------------
    # LAST_FIRST_NAME
    # -------------------------------------------------------------------------
    last_first_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "last_first_name",
            "LAST_FIRST_NAME",
            "lastFirstName",
        ),
        serialization_alias="lastFirstName",
    )

    # -------------------------------------------------------------------------
    # PRIR_NAME
    # -------------------------------------------------------------------------
    prir_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "prir_name",
            "PRIR_NAME",
            "prirName",
        ),
        serialization_alias="prirName",
    )

    # -------------------------------------------------------------------------
    # S_EMPL_STATUS_CD
    # -------------------------------------------------------------------------
    s_empl_status_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "s_empl_status_cd",
            "S_EMPL_STATUS_CD",
            "sEmplStatusCd",
        ),
        serialization_alias="sEmplStatusCd",
    )

    # -------------------------------------------------------------------------
    # HIRE_DT
    # -------------------------------------------------------------------------
    hire_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "hire_dt",
            "HIRE_DT",
            "hireDt",
        ),
        serialization_alias="hireDt",
    )

    # -------------------------------------------------------------------------
    # REH_DT
    # -------------------------------------------------------------------------
    reh_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "reh_dt",
            "REH_DT",
            "rehDt",
        ),
        serialization_alias="rehDt",
    )

    # -------------------------------------------------------------------------
    # TERM_DT
    # -------------------------------------------------------------------------
    term_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "term_dt",
            "TERM_DT",
            "termDt",
        ),
        serialization_alias="termDt",
    )

    # -------------------------------------------------------------------------
    # SENIORITY_DT
    # -------------------------------------------------------------------------
    seniority_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "seniority_dt",
            "SENIORITY_DT",
            "seniorityDt",
        ),
        serialization_alias="seniorityDt",
    )

    # -------------------------------------------------------------------------
    # TERM_REASON_CD
    # -------------------------------------------------------------------------
    term_reason_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "term_reason_cd",
            "TERM_REASON_CD",
            "termReasonCd",
        ),
        serialization_alias="termReasonCd",
    )

    # -------------------------------------------------------------------------
    # TAXBLE_ENTITY_ID
    # Keep spelling exactly as it exists in the MV.
    # -------------------------------------------------------------------------
    taxble_entity_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "taxble_entity_id",
            "TAXBLE_ENTITY_ID",
            "taxbleEntityId",
        ),
        serialization_alias="taxbleEntityId",
    )

    # -------------------------------------------------------------------------
    # LOCATOR_CD
    # -------------------------------------------------------------------------
    locator_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "locator_cd",
            "LOCATOR_CD",
            "locatorCd",
        ),
        serialization_alias="locatorCd",
    )

    # -------------------------------------------------------------------------
    # EMPL_CLASS_CD
    # -------------------------------------------------------------------------
    empl_class_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "empl_class_cd",
            "EMPL_CLASS_CD",
            "emplClassCd",
        ),
        serialization_alias="emplClassCd",
    )

    # -------------------------------------------------------------------------
    # PTO_ACCRL_CD
    # -------------------------------------------------------------------------
    pto_accrl_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "pto_accrl_cd",
            "PTO_ACCRL_CD",
            "ptoAccrlCd",
        ),
        serialization_alias="ptoAccrlCd",
    )

    # -------------------------------------------------------------------------
    # BU_NAME
    # -------------------------------------------------------------------------
    bu_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "bu_name",
            "BU_NAME",
            "buName",
        ),
        serialization_alias="buName",
    )

    # -------------------------------------------------------------------------
    # DEPT_NUM
    # -------------------------------------------------------------------------
    dept_num: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "dept_num",
            "DEPT_NUM",
            "deptNum",
        ),
        serialization_alias="deptNum",
    )

    # -------------------------------------------------------------------------
    # DETL_JOB_CD
    # -------------------------------------------------------------------------
    detl_job_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "detl_job_cd",
            "DETL_JOB_CD",
            "detlJobCd",
        ),
        serialization_alias="detlJobCd",
    )

    # -------------------------------------------------------------------------
    # TITLE_DESC
    # -------------------------------------------------------------------------
    title_desc: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "title_desc",
            "TITLE_DESC",
            "titleDesc",
        ),
        serialization_alias="titleDesc",
    )

    # -------------------------------------------------------------------------
    # MGR_NAME
    # -------------------------------------------------------------------------
    mgr_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "mgr_name",
            "MGR_NAME",
            "mgrName",
        ),
        serialization_alias="mgrName",
    )


# =============================================================================
# LIST RESPONSE
# =============================================================================

class V1IrcCensusReportListResponseModel(V1BaseResponseModel):
    """
    Response model used by list/search IRC Census Report endpoints.
    """

    metadata: V1MetadataModel
    data: List[V1IrcCensusReportResponseModel]


# =============================================================================
# DETAIL RESPONSE
# =============================================================================

class V1IrcCensusReportDetailResponseModel(V1BaseResponseModel):
    """
    Response model used by the IRC Census Report detail endpoint.
    """

    metadata: V1MetadataModel
    data: List[V1IrcCensusReportResponseModel]


# =============================================================================
# REUSABLE FILTER CONTEXT
# =============================================================================

irc_census_report_filter_context = IRCCENSUSREPORT_FILTER_CONTEXT
