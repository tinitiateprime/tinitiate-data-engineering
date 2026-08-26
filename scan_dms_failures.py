import pytest
from pydantic import ValidationError

from domain.models.agent import AgentContractLocationResponse


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def agent_contract_location_dict():
    """
    Standard snake_case payload matching AgentContractLocationResponse.
    """
    return {
        "contract_id": "CONT-1001",
        "award_number": "AWD-1001",
        "order_number": "ORD-1001",
        "mod_number": "MOD-01",
        "places": "Dallas, TX",
        "project_name": "Test Project",
        "program_manager_name": "Test Manager",
        "status": "ACTIVE",
    }


# =============================================================================
# Basic model tests
# =============================================================================


def test_agent_contract_location_response_success(
    agent_contract_location_dict,
):
    """
    Verify the model can be created using snake_case field names.
    """

    result = AgentContractLocationResponse(
        **agent_contract_location_dict
    )

    assert result.contract_id == "CONT-1001"
    assert result.award_number == "AWD-1001"
    assert result.order_number == "ORD-1001"
    assert result.mod_number == "MOD-01"
    assert result.places == "Dallas, TX"
    assert result.project_name == "Test Project"
    assert result.program_manager_name == "Test Manager"
    assert result.status == "ACTIVE"


def test_agent_contract_location_required_contract_id():
    """
    contract_id is required.
    """

    with pytest.raises(ValidationError):
        AgentContractLocationResponse(
            award_number="AWD-1001",
            order_number="ORD-1001",
            mod_number="MOD-01",
            places="Dallas, TX",
            project_name="Test Project",
            program_manager_name="Test Manager",
            status="ACTIVE",
        )


def test_agent_contract_location_optional_fields():
    """
    All fields other than contract_id are optional.
    """

    result = AgentContractLocationResponse(
        contract_id="CONT-1001"
    )

    assert result.contract_id == "CONT-1001"

    assert result.award_number is None
    assert result.order_number is None
    assert result.mod_number is None
    assert result.places is None
    assert result.project_name is None
    assert result.program_manager_name is None
    assert result.status is None


# =============================================================================
# Alias tests
# =============================================================================


def test_contract_id_camel_case_alias():
    """
    Verify contractId is accepted.
    """

    result = AgentContractLocationResponse(
        contractId="CONT-1001"
    )

    assert result.contract_id == "CONT-1001"


def test_contract_id_uppercase_alias():
    """
    Verify CONTRACT_ID is accepted.
    """

    result = AgentContractLocationResponse(
        CONTRACT_ID="CONT-1001"
    )

    assert result.contract_id == "CONT-1001"


def test_award_number_camel_case_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        awardNumber="AWD-1001",
    )

    assert result.award_number == "AWD-1001"


def test_award_number_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        AWARD_NUMBER="AWD-1001",
    )

    assert result.award_number == "AWD-1001"


def test_order_number_camel_case_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        orderNumber="ORD-1001",
    )

    assert result.order_number == "ORD-1001"


def test_order_number_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        ORDER_NUMBER="ORD-1001",
    )

    assert result.order_number == "ORD-1001"


def test_mod_number_camel_case_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        modNumber="MOD-01",
    )

    assert result.mod_number == "MOD-01"


def test_mod_number_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        MOD_NUMBER="MOD-01",
    )

    assert result.mod_number == "MOD-01"


def test_places_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        PLACES="Dallas, TX",
    )

    assert result.places == "Dallas, TX"


def test_project_name_camel_case_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        projectName="Test Project",
    )

    assert result.project_name == "Test Project"


def test_project_name_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        PROJECT_NAME="Test Project",
    )

    assert result.project_name == "Test Project"


def test_program_manager_name_camel_case_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        programManagerName="Test Manager",
    )

    assert result.program_manager_name == "Test Manager"


def test_program_manager_name_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        PROGRAM_MANAGER_NAME="Test Manager",
    )

    assert result.program_manager_name == "Test Manager"


