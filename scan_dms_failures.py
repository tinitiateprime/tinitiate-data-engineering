"""
V1 schema for EmployeeProfileComplete
"""

from datetime import date
from typing import Any, List, Optional

from core.filters import FilterContext
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .base import V1BaseResponseModel, V1MetadataModel


# ============================================================
# Allowed fields & operators, sort fields, and filter aliases
# ============================================================

EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT = FilterContext(
    allowed_fields={
        "email_key": {
            "operators": {"eq", "in", "contains"}
        },
        "empl_id": {
            "operators": {"eq", "in", "contains"}
        },
        "my_id": {
            "operators": {"eq", "in", "contains"}
        },
        "sotv_employee_id": {
            "operators": {"eq", "in", "contains"}
        },

        # ----------------------------------------------------
        # NEW NAME FIELDS
        # ----------------------------------------------------
        "first_name": {
            "operators": {"eq", "in", "contains"}
        },
        "last_name": {
            "operators": {"eq", "in", "contains"}
        },
        "mid_name": {
            "operators": {"eq", "in", "contains"}
        },

        "employee_name": {
            "operators": {"eq", "in", "contains"}
        },
        "job_title": {
            "operators": {"eq", "in", "contains"}
        },
        "org_id": {
            "operators": {"eq", "in", "contains"}
        },
        "dept_name": {
            "operators": {"eq", "in", "contains"}
        },
        "location": {
            "operators": {"eq", "in", "contains"}
        },
        "mgr_name": {
            "operators": {"eq", "in", "contains"}
        },
        "mgr_empl_id": {
            "operators": {"eq", "in", "contains"}
        },
        "hire_date": {
            "operators": {
                "eq",
                "gt",
                "gte",
                "lt",
                "lte",
                "between",
            }
        },
        "clearance_status": {
            "operators": {"eq", "in", "contains"}
        },
        "clearance_eligibility": {
            "operators": {"eq", "in", "contains"}
        },
        "sotv_headline": {
            "operators": {"eq", "in", "contains"}
        },
        "certifications": {
            "operators": {"eq"}
        },
        "certification_names": {
            "operators": {"eq", "contains"}
        },
        "certification_count": {
            "operators": {
                "eq",
                "in",
                "gt",
                "gte",
                "lt",
                "lte",
                "between",
            }
        },
        "skills": {
            "operators": {"eq"}
        },
        "skill_names": {
            "operators": {"eq", "contains"}
        },
        "skill_count": {
            "operators": {
                "eq",
                "in",
                "gt",
                "gte",
                "lt",
                "lte",
                "between",
            }
        },
        "education": {
            "operators": {"eq"}
        },
        "education_count": {
            "operators": {
                "eq",
                "in",
                "gt",
                "gte",
                "lt",
                "lte",
                "between",
            }
        },
        "languages": {
            "operators": {"eq", "contains"}
        },
        "language_count": {
            "operators": {
                "eq",
                "in",
                "gt",
                "gte",
                "lt",
                "lte",
                "between",
            }
        },
    },

    allowed_sort_fields={
        "employee_key",
        "email_key",
        "empl_id",
        "my_id",
        "sotv_employee_id",

        # NEW
        "first_name",
        "last_name",
        "mid_name",

        "employee_name",
        "job_title",
        "org_id",
        "dept_name",
        "location",
        "mgr_name",
        "mgr_empl_id",
        "hire_date",
        "clearance_status",
        "clearance_eligibility",
        "sotv_headline",
        "certification_count",
        "skill_count",
        "education_count",
        "language_count",
    },

    filter_aliases={
        "emailKey": "email_key",
        "emplId": "empl_id",
        "myId": "my_id",
        "sotvEmployeeId": "sotv_employee_id",

        # ----------------------------------------------------
        # NEW NAME ALIASES
        # ----------------------------------------------------
        "firstName": "first_name",
        "lastName": "last_name",
        "midName": "mid_name",

        "employeeName": "employee_name",
        "jobTitle": "job_title",
        "orgId": "org_id",
        "deptName": "dept_name",
        "location": "location",
        "mgrName": "mgr_name",
        "mgrEmplId": "mgr_empl_id",
        "hireDate": "hire_date",
        "clearanceStatus": "clearance_status",
        "clearanceEligibility": "clearance_eligibility",
        "sotvHeadline": "sotv_headline",
        "certifications": "certifications",
        "certificationNames": "certification_names",
        "certificationCount": "certification_count",
        "skills": "skills",
        "skillNames": "skill_names",
        "skillCount": "skill_count",
        "education": "education",
        "educationCount": "education_count",
        "languages": "languages",
        "languageCount": "language_count",
    },
)


# ============================================================
# Legacy compatibility constants
# ============================================================

EMPLOYEEPROFILECOMPLETES_ALLOWED_FILTER_FIELDS = (
    EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT.allowed_fields
)

EMPLOYEEPROFILECOMPLETES_ALLOWED_SORT_FIELDS = (
    EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT.allowed_sort_fields
)

EMPLOYEEPROFILECOMPLETES_FILTER_ALIASES = (
    EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT.filter_aliases
)


# ============================================================
# Employee Profile Complete response model
# ============================================================

