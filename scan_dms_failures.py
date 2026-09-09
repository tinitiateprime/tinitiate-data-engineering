"""
Auto-generated V1 schema for IrcCensusReport
"""

from datetime import date
from typing import Any, List, Optional

from core.filters import FilterContext
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .base import V1BaseResponseModel, V1MetadataModel


# =============================================================================
# Allowed fields & operators, sort fields, and filter aliases
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
# Legacy constants
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
# Response Model
# =============================================================================

class V1IrcCensusReportResponseModel(BaseModel):
    """
    External API representation of an IrcCensusReport.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    # -------------------------------------------------------------------------
    # IMPORTANT:
    # DB/MV row_id is integer.
    # Keep this as Optional[int], NOT str.
    # row_id is used for stable/keyset pagination.
    # -------------------------------------------------------------------------
    row_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "rowid",
            "row_id",
        ),
        serialization_alias="rowid",
        description="Surrogate key for deterministic pagination.",
    )

    my_id: Optional[str] = Field(
        default=None,
        validation_alias="my_id",
        serialization_alias="myId",
    )

    last_first_name: Optional[str] = Field(
        default=None,
        validation_alias="last_first_name",
        serialization_alias="lastFirstName",
    )

    prir_name: Optional[str] = Field(
        default=None,
        validation_alias="prir_name",
        serialization_alias="prirName",
    )

    s_empl_status_cd: Optional[str] = Field(
        default=None,
        validation_alias="s_empl_status_cd",
        serialization_alias="sEmplStatusCd",
    )

    hire_dt: Optional[date] = Field(
        default=None,
        validation_alias="hire_dt",
        serialization_alias="hireDt",
    )

    reh_dt: Optional[date] = Field(
        default=None,
        validation_alias="reh_dt",
        serialization_alias="rehDt",
    )

    term_dt: Optional[date] = Field(
        default=None,
        validation_alias="term_dt",
        serialization_alias="termDt",
    )

    seniority_dt: Optional[date] = Field(
        default=None,
        validation_alias="seniority_dt",
        serialization_alias="seniorityDt",
    )

    term_reason_cd: Optional[str] = Field(
        default=None,
        validation_alias="term_reason_cd",
        serialization_alias="termReasonCd",
    )

    taxble_entity_id: Optional[str] = Field(
        default=None,
        validation_alias="taxble_entity_id",
        serialization_alias="taxbleEntityId",
    )

    locator_cd: Optional[str] = Field(
        default=None,
        validation_alias="locator_cd",
        serialization_alias="locatorCd",
    )

    empl_class_cd: Optional[str] = Field(
        default=None,
        validation_alias="empl_class_cd",
        serialization_alias="emplClassCd",
    )

    pto_accrl_cd: Optional[str] = Field(
        default=None,
        validation_alias="pto_accrl_cd",
        serialization_alias="ptoAccrlCd",
    )

    bu_name: Optional[str] = Field(
        default=None,
        validation_alias="bu_name",
        serialization_alias="buName",
    )

    dept_num: Optional[str] = Field(
        default=None,
        validation_alias="dept_num",
        serialization_alias="deptNum",
    )

    detl_job_cd: Optional[str] = Field(
        default=None,
        validation_alias="detl_job_cd",
        serialization_alias="detlJobCd",
    )

    title_desc: Optional[str] = Field(
        default=None,
        validation_alias="title_desc",
        serialization_alias="titleDesc",
    )

    mgr_name: Optional[str] = Field(
        default=None,
        validation_alias="mgr_name",
        serialization_alias="mgrName",
    )


# =============================================================================
# List Response
# =============================================================================

class V1IrcCensusReportListResponseModel(V1BaseResponseModel):
    """
    Response returned for IRC Census list/search requests.
    """

    metadata: V1MetadataModel
    data: List[V1IrcCensusReportResponseModel]


# =============================================================================
# Detail Response
# =============================================================================

class V1IrcCensusReportDetailResponseModel(V1BaseResponseModel):
    """
    Response returned for a single IRC Census employee lookup.
    """

    metadata: V1MetadataModel
    data: List[V1IrcCensusReportResponseModel]


# =============================================================================
# Reusable filter context
# =============================================================================

irc_census_report_filter_context = IRCCENSUSREPORT_FILTER_CONTEXT
