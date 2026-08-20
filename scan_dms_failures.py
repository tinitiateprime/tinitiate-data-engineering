# ============================================================
# api_test_config.py
# Manager-approved Contract tests are the behavioral baseline.
#
# Add new APIs here. API-specific differences belong in config.
# ============================================================

from pathlib import Path

# Folder containing api_test_config.py and generate_api_tests.py
API_ROOT = Path(__file__).resolve().parent

# Actual Git repository containing the production main-function source.
# Change only this line if the repository is cloned to a different folder.
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

        "response_model": "AgentContractLocationResponse",
        "search_response_model": "AgentContractServiceResponse",

        "key_column": "contract_id",
        "key_argument": "contract_id",
        "handler_path_parameter": "contractId",
        "sample_key": "609998",

        "search_requires_key": True,

        "supports_search": True,
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
        "repo_key_function": None,

        "service_search_function": "search_gl_details",
        "service_key_function": None,

        "handler_search_function": "search_gl_details_v1",
        "handler_key_function": None,

        "response_model": "GlDetailsResponse",
        "search_response_model": "GlDetailsSearchServiceResponse",

        # QuerySpec logical_id_field in gl_details_repo.py
        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": None,
        "sample_key": "P-1001",

        "search_requires_key": False,

        "supports_search": True,
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

        "sample_field": "name",
        "sample_value": "Test Project",

        "response_key_field": "proj_id",
        "response_assert_fields": ["proj_id"],
    },

    # ========================================================
    # EMPLOYEE PROFILE COMPLETE
    # ========================================================
    "employee_profile_complete": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "employee_profile_complete",
        "repo_module": "employee_profile_complete_repo",
        "service_module": "employee_profile_complete_service",
        "handler_module": "employee_profile_complete",

        # ----------------------------------------------------
        # Repository
        #
        # Actual functions from employee_profile_complete_repo.py:
        #
        # get_employee_profile_completes(
        #     filters=None,
        #     sort=None,
        #     page=None,
        #     columns=None,
        # )
        #
        # get_employee_profile_complete_by_id(
        #     employee_key,
        #     filters=None,
        #     page=None,
        #     columns=None,
        #     sort=None,
        # )
        # ----------------------------------------------------
        "repo_search_function": "get_employee_profile_completes",
        "repo_key_function": "get_employee_profile_complete_by_id",

        # ----------------------------------------------------
        # Service
        #
        # Actual functions from employee_profile_complete_service.py:
        #
        # search_employee_profile_completes(
        #     filters=None,
        #     sort=None,
        #     page=None,
        #     columns=None,
        # )
        #
        # get_employee_profile_complete_details(
        #     employee_key,
        #     filters=None,
        #     limit=settings.DEFAULT_PAGE_SIZE,
        #     cursor=None,
        #     columns=None,
        #     sort=None,
        # )
        # ----------------------------------------------------
        "service_search_function": "search_employee_profile_completes",
        "service_key_function": "get_employee_profile_complete_details",

        # ----------------------------------------------------
        # Handler
        #
        # Actual handlers:
        #
        # GET /v1/employee-profile-complete/{employee_key}
        #     get_employee_profile_complete_v1
        #
        # POST /v1/employee-profile-complete/search
        #     search_employee_profile_completes_v1
        #
        # GET /v1/employee-profile-complete
        #     list_employee_profile_completes_v1
        # ----------------------------------------------------
        "handler_search_function": "search_employee_profile_completes_v1",
        "handler_list_function": "list_employee_profile_completes_v1",
        "handler_key_function": "get_employee_profile_complete_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "EmployeeProfileCompleteResponse",
        "search_response_model": (
            "EmployeeProfileCompleteSearchServiceResponse"
        ),

        # ----------------------------------------------------
        # Key
        #
        # Repository QuerySpec:
        # logical_id_field = "employee_key"
        # ----------------------------------------------------
        "key_column": "employee_key",
        "key_argument": "employee_key",
        "handler_path_parameter": "employee_key",
        "sample_key": "EMP-1001",

        # Search endpoint itself does NOT require employee_key.
        # Detail endpoint DOES require employee_key.
        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": True,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        # ----------------------------------------------------
        # Repository function signatures
        # ----------------------------------------------------
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

        # ----------------------------------------------------
        # Service function signatures
        # ----------------------------------------------------
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

        # ----------------------------------------------------
        # Handler -> service signatures
        # ----------------------------------------------------
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

        # ----------------------------------------------------
        # Pagination / DB execution
        #
        # Repository calls:
        # execute_query(plan.sql, plan.params, limit=current_page.limit)
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "limit_cursor",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "employee_name",
        "sample_value": "Test Employee",

        "response_key_field": "employee_key",
        "response_assert_fields": ["employee_key"],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": (
            "V1EmployeeProfileCompleteResponseModel"
        ),
        "handler_outer_schema": (
            "V1EmployeeProfileCompleteListResponseModel"
        ),
        "handler_detail_outer_schema": (
            "V1EmployeeProfileCompleteDetailResponseModel"
        ),

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": (
            "EmployeeProfileComplete ID is required."
        ),

        "handler_detail_route": (
            "/v1/employee-profile-complete/{employee_key}"
        ),
        "handler_search_route": (
            "/v1/employee-profile-complete/search"
        ),
        "handler_list_route": (
            "/v1/employee-profile-complete"
        ),
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
        "sample_key",
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
                    f"{api_name}: "
                    "supports_handler_key_lookup=True "
                    "but handler_key_function is missing"
                )

            if not cfg.get(
                "handler_key_service_parameters"
            ):
                errors.append(
                    f"{api_name}: "
                    "supports_handler_key_lookup=True "
                    "but handler_key_service_parameters "
                    "is missing"
                )

        if (
            cfg.get("search_requires_key")
            and not cfg.get("key_argument")
        ):
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
