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
        #
        # get_project_modifications(
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

        # ----------------------------------------------------
        # Repository key lookup
        #
        # get_project_modifications_by_project_id(
        #     proj_id,
        #     page,
        #     sort,
        #     columns,
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
        #
        # search_project_modifications(
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

        # ----------------------------------------------------
        # Service key lookup
        #
        # get_project_modifications_by_project(
        #     proj_id,
        #     page,
        #     sort,
        #     columns,
        # )
        # ----------------------------------------------------
        "service_key_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # POST search handler -> service
        #
        # search_project_modifications_v1 calls:
        #
        # search_project_modifications(
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

        # ----------------------------------------------------
        # GET detail handler -> service
        #
        # get_project_modifications_v1 calls:
        #
        # get_project_modifications_by_project(
        #     proj_id=...,
        #     page=...,
        #     sort=...,
        #     columns=...,
        # )
        # ----------------------------------------------------
        "handler_key_service_parameters": [
            "proj_id",
            "page",
            "sort",
            "columns",
        ],

        # ----------------------------------------------------
        # Repository execute_query behavior
        #
        # execute_query(
        #     plan.sql,
        #     plan.params,
        #     limit=current_page.limit,
        # )
        # ----------------------------------------------------
        "repo_execute_query_passes_limit": True,

        # ----------------------------------------------------
        # Composite cursor
        #
        # project_modifications_repo.py uses:
        #
        # PROJ_ID
        # PROJ_MOD_ID
        #
        # and constructs:
        #
        # f"{PROJ_ID}_{PROJ_MOD_ID}"
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
        # Pagination
        # ----------------------------------------------------
        "repo_pagination_mode": "page",
        "service_search_pagination_mode": "page",
        "service_key_pagination_mode": "page",

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
        #
        # Exact names imported by
        # v1.handlers.project_modifications
        # ----------------------------------------------------
        "handler_inner_schema": (
            "V1ProjectModificationResponseModel"
        ),

        "handler_outer_schema": (
            "V1ProjectModificationListResponseModel"
        ),

        # Detail GET returns the same list response model
        # because one project can have multiple modifications.
        "handler_detail_outer_schema": (
            "V1ProjectModificationListResponseModel"
        ),

        # ----------------------------------------------------
        # Handler expectations
        # ----------------------------------------------------
        "handler_success_status": 200,
        "handler_missing_key_status": 400,
        "handler_not_found_status": 404,

        "handler_missing_key_message": (
            "Project ID is required."
        ),

        "handler_detail_route": (
            "/v1/projects/modifications/{proj_id}"
        ),

        "handler_search_route": (
            "/v1/projects/modifications/search"
        ),
    },
