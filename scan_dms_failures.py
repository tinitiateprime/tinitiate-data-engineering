"""
Domain models for IRC Census Report.
"""

from datetime import date
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .metadata import MetadataModel


class IrcCensusReportResponse(BaseModel):
    """
    Domain response model for a single IRC Census Report record.

    Supports:
    - database/repository snake_case field names
    - uppercase materialized-view column names
    - camelCase API aliases
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    row_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "row_id",
            "ROW_ID",
            "rowid",
            "rowId",
        ),
        serialization_alias="rowId",
    )

    my_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "my_id",
            "MY_ID",
            "myId",
        ),
        serialization_alias="myId",
    )

    last_first_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "last_first_name",
            "LAST_FIRST_NAME",
            "lastFirstName",
        ),
        serialization_alias="lastFirstName",
    )

    prir_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "prir_name",
            "PRIR_NAME",
            "prirName",
        ),
        serialization_alias="prirName",
    )

    s_empl_status_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "s_empl_status_cd",
            "S_EMPL_STATUS_CD",
            "sEmplStatusCd",
        ),
        serialization_alias="sEmplStatusCd",
    )

    hire_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "hire_dt",
            "HIRE_DT",
            "hireDt",
        ),
        serialization_alias="hireDt",
    )

    reh_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "reh_dt",
            "REH_DT",
            "rehDt",
        ),
        serialization_alias="rehDt",
    )

    term_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "term_dt",
            "TERM_DT",
            "termDt",
        ),
        serialization_alias="termDt",
    )

    seniority_dt: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "seniority_dt",
            "SENIORITY_DT",
            "seniorityDt",
        ),
        serialization_alias="seniorityDt",
    )

    term_reason_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "term_reason_cd",
            "TERM_REASON_CD",
            "termReasonCd",
        ),
        serialization_alias="termReasonCd",
    )

    taxble_entity_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "taxble_entity_id",
            "TAXBLE_ENTITY_ID",
            "taxbleEntityId",
        ),
        serialization_alias="taxbleEntityId",
    )

    locator_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "locator_cd",
            "LOCATOR_CD",
            "locatorCd",
        ),
        serialization_alias="locatorCd",
    )

    empl_class_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "empl_class_cd",
            "EMPL_CLASS_CD",
            "emplClassCd",
        ),
        serialization_alias="emplClassCd",
    )

    pto_accrl_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "pto_accrl_cd",
            "PTO_ACCRL_CD",
            "ptoAccrlCd",
        ),
        serialization_alias="ptoAccrlCd",
    )

    bu_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "bu_name",
            "BU_NAME",
            "buName",
        ),
        serialization_alias="buName",
    )

    dept_num: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "dept_num",
            "DEPT_NUM",
            "deptNum",
        ),
        serialization_alias="deptNum",
    )

    detl_job_cd: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "detl_job_cd",
            "DETL_JOB_CD",
            "detlJobCd",
        ),
        serialization_alias="detlJobCd",
    )

    title_desc: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "title_desc",
            "TITLE_DESC",
            "titleDesc",
        ),
        serialization_alias="titleDesc",
    )

    mgr_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "mgr_name",
            "MGR_NAME",
            "mgrName",
        ),
        serialization_alias="mgrName",
    )


class IrcCensusReportSearchServiceResponse(BaseModel):
    """
    Internal domain-level search/list response.

    This is used between repository/service/handler layers.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        from_attributes=True,
    )

    items: List[IrcCensusReportResponse]
    metadata: MetadataModel


class IrcCensusReportDetailServiceResponse(BaseModel):
    """
    Internal domain-level detail response.

    Kept separate so the handler/service can use a detail-specific type
    while still returning a list when LAST_FIRST_NAME is not guaranteed
    to be unique.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        from_attributes=True,
    )

    items: List[IrcCensusReportResponse]
    metadata: MetadataModel
