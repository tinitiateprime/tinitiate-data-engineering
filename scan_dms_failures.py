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
        "repo_key_function": "get_po_funding_detail_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_po_funding_detail",
        "service_key_function": "get_po_funding_detail_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_po_funding_detail_v1",
        "handler_key_function": "get_po_funding_detail_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "PoFundingDetailResponse",
        "search_response_model": "PoFundingDetailSearchServiceResponse",

        # ----------------------------------------------------
        # Key configuration
        # ----------------------------------------------------
        "key_column": "project_id",
        "key_argument": "project_id",
        "handler_path_parameter": "project_id",
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
            "project_id",
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
            "project_id",
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
            "project_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Repository execute_query / pagination
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # Keep the existing cursor expectations used by the
        # generator until the repository cursor implementation
        # is confirmed directly from po_funding_detail_repo.py.
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
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "vendor_name",
        "sample_value": "Test Vendor",
        "sample_data": {
            "po_id": "PO-1001",
            "po_release_no": 1,
            "po_line_no": 1,
            "vendor_id": "VENDOR-001",
            "vendor_name": "Test Vendor",
            "order_date": "2026-01-15",
            "po_line_desc": "Test PO Line",
            "po_text": "Test PO Funding Detail",
            "ordered_qty": 10.0,
            "po_line_total_amt": 1000.0,
            "vouchered_amt": 250.0,
            "remaining": 750.0,
            "project_id": "P-1001",
            "min_po_line_total": 1000.0,
            "min_vouchered_amt": 250.0,
            "min_remaining": 750.0,
        },

        "response_key_field": "project_id",
        "response_assert_fields": [
            "project_id",
            "po_id",
            "po_line_no",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1PoFundingDetailResponseModel",
        "handler_outer_schema": "V1PoFundingDetailListResponseModel",
        "handler_detail_outer_schema": "V1PoFundingDetailListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",
        "handler_detail_route": "/v1/financials/po-funding/{project_id}",
        "handler_search_route": "/v1/financials/po-funding/search",
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


    # ========================================================
    # PERIOD TARGET COST REVENUE
    # ========================================================
    "period_target_cost_revenue": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "period_target_cost_revenue",
        "repo_module": "period_target_cost_revenue_repo",
        "service_module": "period_target_cost_revenue_service",
        "handler_module": "period_target_cost_revenue",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_period_target_cost_revenue",
        "repo_key_function": "get_period_target_cost_revenue_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_period_target_cost_revenue",
        "service_key_function": "get_period_target_cost_revenue_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_period_target_cost_revenue_v1",
        "handler_key_function": "get_period_target_cost_revenue_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "PeriodTargetCostRevenueResponse",
        "search_response_model": "PeriodTargetCostRevenueSearchServiceResponse",

        # ----------------------------------------------------
        # Key
        # QuerySpec logical_id_field = "proj_id"
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
        # Repository function signatures
        # ----------------------------------------------------
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
            "proj_id",
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
            "proj_id",
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
        # f"{last_item.get('PROJ_ID')}_{last_item.get('PD_NO')}"
        "repo_cursor_fields": [
            "PROJ_ID",
            "PD_NO",
        ],
        "repo_cursor_values": [
            "P-1001",
            1,
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "proj_name",
        "sample_value": "Test Project",
        "sample_data": {
            "PROJ_CLASS": "TEST",
            "LVL1": "1",
            "TGT/ACT": "TGT",
            "PROJ_ID": "P-1001",
            "proj_name": "Test Project",
            "company_id": "COMP-001",
            "PROJ_TYPE": "TEST",
            "REV_FORMULA": "REV",
            "BILL_FORMULA": "BILL",
            "BILL_PROJECT_ID": "BP-1001",
            "START_DT": "2026-01-01",
            "END_DT": "2026-12-31",
            "ACCT_ID": "ACCT-001",
            "acct_name": "Test Account",
            "ORG_ID": "ORG-001",
            "REORG_ID": "REORG-001",
            "L4_REORG_NAME": "Test Reorg",
            "FRG_POOL": "FRG",
            "OH_POOL": "OH",
            "MH_POOL": "MH",
            "GA_POOL": "GA",
            "GA_MH_POOL": "GA_MH",
            "LAB_NONLAB": "LAB",
            "FY_CD": "2026",
            "PD_NO": 1,
            "HOURS": 10.0,
            "LABOR_EXPENSE": 100.0,
            "FR": 1.0,
            "FR_RT": 0.1,
            "OH": 2.0,
            "OH_RT": 0.2,
            "GA_LAB": 3.0,
            "GA_RT": 0.3,
            "LABOR_BURDEN": 10.0,
            "LABOR_LOADED": 110.0,
            "LABOR_PROFIT": 5.0,
            "LABOR_REVENUE": 115.0,
            "ODC_EXPENSE": 50.0,
            "MH": 1.0,
            "MH_RT": 0.1,
            "GA_NONLAB": 2.0,
            "GA_RT_NONLAB": 0.2,
            "GA_MH_NONLAB": 3.0,
            "GA_MH_RT_NONLAB": 0.3,
            "ODC_BURDEN": 5.0,
            "ODC_LOADED": 55.0,
            "ODC_PROFIT": 2.5,
            "ODC_REVENUE": 57.5,
            "PD_TOTAL_COST": 165.0,
            "AWARD_FEE_TGT_AMT": 10.0,
            "FEEL_BURD_TGT_AMT": 1.0,
            "FEE_ON_DIR_AMT": 5.0,
            "FEE_ON_HRS_AMT": 2.0,
            "MARKUP_FEE_AMT": 1.0,
            "OTH_FEE_TGT_AMT": 1.0,
            "OVER_TGT_FEE_AMT": 1.0,
            "PD_TOTAL_PROFIT": 8.5,
            "PD_TOTAL_REVENUE": 172.5,
        },

        "response_key_field": "proj_id",
        "response_assert_fields": [
            "proj_id",
            "pd_no",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1PeriodTargetCostRevenueResponseModel",
        "handler_outer_schema": "V1PeriodTargetCostRevenueListResponseModel",
        "handler_detail_outer_schema": "V1PeriodTargetCostRevenueListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",
        "handler_detail_route": "/v1/financials/period-target-cost-revenue/{proj_id}",
        "handler_search_route": "/v1/financials/period-target-cost-revenue/search",
    },


    # ========================================================
    # PO OPEN COMMITMENT
    # ========================================================
    "po_open_commitment": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "po_open_commitment",
        "repo_module": "po_open_commitment_repo",
        "service_module": "po_open_commitment_service",
        "handler_module": "po_open_commitment",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_po_open_commitments",
        "repo_key_function": "get_po_open_commitments_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_po_open_commitments",
        "service_key_function": "get_po_open_commitments_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_po_open_commitments_v1",
        "handler_key_function": "get_po_open_commitments_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "PoOpenCommitmentResponse",
        "search_response_model": "PoOpenCommitmentSearchServiceResponse",

        # ----------------------------------------------------
        # Key
        #
        # The QuerySpec logical_id_field is po_number, but the
        # GET/detail API is keyed by project_id.
        # ----------------------------------------------------
        "key_column": "project_id",
        "key_argument": "project_id",
        "handler_path_parameter": "project_id",
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
            "project_id",
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
            "project_id",
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
            "project_id",
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

        # Repository cursor is built from:
        # po_number + "_" + line_number
        "repo_cursor_fields": [
            "po_number",
            "line_number",
        ],
        "repo_cursor_values": [
            "PO-10001",
            1,
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "project_name",
        "sample_value": "Test Project",
        "sample_data": {
            "project_id": "P-1001",
            "account_id": "ACCT-001",
            "organization_id": "ORG-001",
            "commitment_status_flag": "Y",
            "account_name": "Test Account",
            "day_difference": "10",
            "prompt_on_or_off": "ON",
            "prime_contract_id": "CONTRACT-001",
            "requisition_id": "REQ-001",
            "po_number": "PO-10001",
            "release_number": 1,
            "order_date": "2026-01-15",
            "due_date": "2026-02-15",
            "original_due_date": "2026-02-01",
            "desired_date": "2026-02-10",
            "requisitioner_employee_id": "EMP-001",
            "requisitioner_name": "Test Requisitioner",
            "c61": "C61-TEST",
            "buyer_id": "BUYER-001",
            "buyer_name": "Test Buyer",
            "material_handler_employee_id": "EMP-002",
            "material_handler_name": "Test Handler",
            "vendor_name": "Test Vendor",
            "vendor_terms": "NET30",
            "header_performance_start_date": "2026-01-15",
            "header_performance_end_date": "2026-12-31",
            "procurement_type": "STANDARD",
            "match_cd": "3WAY",
            "line_number": 1,
            "item_id": "ITEM-001",
            "line_desc": "Test PO Line",
            "vendor_part_id": "VP-001",
            "performance_start_date": "2026-01-15",
            "performance_end_date": "2026-12-31",
            "deliver_to": "Test Location",
            "gross_unit_cost": 100.0,
            "order_quantity": 10.0,
            "vouchered_qty": 2.0,
            "total_out": 800.0,
            "cost_percentage": 20.0,
            "out_dollars": 800.0,
            "po_line_ext_amt": 1000.0,
            "sales_tax": 0.0,
            "po_line_total_amt": 1000.0,
            "vchr_po_amt_used": 200.0,
            "open_commitments": 800.0,
            "line_notes": "Test line notes",
            "project_name": "Test Project",
            "total_funded": 50000.0,
            "project_start_date": "2026-01-01",
            "project_end_date": "2026-12-31",
            "access_type": "READ",
        },

        "response_key_field": "project_id",
        "response_assert_fields": [
            "project_id",
            "po_number",
            "line_number",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1PoOpenCommitmentResponseModel",
        "handler_outer_schema": "V1PoOpenCommitmentListResponseModel",
        "handler_detail_outer_schema": "V1PoOpenCommitmentListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",
        "handler_detail_route": "/v1/financials/po-open-commitments/{project_id}",
        "handler_search_route": "/v1/financials/po-open-commitments/search",
    },


    # ========================================================
    # CLM TCV
    # ========================================================
    "clm_tcv": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "clm_tcv",
        "repo_module": "clm_tcv_repo",
        "service_module": "clm_tcv_service",
        "handler_module": "clm_tcv",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_clm_contracts",
        "repo_key_function": "get_clm_contract_by_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_clm_contracts",
        "service_key_function": "get_clm_contract_details",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_clm_contracts_v1",
        "handler_key_function": "get_clm_contract_v1",
        "handler_list_function": "list_clm_contracts_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "ClmTcvResponse",
        "search_response_model": "ClmTcvSearchServiceResponse",

        # ----------------------------------------------------
        # Key configuration
        # ----------------------------------------------------
        "key_column": "contract_id",
        "key_argument": "contract_id",
        "handler_path_parameter": "contract_id",
        "sample_key": "CONTRACT-001",

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
            "contract_id",
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
            "contract_id",
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
            "contract_id",
            "page",
            "sort",
            "columns",
        ],
        "handler_list_service_parameters": [
            "filters",
            "page",
        ],

        # ----------------------------------------------------
        # Pagination / DB execution
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

        # Repository cursor:
        # f"{last_item.get('contract_id')}_{last_item.get('mod_no')}"
        "repo_cursor_fields": [
            "contract_id",
            "mod_no",
        ],
        "repo_cursor_values": [
            "CONTRACT-001",
            "0001",
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "title",
        "sample_value": "Test CLM Contract",
        "sample_data": {
            "award_no": "AWARD-001",
            "order_no": "ORDER-001",
            "mod_no": "0001",
            "award_type": "TEST",
            "num_awardees": "1",
            "own_org_code": "ORG-001",
            "own_org_desc": "Test Organization",
            "title": "Test CLM Contract",
            "neg_total_value": 1000.0,
            "neg_chg_value": 100.0,
            "exer_total_value": 900.0,
            "exer_chg_value": 50.0,
            "fund_total_value": 800.0,
            "fund_chg_value": 25.0,
            "proj_id": "P-1001",
            "contract_id": "CONTRACT-001",
            "order_id": "ORDER-ID-001",
            "contractor_role": "Prime",
            "contract_type": "TEST",
            "cust_name": "Test Customer",
            "leg_ent_code": "LE-001",
            "leg_ent_name": "Test Legal Entity",
            "prop_no": "PROP-001",
            "mod_reason": "Test Modification",
            "con_admin_name": "Test Contract Admin",
            "prog_mgr_name": "Test Program Manager",
            "contract_max_value": 1000.0,
            "iwo": "N",
            "award_status": "ACTIVE",
            "con_status": "ACTIVE",
            "opp_id": "OPP-001",
            "subcon_admin_name": "Test Subcontract Admin",
            "active_flag": "Y",
            "perf_org_code": "PERF-001",
            "perf_org_desc": "Test Performing Org",
            "con_cust": "Test Contract Customer",
            "proj_mgr_name": "Test Project Manager",
            "sow": "Test SOW",
            "fund_cust_1": "FC1",
            "fund_cust_2": "FC2",
            "cor_name": "Test COR",
            "co_name": "Test CO",
            "px_level": "1",
        },

        "response_key_field": "contract_id",
        "response_assert_fields": [
            "contract_id",
            "mod_no",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ClmTcvResponseModel",
        "handler_outer_schema": "V1ClmTcvListResponseModel",
        "handler_detail_outer_schema": "V1ClmTcvListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Contract ID is required.",
        "handler_detail_route": "/v1/contracts/clm/{contract_id}",
        "handler_search_route": "/v1/contracts/clm/search",
        "handler_list_route": "/v1/contracts/clm",
    },


    # ========================================================
    # CONTRACT ANALYSIS
    # ========================================================
    "contract_analysis": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "contract_analysis",
        "repo_module": "contract_analysis_repo",
        "service_module": "contract_analysis_service",
        "handler_module": "contract_analysis",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_contract_analysis",
        "repo_key_function": "get_contract_analysis_by_project_level",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_contract_analysis",
        "service_key_function": "get_contract_analysis_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_contract_analysis_v1",
        "handler_key_function": "get_contract_analysis_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "ContractAnalysisResponse",
        "search_response_model": "ContractAnalysisSearchServiceResponse",

        # ----------------------------------------------------
        # Key configuration
        # ----------------------------------------------------
        "key_column": "project_level",
        "key_argument": "project_level",
        "handler_path_parameter": "project_level",
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
            "project_level",
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
            "project_level",
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
            "project_level",
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
        # f"{last_item.get('project_level')}_{last_item.get('fy_cd')}_{last_item.get('pd_no')}"
        "repo_cursor_fields": [
            "project_level",
            "fy_cd",
            "pd_no",
        ],
        "repo_cursor_values": [
            "P-1001",
            "2026",
            1,
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "project_name",
        "sample_value": "Test Project",
        "sample_data": {
            "project_level": "P-1001",
            "reorg_level": "R-01",
            "fy_cd": "2026",
            "pd_no": 1,
            "revenue": 1000.0,
            "direct_labor_on": 100.0,
            "direct_labor_off": 50.0,
            "total_labor": 150.0,
            "fringe_at_target": 10.0,
            "cilof": 5.0,
            "direct_travel": 25.0,
            "materials": 50.0,
            "odcs": 20.0,
            "interco": 10.0,
            "subs": 30.0,
            "direct_subk_accruals": 15.0,
            "direct_misc_accruals": 5.0,
            "unbillable": 0.0,
            "covid_19_cost": 0.0,
            "burdens_at_target": 20.0,
            "total_cost": 305.0,
            "com": 100.0,
            "fee": 50.0,
            "project_name": "Test Project",
            "project_type_desc": "Test Project Type",
            "project_manager_name_validated": "Test Project Manager",
            "customer_name": "Test Customer",
            "enterprise": "Test Enterprise",
        },

        "response_key_field": "project_level",
        "response_assert_fields": [
            "project_level",
            "fy_cd",
            "pd_no",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ContractAnalysisResponseModel",
        "handler_outer_schema": "V1ContractAnalysisListResponseModel",
        "handler_detail_outer_schema": "V1ContractAnalysisListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project level (proj_id) is required.",
        "handler_detail_route": "/v1/contracts/analysis/{project_level}",
        "handler_search_route": "/v1/contracts/analysis/search",
    },


    # ========================================================
    # AR HISTORY
    # ========================================================
    "ar_history": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "ar_history",
        "repo_module": "ar_history_repo",
        "service_module": "ar_history_service",
        "handler_module": "ar_history",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_ar_history",
        "repo_key_function": "get_ar_history_by_project_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_ar_history",
        "service_key_function": "get_ar_history_by_project",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_ar_history_v1",
        "handler_key_function": "get_ar_history_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "ArHistoryResponse",
        "search_response_model": "ArHistorySearchServiceResponse",

        # ----------------------------------------------------
        # Key configuration
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
        # Repository function signatures
        # ----------------------------------------------------
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
            "proj_id",
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
            "proj_id",
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
        # f"{last_item.get('PROJ_ID')}_{last_item.get('INVC_ID')}"
        "repo_cursor_fields": [
            "PROJ_ID",
            "INVC_ID",
        ],
        "repo_cursor_values": [
            "P-1001",
            "INV-001",
        ],
        "repo_cursor_separator": "_",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "invc_id",
        "sample_value": "INV-001",
        "sample_data": {
            "rcv_acct_id": "RCV-001",
            "proj_id": "P-1001",
            "invc_id": "INV-001",
            "bill_no_id": "BILL-001",
            "invc_dt": "2026-01-15",
            "company_id": "COMP-001",
            "invoice_amount": 1000.0,
            "receipt_amount": 250.0,
            "amount_due": 750.0,
            "last_recpt_dt": "2026-01-20",
        },

        "response_key_field": "proj_id",
        "response_assert_fields": [
            "proj_id",
            "invc_id",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ArHistoryResponseModel",
        "handler_outer_schema": "V1ArHistoryListResponseModel",
        "handler_detail_outer_schema": "V1ArHistoryListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",
        "handler_detail_route": "/v1/financials/ar-history/{proj_id}",
        "handler_search_route": "/v1/financials/ar-history/search",
    },


    # ========================================================
    # PROJECT STATUS REPORT
    # ========================================================
    "project_status_report": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "project_status_report",
        "repo_module": "project_status_report_repo",
        "service_module": "project_status_report_service",
        "handler_module": "project_status_report",

        # Standalone model for project_status_report.
        "model_module": "project_status_report",

        # Handler schemas are imported from v1.schemas.project.
        "handler_schema_module": "project",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "search_project_status_report",
        "repo_key_function": "get_project_status_report_history",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_project_status_report",
        "service_key_function": "get_project_status_report_history",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_project_status_history_v1",
        "handler_key_function": "get_project_status_history_v1",
        "handler_list_function": None,

        # ----------------------------------------------------
        # Domain models
        #
        # Standalone project_status_report domain models
        # ----------------------------------------------------
        "response_model": "ProjectStatusReportResponse",
        "search_response_model": "ProjectStatusReportSearchServiceResponse",

        # Dedicated project_status_report model file/test.
        "supports_model_test": True,

        # ----------------------------------------------------
        # Key configuration
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
        # Repository function signatures
        # ----------------------------------------------------
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
            "proj_id",
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
            "proj_id",
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

        # Repository cursor is generated from proj_id.
        "repo_cursor_fields": [
            "proj_id",
        ],
        "repo_cursor_values": [
            "P-1001",
        ],
        "repo_cursor_separator": "_",

        "default_sort_field": "fiscal_year",
        "default_sort_order": "desc",

        # ----------------------------------------------------
        # Sample model data
        #
        # The API reuses ProjectStatusResponse. Keep the
        # sample minimal so it does not invent fields that
        # were not shown in the project_status_report files.
        # ----------------------------------------------------
        "sample_field": "proj_id",
        "sample_value": "P-1001",
        "sample_data": {
            "proj_id": "P-1001",
            "lvl_no": 1,
        },
        "key_sample_data": {
            "proj_id": "P-1001",
            "lvl_no": 1,
        },

        "response_key_field": "proj_id",
        "response_assert_fields": [
            "proj_id",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ProjectStatusReportResponseModel",
        "handler_outer_schema": "V1ProjectStatusReportListResponseModel",
        "handler_detail_outer_schema": "V1ProjectStatusReportListResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "Project ID is required.",

        "handler_detail_route": "/v1/projects/project-status-history/{proj_id}",
        "handler_search_route": "/v1/projects/project-status-history/search",

        # Used by the GET/list-style query filter parser in the handler.
        "handler_filter_context": "PROJECT_STATUS_REPORT_FILTER_CONTEXT",

        "generate_repo_tests": True,
        "generate_model_tests": True,
        "generate_service_tests": True,
        "generate_handler_tests": True,
    },


    # ========================================================
    # CONTRACT MODIFICATIONS
    # ========================================================
    "contract_modifications": {
        # ----------------------------------------------------
        # Modules
        # ----------------------------------------------------
        "module_name": "contract_modifications",
        "repo_module": "contract_modifications_repo",
        "model_module": "contract_modifications",
        "service_module": "contract_modifications_service",
        "handler_module": "contract_modifications",

        # ----------------------------------------------------
        # Repository
        # ----------------------------------------------------
        "repo_search_function": "get_contract_modifications",
        "repo_key_function": "get_contract_modifications_by_id",

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------
        "service_search_function": "search_contract_modifications",
        "service_key_function": "get_contract_modifications_details",

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------
        "handler_search_function": "search_contract_modifications_v1",
        "handler_key_function": "get_contract_modifications_v1",
        "handler_list_function": "list_contract_modifications_v1",

        # ----------------------------------------------------
        # Domain models
        # ----------------------------------------------------
        "response_model": "ContractModificationsResponse",
        "search_response_model": "ContractModificationsSearchServiceResponse",
        "supports_model_test": True,

        # ----------------------------------------------------
        # Key configuration
        # ----------------------------------------------------
        "key_column": "project_id",
        "key_argument": "project_id",
        "handler_path_parameter": "project_id",
        "sample_key": "P-1001",

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
            "project_id",
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
            "project_id",
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
            "project_id",
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
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "limit_cursor",

        # Repository cursor is generated from project_id.
        "repo_cursor_fields": [
            "project_id",
        ],
        "repo_cursor_values": [
            "P-1001",
        ],
        "repo_cursor_separator": "_",

        "default_sort_field": "effective_date",
        "default_sort_order": "asc",

        # ----------------------------------------------------
        # Sample model data
        # ----------------------------------------------------
        "sample_field": "mod_number",
        "sample_value": "MOD-001",
        "sample_data": {
            "project_id": "P-1001",
            "mod_number": "MOD-001",
            "reason_for_modification": "Test modification",
            "award_status": 1,
            "effective_date": "2026-01-01",
            "negotiated_value": 1000.0,
            "exercised_value": 750.0,
            "funded_amount": 500.0,
        },

        "key_sample_data": {
            "project_id": "P-1001",
            "mod_number": "MOD-001",
            "reason_for_modification": "Test modification",
            "award_status": 1,
            "effective_date": "2026-01-01",
            "negotiated_value": 1000.0,
            "exercised_value": 750.0,
            "funded_amount": 500.0,
        },

        "response_key_field": "project_id",
        "response_assert_fields": [
            "project_id",
            "mod_number",
        ],

        # ----------------------------------------------------
        # V1 handler schemas
        # ----------------------------------------------------
        "handler_inner_schema": "V1ContractModificationsResponseModel",
        "handler_outer_schema": "V1ContractModificationsListResponseModel",
        "handler_detail_outer_schema": "V1ContractModificationsDetailResponseModel",

        # ----------------------------------------------------
        # Handler expectations / routes
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,
        "handler_missing_key_message": "ContractModifications ID is required.",

        "handler_detail_route": "/v1/contracts/modifications/{project_id}",
        "handler_search_route": "/v1/contracts/modifications/search",
        "handler_list_route": "/v1/contracts/modifications",

        "handler_filter_context": "CONTRACTMODIFICATIONS_FILTER_CONTEXT",

        "generate_repo_tests": True,
        "generate_model_tests": True,
        "generate_service_tests": True,
        "generate_handler_tests": True,
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
