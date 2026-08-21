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
    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================
    "po_funding_detail": {
    # ----------------------------------------------------
    # Modules
    # ----------------------------------------------------
    "module_name": "po_funding_detail",
    "repo_module": "po_funding_detail_repo",
    "service_module": "po_funding_detail_service",
    "handler_module": "po_funding_detail",

    # ----------------------------------------------------
    # Repository
    # ----------------------------------------------------
    "repo_search_function": "get_po_funding_detail",
    "repo_key_function": None,

    # ----------------------------------------------------
    # Service
    # ----------------------------------------------------
    "service_search_function": "search_po_funding_detail",
    "service_key_function": None,

    # ----------------------------------------------------
    # Handler
    # ----------------------------------------------------
    "handler_search_function": "search_po_funding_detail_v1",
    "handler_key_function": None,
    "handler_list_function": None,

    # ----------------------------------------------------
    # Domain models
    # ----------------------------------------------------
    "response_model": "PoFundingDetailResponse",
    "search_response_model": "PoFundingDetailSearchServiceResponse",

    # ----------------------------------------------------
    # Key configuration
    #
    # QuerySpec logical_id_field = "proj_id"
    # ----------------------------------------------------
    "key_column": "proj_id",
    "key_argument": "proj_id",
    "handler_path_parameter": None,
    "sample_key": "P-1001",

    # Search does NOT require proj_id
    "search_requires_key": False,

    # ----------------------------------------------------
    # Supported operations
    # ----------------------------------------------------
    "supports_search": True,
    "supports_list": False,
    "supports_key_lookup": False,
    "supports_handler_key_lookup": False,

    # ----------------------------------------------------
    # Repository function signature
    #
    # get_po_funding_detail(
    #     filters,
    #     sort,
    #     page,
    #     columns,
    # )
    # ----------------------------------------------------
    "repo_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # No repository key function
    "repo_key_parameters": [],

    # ----------------------------------------------------
    # Service function signature
    #
    # search_po_funding_detail(
    #     filters,
    #     sort,
    #     page,
    #     columns,
    # )
    # ----------------------------------------------------
    "service_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # No service key function
    "service_key_parameters": [],

    # ----------------------------------------------------
    # Handler -> service parameters
    #
    # search_po_funding_detail_v1 calls:
    # search_po_funding_detail(
    #     filters=...,
    #     sort=...,
    #     page=...,
    #     columns=...,
    # )
    # ----------------------------------------------------
    "handler_service_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    "handler_key_service_parameters": [],

    # ----------------------------------------------------
    # Repository execute_query behavior
    # ----------------------------------------------------
    "repo_execute_query_passes_limit": True,

    # ----------------------------------------------------
    # Pagination / cursor
    #
    # IMPORTANT:
    # _format_paginated_response() builds the cursor from:
    #
    #     po_id
    #     proj_id
    #
    # This MUST match the actual repository implementation.
    # ----------------------------------------------------
    "repo_cursor_fields": [
        "po_id",
        "po_line_id",
    ],

    "repo_cursor_values": [
        "P-1001",
         1,
    ],

    "repo_cursor_separator": "_",

    # ----------------------------------------------------
    # Pagination modes
    # ----------------------------------------------------
    "repo_pagination_mode": "page",
    "service_search_pagination_mode": "page",
    "service_key_pagination_mode": "page",

    # ----------------------------------------------------
    # Sample model data
    # ----------------------------------------------------
    "sample_field": "proj_name",
    "sample_value": "Test Project",

    # ----------------------------------------------------
    # Response assertions
    # ----------------------------------------------------
    "response_key_field": "po_id",
    "response_assert_fields": [
        "po_id",
    ],
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

    # Cursor / pagination configuration
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
    "response_assert_fields": [
        "proj_id",
    ],
    },


    # ========================================================
    # FINANCIALS UPDATED
    # ========================================================
    "financials_updated": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "financials_updated",
        "repo_module": "financials_updated_repo",
        "service_module": "financials_updated_service",
        "handler_module": "financials_updated",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_financials_updated",
        "repo_key_function": "get_financials_updated_by_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_financials_updated",
        "service_key_function": "get_financials_updated_by_id",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_financials_updated_v1",
        "handler_key_function": "get_financials_updated_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "FinancialsUpdatedResponse",
        "search_response_model": "FinancialsUpdatedSearchServiceResponse",

        # ----------------------------------------------------
        # Key configuration
        # ----------------------------------------------------
        "key_column": "id",
        "key_argument": "id_",
        "handler_path_parameter": "id",
        "sample_key": "TEST-ID-001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": False,
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
            "id_",
            "page",
            "sort",
            "columns",
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
            "id_",
            "page",
            "sort",
            "columns",
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
            "id_",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Pagination / DB execution
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # financials_updated_repo builds the cursor from BOTH id and clin:
        # f"{last_item.get('id')}_{last_item.get('clin')}"
        "repo_cursor_fields": [
            "id",
            "clin",
        ],
        "repo_cursor_values": [
            "TEST-ID-001",
            "TEST-CLIN",
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "clin",
        "sample_value": "TEST-CLIN",
        "sample_data": {
            "lvl": "1",
            "id": "TEST-ID-001",
            "clin": "TEST-CLIN",
            "ceiling": 1000.0,
            "funding": 800.0,
            "ltd": 300.0,
            "etc": 500.0,
            "eac": 800.0,
            "date_75": "2026-01-01",
            "date_100": "2026-06-01",
        },
        "response_key_field": "id",
        "response_assert_fields": [
            "id",
            "clin",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1FinancialsUpdatedResponseModel",
        "handler_outer_schema": "V1FinancialsUpdatedListResponseModel",
        "handler_detail_outer_schema": "V1FinancialsUpdatedListResponseModel",

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
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
    # ========================================================
    # PROJECT INFO
    # ========================================================
    "project_info": {
        "module_name": "project_info",
        "repo_module": "project_info_repo",
        "service_module": "project_info_service",
        "handler_module": "project_info",

        "repo_search_function": "get_project_info",
        "repo_key_function": "get_project_info_by_id",

        "service_search_function": "search_project_info",
        "service_key_function": "get_project_info_details",

        "handler_search_function": "search_project_info_v1",
        "handler_key_function": "get_project_info_v1",
        "handler_list_function": None,

        "response_model": "ProjectInfoResponse",
        "search_response_model": "ProjectInfoSearchServiceResponse",

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
            "columns",
        ],

        # project_info_repo calls execute_query(..., limit=current_page.limit)
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        "repo_cursor_fields": ["proj_id"],
        "repo_cursor_values": ["P-1001"],
        "repo_cursor_separator": "_",

        "sample_field": "proj_name",
        "sample_value": "Test Project",
        "response_key_field": "proj_id",
        "response_assert_fields": ["proj_id"],

        # Exact schemas imported and used by v1.handlers.project_info
        "handler_inner_schema": "V1ProjectInfoResponseModel",
        "handler_outer_schema": "V1ProjectInfoListResponseModel",
        "handler_detail_outer_schema": "V1ProjectInfoListResponseModel",

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",

        "handler_detail_route": "/v1/projects/info/{proj_id}",
        "handler_search_route": "/v1/projects/info/search",
    },

    # ========================================================
    # PROJECT MODIFICATIONS
    # ========================================================
    "project_modifications": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "project_modifications",
        "repo_module": "project_modifications_repo",
        "service_module": "project_modifications_service",
        "handler_module": "project_modifications",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_project_modifications",
        "repo_key_function": "get_project_modifications_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_project_modifications",
        "service_key_function": "get_project_modifications_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_project_modifications_v1",
        "handler_key_function": "get_project_modifications_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "ProjectModificationResponse",
        "search_response_model": "ProjectModificationSearchServiceResponse",

        # ----------------------------------------------------
        # Key
        # ----------------------------------------------------
        "key_column": "proj_id",
        "key_argument": "proj_id",
        "handler_path_parameter": "proj_id",
        "sample_key": "P-1001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": False,
        "supports_key_lookup": True,
        "supports_handler_key_lookup": True,

        # ----------------------------------------------------
        # Repository search
        # get_project_modifications(filters, sort, page, columns)
        # ----------------------------------------------------
        "repo_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        # ----------------------------------------------------
        # Repository key lookup
        # get_project_modifications_by_project_id(
        #     proj_id, page, sort, columns
        # )
        # ----------------------------------------------------
        "repo_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Service search
        # search_project_modifications(filters, sort, page, columns)
        # ----------------------------------------------------
        "service_search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        # ----------------------------------------------------
        # Service key lookup
        # get_project_modifications_by_project(
        #     proj_id, page, sort, columns
        # )
        # ----------------------------------------------------
        "service_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Handler -> service (search)
        # ----------------------------------------------------
        "handler_service_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],

        # ----------------------------------------------------
        # Handler -> service (detail)
        # ----------------------------------------------------
        "handler_key_service_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # DB execution / pagination
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # ----------------------------------------------------
        # Composite cursor
        # _format_paginated_response() uses:
        #     PROJ_ID + "_" + PROJ_MOD_ID
        # ----------------------------------------------------
        "repo_cursor_fields": [
            "PROJ_ID",
            "PROJ_MOD_ID",
        ],
        "repo_cursor_values": [
            "P-1001",
            "PM-001",
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "proj_mod_desc",
        "sample_value": "Test Project Modification",
        "response_key_field": "proj_id",
        "response_assert_fields": [
            "proj_id",
            "proj_mod_id",
        ],

        # ----------------------------------------------------
        # Handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ProjectModificationResponseModel",
        "handler_outer_schema": "V1ProjectModificationListResponseModel",
        "handler_detail_outer_schema": "V1ProjectModificationListResponseModel",

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",
        "handler_detail_route": "/v1/projects/modifications/{proj_id}",
        "handler_search_route": "/v1/projects/modifications/search",
    },


    # ========================================================
    # PROJECT STATUS DETAIL
    # ========================================================
    "project_status_detail": {
        "module_name": "project_status_detail",
        "repo_module": "project_status_detail_repo",
        "service_module": "project_status_detail_service",
        "handler_module": "project_status_detail",

        "repo_search_function": "get_project_status_detail",
        "repo_key_function": "get_project_status_detail_by_project_level",

        "service_search_function": "search_project_status_detail",
        "service_key_function": "get_project_status_detail_by_project",

        "handler_search_function": "search_project_status_detail_v1",
        "handler_key_function": "get_project_status_detail_v1",
        "handler_list_function": None,

        "response_model": "ProjectStatusDetailResponse",
        "search_response_model": "ProjectStatusDetailSearchServiceResponse",

        "key_column": "project_level",
        "key_argument": "project_level",
        "handler_path_parameter": "project_level",
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
            "project_level",
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
            "project_level",
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
            "project_level",
            "page",
            "sort",
            "columns",
        ],

        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        "repo_cursor_fields": [
            "project_level",
            "period",
        ],
        "repo_cursor_values": [
            "P-1001",
            1,
        ],
        "repo_cursor_separator": "|",

        "sample_field": "project_name",
        "sample_value": "Test Project",

        "response_key_field": "project_level",
        "response_assert_fields": [
            "project_level",
        ],

        "handler_inner_schema": "V1ProjectStatusDetailResponseModel",
        "handler_outer_schema": "V1ProjectStatusDetailListResponseModel",
        "handler_detail_outer_schema": "V1ProjectStatusDetailListResponseModel",

        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",

        "handler_detail_route": "/v1/projects/status-detail/{project_level}",
        "handler_search_route": "/v1/projects/status-detail/search",
    },


    # ========================================================
    # NON LABOR DETAIL
    # ========================================================
    "non_labor_detail": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "non_labor_detail",
        "repo_module": "non_labor_detail_repo",
        "service_module": "non_labor_detail_service",
        "handler_module": "non_labor_detail",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_non_labor_detail",
        "repo_key_function": "get_non_labor_detail_by_project_rollup",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_non_labor_detail",
        "service_key_function": "get_non_labor_detail_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_non_labor_detail_v1",
        "handler_key_function": "get_non_labor_detail_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "NonLaborDetailResponse",
        "search_response_model": "NonLaborDetailSearchServiceResponse",

        # ----------------------------------------------------
        # Key
        # QuerySpec logical_id_field = "project_rollup"
        # ----------------------------------------------------
        "key_column": "project_rollup",
        "key_argument": "project_rollup",
        "handler_path_parameter": "project_rollup",
        "sample_key": "P-1001",

        "search_requires_key": False,
        "key_lookup_requires_key": True,

        # ----------------------------------------------------
        # Supported operations
        # ----------------------------------------------------
        "supports_search": True,
        "supports_list": False,
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
            "project_rollup",
            "page",
            "sort",
            "columns",
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
            "project_rollup",
            "page",
            "sort",
            "columns",
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
            "project_rollup",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Pagination / DB execution
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # Repository cursor:
        # f"{last_item.get('project_rollup')}_{last_item.get('invoice_id')}"
        "repo_cursor_fields": [
            "project_rollup",
            "invoice_id",
        ],
        "repo_cursor_values": [
            "P-1001",
            "INV-001",
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "account_name",
        "sample_value": "Test Account",
        "sample_data": {
            "project_rollup": "P-1001",
            "account_id": "ACCT-001",
            "period": 1,
            "po_number": "PO-001",
            "vchr_no_je_no_cr_no": "VCHR-001",
            "invoice_id": "INV-001",
            "item_id": "ITEM-001",
            "item_desc": "Test Non Labor Item",
            "account_name": "Test Account",
            "id_jnl_code": "JNL-001",
            "name_cr_je": "Test CR JE",
            "transaction_desc": "Test Transaction",
            "prog_portfolio": "Test Portfolio",
            "amount_for_report": 100.0,
            "project_manager_name_validated": "Test Manager",
            "total_amount_all": 100.0,
            "total_amount_by_project": 100.0,
            "total_amount_by_project_account": 100.0,
            "total_amount_by_project_account_period": 100.0,
        },

        "response_key_field": "project_rollup",
        "response_assert_fields": [
            "project_rollup",
            "invoice_id",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1NonLaborDetailResponseModel",
        "handler_outer_schema": "V1NonLaborDetailListResponseModel",
        "handler_detail_outer_schema": "V1NonLaborDetailListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project rollup ID is required.",
        "handler_detail_route": "/v1/financials/non-labor/{project_rollup}",
        "handler_search_route": "/v1/financials/non-labor/search",
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
