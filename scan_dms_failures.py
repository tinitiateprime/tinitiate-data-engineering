# ============================================================
# PROJECT MODIFICATIONS
# ============================================================
"project_modifications": {

    # ========================================================
    # BASIC MODULE INFORMATION
    # ========================================================
    "module_name": "project_modifications",

    "repo_module": "project_modifications_repo",
    "service_module": "project_modifications_service",
    "handler_module": "project_modifications",

    # ========================================================
    # REPOSITORY FUNCTIONS
    # ========================================================
    # Search:
    # get_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    "repo_search_function": "get_project_modifications",

    # Key/detail:
    # get_project_modifications_by_project_id(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    "repo_key_function": "get_project_modifications_by_project_id",

    # ========================================================
    # SERVICE FUNCTIONS
    # ========================================================
    # Search:
    # search_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    "service_search_function": "search_project_modifications",

    # Key/detail:
    # get_project_modifications_by_project(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    "service_key_function": "get_project_modifications_by_project",

    # ========================================================
    # HANDLER FUNCTIONS
    # ========================================================
    # GET /v1/projects/modifications/{proj_id}
    "handler_key_function": "get_project_modifications_v1",

    # POST /v1/projects/modifications/search
    "handler_search_function": "search_project_modifications_v1",

    # No separate list handler
    "handler_list_function": None,

    # ========================================================
    # DOMAIN MODELS
    # ========================================================
    "response_model": "ProjectModificationResponse",

    "search_response_model": "ProjectModificationSearchServiceResponse",

    # ========================================================
    # HANDLER RESPONSE MODELS
    # ========================================================
    "handler_response_model": "V1ProjectModificationResponseModel",

    "handler_list_response_model": "V1ProjectModificationListResponseModel",

    # ========================================================
    # KEY LOOKUP
    # ========================================================
    "supports_key_lookup": True,

    "key_argument": "proj_id",
    "key_column": "proj_id",
    "key_field": "proj_id",

    "sample_key": "P-1001",

    # ========================================================
    # REPOSITORY SEARCH PARAMETERS
    #
    # get_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # ========================================================
    "repo_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # ========================================================
    # REPOSITORY KEY PARAMETERS
    #
    # get_project_modifications_by_project_id(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ========================================================
    "repo_key_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # SERVICE SEARCH PARAMETERS
    #
    # search_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # ========================================================
    "service_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # ========================================================
    # SERVICE KEY PARAMETERS
    #
    # get_project_modifications_by_project(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ========================================================
    "service_key_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # HANDLER -> SERVICE PARAMETERS
    #
    # get_project_modifications_v1 calls:
    #
    # get_project_modifications_by_project(
    #     proj_id=proj_id,
    #     page=page,
    #     sort=sort,
    #     columns=columns
    # )
    # ========================================================
    "handler_service_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # PARAMETER NAMES
    # ========================================================
    "repo_key_parameter": "proj_id",
    "service_key_parameter": "proj_id",
    "handler_key_parameter": "proj_id",

    # ========================================================
    # REPOSITORY KEY FEATURES
    # ========================================================
    "repo_key_uses_page": True,
    "repo_key_uses_sort": True,
    "repo_key_uses_columns": True,

    # ========================================================
    # SERVICE KEY FEATURES
    # ========================================================
    "service_key_uses_page": True,
    "service_key_uses_sort": True,
    "service_key_uses_columns": True,

    # ========================================================
    # HANDLER KEY FEATURES
    # ========================================================
    "handler_key_uses_columns": True,
    "handler_key_uses_page": True,
    "handler_key_uses_sort": True,

    # ========================================================
    # HANDLER SEARCH FEATURES
    # ========================================================
    "handler_search_uses_filters": True,
    "handler_search_uses_sort": True,
    "handler_search_uses_page": True,
    "handler_search_uses_columns": True,

    # ========================================================
    # DEFAULTS
    # ========================================================
    "default_sort_field": "effect_dt",
    "default_sort_order": "desc",

    # ========================================================
    # CURSOR INFORMATION
    #
    # Repo cursor:
    # f"{PROJ_ID}|{PROJ_MOD_ID}"
    # ========================================================
    "repo_cursor_fields": [
        "proj_id",
        "proj_mod_id",
    ],

    "repo_cursor_values": [
        "P-1001",
        "PM-001",
    ],

    "repo_cursor_separator": "|",

    # ========================================================
    # ROUTES
    # ========================================================
    "handler_key_route": (
        r"/v1/projects/modifications/(?P<proj_id>[^/]+)"
    ),

    "handler_search_route": (
        r"/v1/projects/modifications/search"
    ),

    "handler_list_route": None,
},
