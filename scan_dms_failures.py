# ========================================================
# PROJECT INFO
# ========================================================
"project_info": {
    "module_name": "project_info",
    "repo_module": "project_info_repo",
    "service_module": "project_info_service",
    "handler_module": "project_info",

    # ====================================================
    # Repository functions
    # ====================================================
    "repo_search_function": "get_project_info",
    "repo_key_function": "get_project_info_by_id",

    # ====================================================
    # Service functions
    # ====================================================
    "service_search_function": "search_project_info",
    "service_key_function": "get_project_info_details",

    # ====================================================
    # Handler functions
    # ====================================================
    "handler_search_function": "search_project_info_v1",
    "handler_key_function": "get_project_info_v1",

    # ====================================================
    # Domain models
    # ====================================================
    "response_model": "ProjectInfoResponse",
    "search_response_model": "ProjectInfoSearchServiceResponse",

    # ====================================================
    # Key lookup
    # ====================================================
    "key_column": "proj_id",
    "key_argument": "proj_id",
    "handler_path_parameter": "proj_id",
    "sample_key": "P-1001",

    # ====================================================
    # Supported operations
    # ====================================================
    "supports_search": True,
    "supports_key_lookup": True,
    "supports_handler_key_lookup": True,

    # ====================================================
    # Repository parameters
    # ====================================================
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

    # ====================================================
    # Service parameters
    # ====================================================
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

    # ====================================================
    # Handler behavior
    # ====================================================
    "handler_key_uses_columns": True,
    "handler_key_uses_page": False,
    "handler_key_uses_sort": False,

    "handler_search_uses_filters": True,
    "handler_search_uses_sort": True,
    "handler_search_uses_page": True,
    "handler_search_uses_columns": True,

    # ====================================================
    # Defaults
    # ====================================================
    "default_sort_field": None,
    "default_sort_order": None,
},
