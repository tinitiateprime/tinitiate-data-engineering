"""
Unit tests for domain.models.employee_profile_complete.

EmployeeProfileComplete detail lookup uses empl_id.

employee_key remains part of the response model/data,
but it is NOT the API lookup argument.
"""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from domain.models.employee_profile_complete import (
    EmployeeProfileCompleteResponse,
    EmployeeProfileCompleteSearchServiceResponse,
)
from domain.models.metadata import MetadataModel


# ============================================================
# TEST DATA
# ============================================================

VALID_EMPLOYEE = {
    "employeeKey": "EMPLOYEE-KEY-001",
    "emailKey": "john.doe@example.com",
    "emplId": "EMP-1001",
    "myId": "MY-1001",
    "sotvEmployeeId": "SOTV-1001",
    "firstName": "John",
    "lastName": "Doe",
    "midName": "A",
    "employeeName": "John A Doe",
    "jobTitle": "Engineer",
    "orgId": "ORG1",
    "deptName": "Engineering",
    "location": "New York",
    "mgrName": "Jane Doe",
    "mgrEmplId": "EMP-2001",
    "hireDate": "2026-01-01",
    "clearanceStatus": "ACTIVE",
    "clearanceEligibility": "SECRET",
    "sotvHeadline": "Engineer",
    "certifications": {"aws": "AWS Certified"},
    "certificationNames": ["AWS"],
    "certificationCount": 1,
    "skills": {"python": "advanced"},
    "skillNames": ["Python"],
    "skillCount": 1,
    "education": {"degree": "BS"},
    "educationCount": 1,
    "languages": ["English"],
    "languageCount": 1,
}


# ============================================================
# BASIC MODEL TESTS
# ============================================================

def test_employee_profile_complete_valid_alias_payload():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    assert model.employee_key == "EMPLOYEE-KEY-001"
    assert model.email_key == "john.doe@example.com"

    # IMPORTANT:
    # detail lookup field is empl_id
    assert model.empl_id == "EMP-1001"

    assert model.first_name == "John"
    assert model.last_name == "Doe"
    assert model.employee_name == "John A Doe"
    assert model.org_id == "ORG1"


def test_employee_profile_complete_accepts_field_names():
    """
    populate_by_name=True means snake_case fields
    can also be provided directly.
    """

    payload = {
        "employee_key": "EMPLOYEE-KEY-001",
        "empl_id": "EMP-1001",
        "first_name": "John",
        "last_name": "Doe",
    }

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.employee_key == "EMPLOYEE-KEY-001"
    assert model.empl_id == "EMP-1001"
    assert model.first_name == "John"
    assert model.last_name == "Doe"


def test_employee_key_required():
    payload = VALID_EMPLOYEE.copy()
    payload.pop("employeeKey")

    with pytest.raises(ValidationError):
        EmployeeProfileCompleteResponse.model_validate(
            payload
        )


def test_empl_id_optional():
    """
    empl_id is Optional in the response model.

    The HANDLER/SERVICE requires empl_id for the detail endpoint,
    but the model itself permits None.
    """

    payload = VALID_EMPLOYEE.copy()
    payload["emplId"] = None

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.empl_id is None


def test_optional_fields_can_be_none():
    payload = {
        "employeeKey": "EMPLOYEE-KEY-001",
        "emailKey": None,
        "emplId": None,
        "myId": None,
        "sotvEmployeeId": None,
        "firstName": None,
        "lastName": None,
        "midName": None,
        "employeeName": None,
        "jobTitle": None,
        "orgId": None,
        "deptName": None,
        "location": None,
        "mgrName": None,
        "mgrEmplId": None,
        "hireDate": None,
        "clearanceStatus": None,
        "clearanceEligibility": None,
        "sotvHeadline": None,
        "certifications": None,
        "certificationNames": None,
        "certificationCount": None,
        "skills": None,
        "skillNames": None,
        "skillCount": None,
        "education": None,
        "educationCount": None,
        "languages": None,
        "languageCount": None,
    }

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.employee_key == "EMPLOYEE-KEY-001"
    assert model.empl_id is None
    assert model.first_name is None
    assert model.hire_date is None


# ============================================================
# ALIAS TESTS
# ============================================================

def test_model_dump_by_alias():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    dumped = model.model_dump(by_alias=True)

    assert dumped["employeeKey"] == "EMPLOYEE-KEY-001"
    assert dumped["emplId"] == "EMP-1001"
    assert dumped["firstName"] == "John"
    assert dumped["lastName"] == "Doe"
    assert dumped["mgrEmplId"] == "EMP-2001"

    assert "employee_key" not in dumped
    assert "empl_id" not in dumped


