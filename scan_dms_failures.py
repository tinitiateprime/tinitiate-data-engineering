# domain/models/employee_profile.py

from datetime import date
from typing import List, Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from .metadata import MetadataModel


class EmployeeProfileResponse(BaseModel):
    """Single employee profile response"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    # ============================================================
    # Employee Identity
    # ============================================================

    empl_id: str = Field(
        ...,
        alias="employeeId",
        validation_alias=AliasChoices(
            "employeeId",
            "emplId",
            "EMPL_ID",
            "empl_id",
        ),
        max_length=12,
        description="Employee ID.",
    )

    first_name: Optional[str] = Field(
        None,
        alias="firstName",
        validation_alias=AliasChoices(
            "firstName",
            "FIRST_NAME",
            "first_name",
        ),
        max_length=20,
        description="Employee first name.",
    )

    last_name: Optional[str] = Field(
        None,
        alias="lastName",
        validation_alias=AliasChoices(
            "lastName",
            "LAST_NAME",
            "last_name",
        ),
        max_length=25,
        description="Employee last name.",
    )

    last_first_name: Optional[str] = Field(
        None,
        alias="lastFirstName",
        validation_alias=AliasChoices(
            "lastFirstName",
            "LAST_FIRST_NAME",
            "last_first_name",
        ),
        max_length=25,
        description="Employee name in Last, First format.",
    )

    # ============================================================
    # Position
    # ============================================================

    title_desc: Optional[str] = Field(
        None,
        alias="titleDesc",
        validation_alias=AliasChoices(
            "titleDesc",
            "TITLE_DESC",
            "title_desc",
        ),
        max_length=30,
        description="Employee job title description.",
    )

    job_code: Optional[str] = Field(
        None,
        alias="jobCode",
        validation_alias=AliasChoices(
            "jobCode",
            "JOB_CODE",
            "job_code",
        ),
        max_length=10,
        description="Employee job code.",
    )

    s_empl_type_cd: Optional[str] = Field(
        None,
        alias="emplTypeCd",
        validation_alias=AliasChoices(
            "emplTypeCd",
            "S_EMPL_TYPE_CD",
            "s_empl_type_cd",
        ),
        max_length=1,
        description="Employee type code.",
    )

    # ============================================================
    # Organization
    # ============================================================

    org_id: Optional[str] = Field(
        None,
        alias="orgId",
        validation_alias=AliasChoices(
            "orgId",
            "ORG_ID",
            "org_id",
        ),
        max_length=20,
        description="Organization ID.",
    )

    dept_name: Optional[str] = Field(
        None,
        alias="deptName",
        validation_alias=AliasChoices(
            "deptName",
            "DEPT_NAME",
            "dept_name",
        ),
        max_length=50,
        description="Department name.",
    )

    # ============================================================
    # Location
    # ============================================================

    loc_name: Optional[str] = Field(
        None,
        alias="locName",
        validation_alias=AliasChoices(
            "locName",
            "LOC_NAME",
            "loc_name",
        ),
        max_length=50,
        description="Location name.",
    )

    loc_city: Optional[str] = Field(
        None,
        alias="locCity",
        validation_alias=AliasChoices(
            "locCity",
            "LOC_CITY",
            "loc_city",
        ),
        max_length=50,
        description="Location city.",
    )

    # ============================================================
    # Manager
    # ============================================================

    mgr_name: Optional[str] = Field(
        None,
        alias="mgrName",
        validation_alias=AliasChoices(
            "mgrName",
            "MGR_NAME",
            "mgr_name",
        ),
        max_length=25,
        description="Manager name.",
    )

    mgr_empl_id: Optional[str] = Field(
        None,
        alias="mgrEmplId",
        validation_alias=AliasChoices(
            "mgrEmplId",
            "MGR_EMPL_ID",
            "mgr_empl_id",
        ),
        max_length=12,
        description="Manager employee ID.",
    )

    # ============================================================
    # Employment Details
    # ============================================================

    hire_date: Optional[str] = Field(
        None,
        alias="hireDate",
        validation_alias=AliasChoices(
            "hireDate",
            "HIRE_DATE",
            "hire_date",
        ),
        description="Employee hire date.",
    )

    email_addr: Optional[str] = Field(
        None,
        alias="emailAddr",
        validation_alias=AliasChoices(
            "emailAddr",
            "EMAIL_ADDR",
            "email_addr",
            "emailAddress",
            "email_address",
        ),
        max_length=45,
        description="Employee email address.",
    )

    # ============================================================
    # Clearance
    # ============================================================

    clearance_status: Optional[str] = Field(
        None,
        alias="clearanceStatus",
        validation_alias=AliasChoices(
            "clearanceStatus",
            "clearance_status",
            "CLEARANCE_STATUS",
        ),
        max_length=128,
        description="Employee clearance status.",
    )

    clearance_status_date: Optional[str] = Field(
        None,
        alias="clearanceStatusDate",
        validation_alias=AliasChoices(
            "clearanceStatusDate",
            "clearance_status_date",
            "CLEARANCE_STATUS_DATE",
        ),
        description="Date of clearance status.",
    )

    clearance_eligibility: Optional[str] = Field(
        None,
        alias="clearanceEligibility",
        validation_alias=AliasChoices(
            "clearanceEligibility",
            "clearance_eligibility",
            "CLEARANCE_ELIGIBILITY",
        ),
        max_length=128,
        description="Employee clearance eligibility.",
    )

    # ============================================================
    # Field Validators
    # ============================================================

    @field_validator(
        "hire_date",
        "clearance_status_date",
        mode="before",
    )
    @classmethod
    def convert_date_to_string(cls, value):
        """
        Convert date objects to ISO-format strings.
        """

        if value is None:
            return value

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, str):
            return value

        return str(value)


class EmployeeProfileSearchServiceResponse(BaseModel):
    """
    Internal domain-level response for employee profile searches.
    Decoupled from V1/V2 specific JSON envelopes.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    items: List[EmployeeProfileResponse]
    metadata: MetadataModel
