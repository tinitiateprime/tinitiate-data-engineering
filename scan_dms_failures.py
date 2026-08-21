# ============================================================
# api_test_config.py
# Manager-approved contract tests are the behavioral baseline.
#
# Add new APIs here. API-specific differences belong in config.
# ============================================================

from pathlib import Path

API_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(r"C:\code\mt-dm-gsapdi-lambda-1")

MAIN_FUNCTION_ROOT = PROJECT_ROOT / "main-function"
SOURCE_ROOT = MAIN_FUNCTION_ROOT / "mt-dm-lambda-src"
TEST_ROOT = MAIN_FUNCTION_ROOT / "tests" / "unit"

DESTINATION_DIRS = {
    "db": TEST_ROOT / "db",
    "model": TEST_ROOT / "domain" / "models",
    "service": TEST_ROOT / "domain" / "services",
    "handler": TEST_ROOT / "v1",
}

TEST_TYPES = ("db", "model", "service", "handler")


APIS = {
    # ========================================================
    # AGENT
    # ========================================================
    "agent": {
        "module_name": "agent",
        "repo_module": "agent_repo",
        "service_module": "agent_service",
        "handler_module": "agent",

        "repo_search_function": "get_work_locations_by_contract_id",
        "repo_key_function": None,

        "service_search_function": "agent_get_contract_locations",
        "service_key_function": None,

        "handler_search_function": "get_agent_contract_locations_v1",
        "handler_key_function": None,

        "response_model": "V1AgentContractLocationResponse",
        "search_response_model": "AgentContractServiceResponse",

        "key_column": "contract_id",
        "key_argument": "contract_id",
        "handler_path_parameter": "contractId",
        "sample_key": "600908",

        "search_requires_key": True,

        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,

        "repo_search_parameters": [
            "contract_id",
            "filters",
            "page",
            "columns",
            "sort",
        ],

        "service_search_parameters": [
            "contract_id",
            "filters",
            "limit",
            "cursor",
            "columns",
            "sort",
        ],

        "handler_service_parameters": [
            "contract_id",
            "filters",
            "columns",
            "limit",
            "cursor",
        ],

        "repo_execute_query_passes_limit": False,

        "sample_field": "worklocation",
        "sample_value": "Location A",

        "response_key_field": "contract_id",
        "response_assert_fields": ["contract_id"],

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Contract ID is required.",

        "handler_inner_schema": "V1AgentResponseModel",
        "handler_outer_schema": "V1AgentListResponseModel",
    },

    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================
    "po_funding_detail": {
        "module_name": "po_funding_detail",
        "repo_module": "po_funding_detail_repo",
        "service_module": "po_funding_detail_service",
        "handler_module": "po_funding_detail",

        "repo_search_function": "get_po_funding_detail",
        "repo_key_function": None,

        "service_search_function": "search_po_funding_detail",
        "service_key_function": None,

        "handler_search_function": "search_po_funding_detail_v1",
        "handler_key_function": None,

        "response_model": "PoFundingDetailResponse",
        "search_response_model": "PoFundingDetailSearchServiceResponse",

        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": None,
        "sample_key": "P-1001",

        "search_requires_key": False,

        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": False,
        "supports_handler_key_lookup": False,

        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_execute_query_passes_limit": True,

        "sample_field": "proj_name",
        "sample_value": "Test Project",

        "response_key_field": "po_id",
        "response_assert_fields": ["po_id"],
    },

    # ========================================================
    # GL DETAILS
    # ========================================================
    "gl_details": {
        "module_name": "gl_details",
        "repo_module": "gl_details_repo",
        "service_module": "gl_details_service",
        "handler_module": "gl_details",

        "repo_search_function": "get_gl_details",
        "repo_key_function": "get_gl_details_by_project_id",

        "service_search_function": "search_gl_details",
        "service_key_function": "get_gl_details_by_project",

        "handler_search_function": "search_gl_details_v1",
        "handler_key_function": "get_gl_details_v1",

        "response_model": "GlDetailsResponse",
        "search_response_model": "GlDetailsSearchServiceResponse",

        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": "proj_id",
        "sample_key": "P-1001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_key_service_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        "repo_execute_query_passes_limit": True,

        "repo_cursor_fields": [
            "PROJ_ID",
            "VCHR_NO",
        ],
        "repo_cursor_values": [
            "P-1001",
            "test_vchr_no",
        ],
        "repo_cursor_separator": "_",

        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        "sample_field": "name",
        "sample_value": "Test Project",

        "response_key_field": "proj_id",
        "response_assert_fields": ["proj_id"],

        "handler_inner_schema": "V1GlDetailsResponseModel",
        "handler_outer_schema": "V1GlDetailsListResponseModel",
        "handler_detail_outer_schema": "V1GlDetailsListResponseModel",

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",

        "handler_detail_route": "/v1/financials/gl-details/{proj_id}",
        "handler_search_route": "/v1/financials/gl-details/search",
    },

    # ========================================================
    # FINANCIALS UPDATED
    # ========================================================
    "financials_updated": {
        "module_name": "financials_updated",
        "repo_module": "financials_updated_repo",
        "service_module": "financials_updated_service",
        "handler_module": "financials_updated",

        "repo_search_function": "get_financials_updated",
        "repo_key_function": "get_financials_updated_by_id",

        "service_search_function": "search_financials_updated",
        "service_key_function": "get_financials_updated_by_id",

        "handler_search_function": "search_financials_updated_v1",
        "handler_key_function": "get_financials_updated_v1",

        "response_model": "FinancialsUpdatedResponse",
        "search_response_model": "FinancialsUpdatedSearchServiceResponse",

        "key_column": "id",
        "key_argument": "id_",
        "handler_path_parameter": "id",
        "sample_key": "TEST-ID-001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,
        "supports_list_handler": False,

        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_key_parameters": [
            "id_",
            "page",
            "sort",
            "columns",
        ],

        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [
            "id_",
            "page",
            "sort",
            "columns",
        ],

        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_key_service_parameters": [
            "id_",
            "page",
            "sort",
            "columns",
        ],

        "repo_execute_query_passes_limit": True,

        "repo_cursor_fields": [
            "id",
            "clin",
        ],
        "repo_cursor_values": [
            "TEST-ID-001",
            "TEST-CLIN",
        ],
        "repo_cursor_separator": "_",

        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        "sample_field": "clin",
        "sample_value": "TEST-CLIN",

        "response_key_field": "id",
        "response_assert_fields": [
            "id",
            "clin",
        ],

        "sample_data": {
            "lvl": "1",
            "id": "TEST-ID-001",
            "clin": "TEST-CLIN",
            "ceiling": 1000.0,
            "funding": 800.0,
            "ltd": 500.0,
            "etc": 300.0,
            "eac": 800.0,
            "date_75": "2026-01-01",
            "date_100": "2026-06-01",
        },

        "handler_inner_schema": "V1FinancialsUpdatedResponseModel",
        "handler_outer_schema": "V1FinancialsUpdatedListResponseModel",

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project/task-order ID is required.",

        "handler_detail_route": "/v1/financials/funding-forecast/{id}",
        "handler_search_route": "/v1/financials/funding-forecast/search",
    },

    # ========================================================
    # EMPLOYEE PROFILE COMPLETE
    # ========================================================
    "employee_profile_complete": {
        "module_name": "employee_profile_complete",
        "repo_module": "employee_profile_complete_repo",
        "service_module": "employee_profile_complete_service",
        "handler_module": "employee_profile_complete",

        "repo_search_function": "get_employee_profile_completes",
        "repo_key_function": "get_employee_profile_complete_by_id",

        "service_search_function": "search_employee_profile_completes",
        "service_key_function": "get_employee_profile_complete_details",

        "handler_search_function": "search_employee_profile_completes_v1",
        "handler_list_function": "list_employee_profile_completes_v1",
        "handler_key_function": "get_employee_profile_complete_v1",

        "response_model": "EmployeeProfileCompleteResponse",
        "search_response_model": "EmployeeProfileCompleteSearchServiceResponse",

        "key_column": "employee_key",
        "key_argument": "employee_key",
        "handler_path_parameter": "employee_key",
        "sample_key": "EMPR-1001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        "supports_search": True,
        "supports_list": True,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "repo_key_parameters": [
            "employee_key",
            "filters",
            "page",
            "columns",
            "sort",
        ],

        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "service_key_parameters": [
            "employee_key",
            "filters",
            "limit",
            "cursor",
            "columns",
            "sort",
        ],

        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        "handler_key_service_parameters": [
            "employee_key",
            "filters",
            "limit",
            "cursor",
            "columns",
        ],

        "handler_list_service_parameters": [
            "filters",
            "page",
        ],

        "repo_execute_query_passes_limit": True,

        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "limit_cursor",

        "sample_field": "employee_name",
        "sample_value": "Test Employee",

        "response_key_field": "employee_key",
        "response_assert_fields": ["employee_key"],

        "handler_inner_schema": "V1EmployeeProfileCompleteResponseModel",
        "handler_outer_schema": "V1EmployeeProfileCompleteListResponseModel",
        "handler_detail_outer_schema": "V1EmployeeProfileCompleteDetailResponseModel",

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "EmployeeProfileComplete ID is required.",

        "handler_detail_route": "/v1/employee-profile-complete/{employee_key}",
        "handler_search_route": "/v1/employee-profile-complete/search",
        "handler_list_route": "/v1/employee-profile-complete",
    },
}