def test_status_uppercase_alias():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        STATUS="ACTIVE",
    )

    assert result.status == "ACTIVE"


# =============================================================================
# Complete database-style payload
# =============================================================================


def test_agent_contract_location_from_database_columns():
    """
    Verify a payload using database-style uppercase columns
    is converted correctly.
    """

    payload = {
        "CONTRACT_ID": "CONT-1001",
        "AWARD_NUMBER": "AWD-1001",
        "ORDER_NUMBER": "ORD-1001",
        "MOD_NUMBER": "MOD-01",
        "PLACES": "Dallas, TX",
        "PROJECT_NAME": "Test Project",
        "PROGRAM_MANAGER_NAME": "Test Manager",
        "STATUS": "ACTIVE",
    }

    result = AgentContractLocationResponse(**payload)

    assert result.contract_id == "CONT-1001"
    assert result.award_number == "AWD-1001"
    assert result.order_number == "ORD-1001"
    assert result.mod_number == "MOD-01"
    assert result.places == "Dallas, TX"
    assert result.project_name == "Test Project"
    assert result.program_manager_name == "Test Manager"
    assert result.status == "ACTIVE"


# =============================================================================
# Complete API-style payload
# =============================================================================


def test_agent_contract_location_from_api_aliases():
    """
    Verify camelCase API field aliases.
    """

    payload = {
        "contractId": "CONT-1001",
        "awardNumber": "AWD-1001",
        "orderNumber": "ORD-1001",
        "modNumber": "MOD-01",
        "places": "Dallas, TX",
        "projectName": "Test Project",
        "programManagerName": "Test Manager",
        "status": "ACTIVE",
    }

    result = AgentContractLocationResponse(**payload)

    assert result.contract_id == "CONT-1001"
    assert result.award_number == "AWD-1001"
    assert result.order_number == "ORD-1001"
    assert result.mod_number == "MOD-01"
    assert result.places == "Dallas, TX"
    assert result.project_name == "Test Project"
    assert result.program_manager_name == "Test Manager"
    assert result.status == "ACTIVE"


# =============================================================================
# Serialization
# =============================================================================


def test_agent_contract_location_model_dump(
    agent_contract_location_dict,
):
    """
    Verify normal model serialization.
    """

    model = AgentContractLocationResponse(
        **agent_contract_location_dict
    )

    result = model.model_dump()

    assert result["contract_id"] == "CONT-1001"
    assert result["award_number"] == "AWD-1001"
    assert result["order_number"] == "ORD-1001"
    assert result["mod_number"] == "MOD-01"
    assert result["places"] == "Dallas, TX"
    assert result["project_name"] == "Test Project"
    assert result["program_manager_name"] == "Test Manager"
    assert result["status"] == "ACTIVE"


def test_agent_contract_location_model_dump_by_alias(
    agent_contract_location_dict,
):
    """
    Verify response serialization uses the configured aliases.
    """

    model = AgentContractLocationResponse(
        **agent_contract_location_dict
    )

    result = model.model_dump(by_alias=True)

    assert result["contractId"] == "CONT-1001"
    assert result["awardNumber"] == "AWD-1001"
    assert result["orderNumber"] == "ORD-1001"
    assert result["modNumber"] == "MOD-01"
    assert result["places"] == "Dallas, TX"
    assert result["projectName"] == "Test Project"
    assert result["programManagerName"] == "Test Manager"
    assert result["status"] == "ACTIVE"


# =============================================================================
# None handling
# =============================================================================


def test_agent_contract_location_accepts_none_optional_values():
    result = AgentContractLocationResponse(
        contract_id="CONT-1001",
        award_number=None,
        order_number=None,
        mod_number=None,
        places=None,
        project_name=None,
        program_manager_name=None,
        status=None,
    )

    assert result.contract_id == "CONT-1001"
    assert result.award_number is None
    assert result.order_number is None
    assert result.mod_number is None
    assert result.places is None
    assert result.project_name is None
    assert result.program_manager_name is None
    assert result.status is None
