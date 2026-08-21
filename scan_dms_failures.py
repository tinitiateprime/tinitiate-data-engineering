# ============================================================
# PROJECT STATUS DETAIL
# ============================================================
"project_status_detail": {

    # ========================================================
    # BASIC MODULE INFORMATION
    # ========================================================
    "module_name": "project_status_detail",

    "repo_module": "project_status_detail_repo",
    "service_module": "project_status_detail_service",
    "handler_module": "project_status_detail",

    # ========================================================
    # REPOSITORY FUNCTIONS
    # ========================================================
    "repo_search_function": "get_project_status_detail",
    "repo_key_function": "get_project_status_detail_by_project_level",

    # ========================================================
    # SERVICE FUNCTIONS
    # ========================================================
    "service_search_function": "search_project_status_detail",
    "service_key_function": "get_project_status_detail_by_project",

    # ========================================================
    # HANDLER FUNCTIONS
    # ========================================================
    "handler_search_function": "search_project_status_detail_v1",
    "handler_key_function": "get_project_status_detail_v1",

    # No separate list handler
    "handler_list_function": None,

    # ========================================================
    # DOMAIN MODELS
    # ========================================================
    "response_model": "ProjectStatusDetailResponse",
    "search_response_model": "ProjectStatusDetailSearchServiceResponse",

    # ========================================================
    # HANDLER RESPONSE MODELS
    # ========================================================
    "handler_response_model": "V1ProjectStatusDetailResponseModel",
    "handler_list_response_model": "V1ProjectStatusDetailListResponseModel",

    # ========================================================
    # KEY LOOKUP
    # ========================================================
    "supports_key_lookup": True,

    "key_argument": "project_level",
    "key_column": "project_level",
    "key_field": "project_level",

    "sample_key": "P-1001",

    # ========================================================
    # REPOSITORY SEARCH PARAMETERS
    #
    # get_project_status_detail(
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
    # get_project_status_detail_by_project_level(
    #     project_level,
    #     page,
    #     sort,
    #     columns
    # )
    # ========================================================
    "repo_key_parameters": [
        "project_level",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # SERVICE SEARCH PARAMETERS
    #
    # search_project_status_detail(
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
    # get_project_status_detail_by_project(
    #     project_level,
    #     page,
    #     sort,
    #     columns
    # )
    # ========================================================
    "service_key_parameters": [
        "project_level",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # HANDLER -> SERVICE PARAMETERS
    #
    # GET handler calls:
    #
    # get_project_status_detail_by_project(
    #     project_level=project_level,
    #     page=page,
    #     sort=sort,
    #     columns=columns
    # )
    # ========================================================
    "handler_service_parameters": [
        "project_level",
        "page",
        "sort",
        "columns",
    ],

    # ========================================================
    # PARAMETER NAMES
    # ========================================================
    "repo_key_parameter": "project_level",
    "service_key_parameter": "project_level",
    "handler_key_parameter": "project_level",

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
    "default_sort_field": "period",
    "default_sort_order": "desc",

    # ========================================================
    # REPOSITORY CURSOR CONFIGURATION
    # ========================================================
    "repo_cursor_fields": [
        "project_level",
    ],

    "repo_cursor_values": [
        "P-1001",
    ],

    "repo_cursor_separator": "|",

    # ========================================================
    # HANDLER ROUTES
    # ========================================================
    "handler_detail_route": (
        r"/v1/projects/status-detail/(?P<project_level>[^/]+)"
    ),

    "handler_search_route": (
        r"/v1/projects/status-detail/search"
    ),
},