def get_api_config(api_name: str) -> dict:
    if api_name not in APIS:
        available = ", ".join(sorted(APIS))
        raise KeyError(
            f"Unknown API '{api_name}'. "
            f"Available APIs: {available}"
        )

    return dict(APIS[api_name])


def get_destination_dir(test_type: str) -> Path:
    if test_type not in DESTINATION_DIRS:
        raise KeyError(
            f"Unknown test type: {test_type}"
        )

    return DESTINATION_DIRS[test_type]


def validate_config() -> None:
    required = {
        "module_name",
        "repo_module",
        "service_module",
        "handler_module",
        "repo_search_function",
        "service_search_function",
        "handler_search_function",
        "response_model",
        "search_response_model",
        "key_column",
        "key_argument",
        "repo_search_parameters",
        "service_search_parameters",
        "handler_service_parameters",
    }

    errors = []

    for api_name, cfg in APIS.items():
        for field in sorted(required - set(cfg)):
            errors.append(
                f"{api_name}: missing '{field}'"
            )

        if cfg.get("supports_key_lookup"):
            if not cfg.get("repo_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but repo_key_function is missing"
                )

            if not cfg.get("service_key_function"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but service_key_function is missing"
                )

            if not cfg.get("repo_key_parameters"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but repo_key_parameters is missing"
                )

            if not cfg.get("service_key_parameters"):
                errors.append(
                    f"{api_name}: supports_key_lookup=True "
                    "but service_key_parameters is missing"
                )

        if cfg.get("supports_handler_key_lookup"):
            if not cfg.get("handler_key_function"):
                errors.append(
                    f"{api_name}: supports_handler_key_lookup=True "
                    "but handler_key_function is missing"
                )

            if not cfg.get("handler_key_service_parameters"):
                errors.append(
                    f"{api_name}: supports_handler_key_lookup=True "
                    "but handler_key_service_parameters is missing"
                )

        if cfg.get("search_requires_key") and not cfg.get("key_argument"):
            errors.append(
                f"{api_name}: search_requires_key=True "
                "but key_argument is missing"
            )

    if errors:
        raise ValueError(
            "Invalid api_test_config.py:\n"
            + "\n".join(errors)
        )


if __name__ == "__main__":
    validate_config()

    print()
    print("=" * 80)
    print("API TEST CONFIGURATION")
    print("=" * 80)

    for api_name, cfg in APIS.items():
        print(
            f"{api_name:<30} "
            f"search={cfg['repo_search_function']:<40} "
            f"key_lookup={cfg.get('supports_key_lookup', False)}"
        )

    print()
    print("Configuration OK")
