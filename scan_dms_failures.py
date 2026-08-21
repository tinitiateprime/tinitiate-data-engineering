# ========================================================
# PROJECT INFO
# ========================================================
"project_info": {
    "module_name": "project_info",
    "repo_module": "project_info_repo",
    "service_module": "project_info_service",
    "handler_module": "project_info",

    # ====================================================
    # Repository
    # ====================================================
    "repo_search_function": "get_project_info",
    "repo_key_function": "get_project_info_by_id",

    # ====================================================
    # Service
    # ====================================================
    "service_search_function": "search_project_info",
    "service_key_function": "get_project_info_details",

    # ====================================================
    # Handler
    # ====================================================
    "handler_search_function": "search_project_info_v1",
    "handler_key_function": "get_project_info_v1",

    # ====================================================
    # Models
    # ====================================================
    "response_model": "ProjectInfoResponse",
    "search_response_model": "ProjectInfoSearchServiceResponse",

    "handler_response_model": "V1ProjectInfoResponseModel",
    "handler_list_response_model": "V1ProjectInfoListResponseModel",

    # IMPORTANT:
    # GET handler also uses the LIST response model.
    "handler_key_response_model": "V1ProjectInfoListResponseModel",
    "handler_key_item_model": "V1ProjectInfoResponseModel",

    # ====================================================
    # Key
    # ====================================================
    "key_column": "proj_id",
    "key_argument": "proj_id",
    "handler_path_parameter": "proj_id",
    "sample_key": "P-1001",

    # ====================================================
    # Behavior
    # ====================================================
    "supports_search": True,
    "supports_key_lookup": True,
    "supports_handler_key_lookup": True,

    # ====================================================
    # Repo parameters
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

    # Repo execute_query includes page limit
    "repo_execute_uses_limit": True,

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
    # Handler -> Service parameters
    # ====================================================
    "handler_service_parameters": [
        "proj_id",
        "columns",
    ],

    "handler_key_service_parameters": [
        "proj_id",
        "columns",
    ],

    "handler_search_service_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    "handler_key_uses_columns": True,
    "handler_key_uses_page": False,
    "handler_key_uses_sort": False,

    "handler_search_uses_filters": True,
    "handler_search_uses_sort": True,
    "handler_search_uses_page": True,
    "handler_search_uses_columns": True,

    # ====================================================
    # Handler validation messages
    # ====================================================
    "handler_missing_key_message": "Project ID is required.",

    # ====================================================
    # Defaults
    # ====================================================
    "default_sort_field": None,
    "default_sort_order": None,
},
