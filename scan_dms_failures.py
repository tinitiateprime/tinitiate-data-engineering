"""
Domain models for EmployeeProfileComplete.
"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from .metadata import MetadataModel


class EmployeeProfileCompleteResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    employee_key: str = Field(..., alias="employeeKey")
    email_key: Optional[str] = Field(None, alias="emailKey")
    empl_id: Optional[str] = Field(None, alias="emplId")
    my_id: Optional[str] = Field(None, alias="myId")
    sotv_employee_id: Optional[str] = Field(None, alias="sotvEmployeeId")
    employee_name: Optional[str] = Field(None, alias="employeeName")
    job_title: Optional[str] = Field(None, alias="jobTitle")
    org_id: Optional[str] = Field(None, alias="orgId")
    dept_name: Optional[str] = Field(None, alias="deptName")
    location: Optional[str] = Field(None, alias="location")
    mgr_name: Optional[str] = Field(None, alias="mgrName")
    mgr_empl_id: Optional[str] = Field(None, alias="mgrEmplId")

    hire_date: Optional[date] = Field(None, alias="hireDate")

    clearance_status: Optional[str] = Field(None, alias="clearanceStatus")
    clearance_eligibility: Optional[str] = Field(
        None,
        alias="clearanceEligibility",
    )
    sotv_headline: Optional[str] = Field(None, alias="sotvHeadline")

    certifications: Optional[Any] = Field(None, alias="certifications")
    certification_names: Optional[List[str]] = Field(
        None,
        alias="certificationNames",
    )
    certification_count: Optional[int] = Field(
        None,
        alias="certificationCount",
    )

    skills: Optional[Any] = Field(None, alias="skills")
    skill_names: Optional[List[str]] = Field(None, alias="skillNames")
    skill_count: Optional[int] = Field(None, alias="skillCount")

    education: Optional[Any] = Field(None, alias="education")
    education_count: Optional[int] = Field(None, alias="educationCount")

    languages: Optional[List[str]] = Field(None, alias="languages")
    language_count: Optional[int] = Field(None, alias="languageCount")

    @field_validator("hire_date", mode="before")
    @classmethod
    def parse_hire_date(cls, value):
        """
        Normalize hire_date values returned by the database.

        Supported examples:
            3/31/2014
            03/31/2014
            2014-03-31
            date/datetime objects
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

            # Database currently returns M/D/YYYY.
            for date_format in (
                "%m/%d/%Y",
                "%Y-%m-%d",
            ):
                try:
                    return datetime.strptime(
                        value,
                        date_format,
                    ).date()
                except ValueError:
                    continue

        # Return original value so Pydantic can produce
        # the normal validation error for truly invalid data.
        return value


class EmployeeProfileCompleteSearchServiceResponse(BaseModel):
    """
    Internal domain-level response.
    Decoupled from V1/V2 specific JSON envelopes.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    items: List[EmployeeProfileCompleteResponse]
    metadata: MetadataModel