def test_model_dump_without_alias():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    dumped = model.model_dump()

    assert dumped["employee_key"] == "EMPLOYEE-KEY-001"
    assert dumped["empl_id"] == "EMP-1001"
    assert dumped["first_name"] == "John"
    assert dumped["last_name"] == "Doe"


# ============================================================
# HIRE DATE VALIDATOR TESTS
# ============================================================

def test_hire_date_iso_format():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = "2026-01-15"

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date == date(2026, 1, 15)


def test_hire_date_database_format():
    """
    Current validator supports M/D/YYYY-style database values.
    """

    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = "1/15/2026"

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date == date(2026, 1, 15)


def test_hire_date_empty_string_returns_none():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = ""

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date is None


def test_hire_date_whitespace_returns_none():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = "   "

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date is None


def test_hire_date_none():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = None

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date is None


def test_hire_date_date_object():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = date(2026, 2, 1)

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date == date(2026, 2, 1)


def test_hire_date_datetime_object():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = datetime(
        2026,
        2,
        1,
        12,
        30,
        0,
    )

    model = EmployeeProfileCompleteResponse.model_validate(
        payload
    )

    assert model.hire_date == date(2026, 2, 1)


def test_hire_date_invalid_value():
    payload = VALID_EMPLOYEE.copy()
    payload["hireDate"] = "not-a-date"

    with pytest.raises(ValidationError):
        EmployeeProfileCompleteResponse.model_validate(
            payload
        )


# ============================================================
# JSON / LIST FIELDS
# ============================================================

def test_certifications_field():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    assert model.certifications == {
        "aws": "AWS Certified"
    }

    assert model.certification_names == ["AWS"]
    assert model.certification_count == 1


def test_skills_field():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    assert model.skills == {
        "python": "advanced"
    }

    assert model.skill_names == ["Python"]
    assert model.skill_count == 1


def test_education_field():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    assert model.education == {
        "degree": "BS"
    }

    assert model.education_count == 1


def test_languages_field():
    model = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    assert model.languages == ["English"]
    assert model.language_count == 1


# ============================================================
# SEARCH SERVICE RESPONSE MODEL
# ============================================================

def test_search_service_response_success():
    employee = EmployeeProfileCompleteResponse.model_validate(
        VALID_EMPLOYEE
    )

    metadata = MetadataModel(
        cursor=None,
        has_more=False,
        applied_filters=None,
    )

    response = EmployeeProfileCompleteSearchServiceResponse(
        items=[employee],
        metadata=metadata,
    )

    assert len(response.items) == 1
    assert response.items[0].empl_id == "EMP-1001"

    assert response.metadata.cursor is None
    assert response.metadata.has_more is False


def test_search_service_response_empty():
    metadata = MetadataModel(
        cursor=None,
        has_more=False,
        applied_filters=None,
    )

    response = EmployeeProfileCompleteSearchServiceResponse(
        items=[],
        metadata=metadata,
    )

    assert response.items == []
    assert response.metadata.has_more is False


def test_search_service_response_multiple_employees():
    first = VALID_EMPLOYEE.copy()

    second = VALID_EMPLOYEE.copy()
    second["employeeKey"] = "EMPLOYEE-KEY-002"
    second["emplId"] = "EMP-1002"
    second["firstName"] = "Jane"
    second["lastName"] = "Smith"

    metadata = MetadataModel(
        cursor="NEXT-CURSOR",
        has_more=True,
        applied_filters=None,
    )

    response = EmployeeProfileCompleteSearchServiceResponse(
        items=[
            EmployeeProfileCompleteResponse.model_validate(
                first
            ),
            EmployeeProfileCompleteResponse.model_validate(
                second
            ),
        ],
        metadata=metadata,
    )

    assert len(response.items) == 2

    assert response.items[0].empl_id == "EMP-1001"
    assert response.items[1].empl_id == "EMP-1002"

    assert response.metadata.cursor == "NEXT-CURSOR"
    assert response.metadata.has_more is True


# ============================================================
# REGRESSION TEST - EMPL_ID MUST EXIST
# ============================================================

def test_model_has_empl_id_field():
    """
    Regression protection.

    employee_key remains part of the data model,
    but empl_id must also be present because the detail endpoint
    performs lookup using empl_id.
    """

    fields = EmployeeProfileCompleteResponse.model_fields

    assert "employee_key" in fields
    assert "empl_id" in fields

    assert fields["empl_id"].alias == "emplId"