class V1EmployeeProfileCompleteResponseModel(BaseModel):
    """
    External API representation of an EmployeeProfileComplete.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    # --------------------------------------------------------
    # Internal surrogate / pagination key
    # --------------------------------------------------------
    employee_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "employeeKey",
            "employee_key",
        ),
        serialization_alias="employeeKey",
        description="Surrogate key for deterministic pagination.",
    )

    # --------------------------------------------------------
    # Employee identifiers
    # --------------------------------------------------------
    email_key: Optional[str] = Field(
        default=None,
        validation_alias="email_key",
        serialization_alias="emailKey",
    )

    empl_id: Optional[str] = Field(
        default=None,
        validation_alias="empl_id",
        serialization_alias="emplId",
    )

    my_id: Optional[str] = Field(
        default=None,
        validation_alias="my_id",
        serialization_alias="myId",
    )

    sotv_employee_id: Optional[str] = Field(
        default=None,
        validation_alias="sotv_employee_id",
        serialization_alias="sotvEmployeeId",
    )

    # --------------------------------------------------------
    # NEW: Employee name fields
    # --------------------------------------------------------
    first_name: Optional[str] = Field(
        default=None,
        validation_alias="first_name",
        serialization_alias="firstName",
    )

    last_name: Optional[str] = Field(
        default=None,
        validation_alias="last_name",
        serialization_alias="lastName",
    )

    mid_name: Optional[str] = Field(
        default=None,
        validation_alias="mid_name",
        serialization_alias="midName",
    )

    employee_name: Optional[str] = Field(
        default=None,
        validation_alias="employee_name",
        serialization_alias="employeeName",
    )

    # --------------------------------------------------------
    # Employee profile attributes
    # --------------------------------------------------------
    job_title: Optional[str] = Field(
        default=None,
        validation_alias="job_title",
        serialization_alias="jobTitle",
    )

    org_id: Optional[str] = Field(
        default=None,
        validation_alias="org_id",
        serialization_alias="orgId",
    )

    dept_name: Optional[str] = Field(
        default=None,
        validation_alias="dept_name",
        serialization_alias="deptName",
    )

    location: Optional[str] = Field(
        default=None,
        validation_alias="location",
        serialization_alias="location",
    )

    mgr_name: Optional[str] = Field(
        default=None,
        validation_alias="mgr_name",
        serialization_alias="mgrName",
    )

    mgr_empl_id: Optional[str] = Field(
        default=None,
        validation_alias="mgr_empl_id",
        serialization_alias="mgrEmplId",
    )

    hire_date: Optional[date] = Field(
        default=None,
        validation_alias="hire_date",
        serialization_alias="hireDate",
    )

    clearance_status: Optional[str] = Field(
        default=None,
        validation_alias="clearance_status",
        serialization_alias="clearanceStatus",
    )

    clearance_eligibility: Optional[str] = Field(
        default=None,
        validation_alias="clearance_eligibility",
        serialization_alias="clearanceEligibility",
    )

    sotv_headline: Optional[str] = Field(
        default=None,
        validation_alias="sotv_headline",
        serialization_alias="sotvHeadline",
    )

    # --------------------------------------------------------
    # Certifications
    # --------------------------------------------------------
    certifications: Optional[Any] = Field(
        default=None,
        validation_alias="certifications",
        serialization_alias="certifications",
    )

    certification_names: Optional[List[str]] = Field(
        default=None,
        validation_alias="certification_names",
        serialization_alias="certificationNames",
    )

    certification_count: Optional[int] = Field(
        default=None,
        validation_alias="certification_count",
        serialization_alias="certificationCount",
    )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------
    skills: Optional[Any] = Field(
        default=None,
        validation_alias="skills",
        serialization_alias="skills",
    )

    skill_names: Optional[List[str]] = Field(
        default=None,
        validation_alias="skill_names",
        serialization_alias="skillNames",
    )

    skill_count: Optional[int] = Field(
        default=None,
        validation_alias="skill_count",
        serialization_alias="skillCount",
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------
    education: Optional[Any] = Field(
        default=None,
        validation_alias="education",
        serialization_alias="education",
    )

    education_count: Optional[int] = Field(
        default=None,
        validation_alias="education_count",
        serialization_alias="educationCount",
    )

    # --------------------------------------------------------
    # Languages
    # --------------------------------------------------------
    languages: Optional[List[str]] = Field(
        default=None,
        validation_alias="languages",
        serialization_alias="languages",
    )

    language_count: Optional[int] = Field(
        default=None,
        validation_alias="language_count",
        serialization_alias="languageCount",
    )


# ============================================================
# List response
# ============================================================

class V1EmployeeProfileCompleteListResponseModel(V1BaseResponseModel):
    metadata: V1MetadataModel
    data: List[V1EmployeeProfileCompleteResponseModel]


# ============================================================
# Detail response
# ============================================================

class V1EmployeeProfileCompleteDetailResponseModel(V1BaseResponseModel):
    metadata: V1MetadataModel
    data: List[V1EmployeeProfileCompleteResponseModel]


# ============================================================
# Reusable context
# ============================================================

employee_profile_complete_filter_context = (
    EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT
)
