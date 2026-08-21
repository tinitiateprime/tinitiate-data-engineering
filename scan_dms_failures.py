# ========================================================
# PROJECT MODIFICATIONS
# ========================================================
"project_modifications": {
    # ====================================================
    # BASIC MODULE INFORMATION
    # ====================================================
    "module_name": "project_modifications",

    "repo_module": "project_modifications_repo",
    "service_module": "project_modifications_service",
    "handler_module": "project_modifications",

    # ====================================================
    # REPOSITORY FUNCTIONS
    # ====================================================
    "repo_search_function": "get_project_modifications",
    "repo_key_function": "get_project_modifications_by_project_id",

    # ====================================================
    # SERVICE FUNCTIONS
    # ====================================================
    "service_search_function": "search_project_modifications",
    "service_key_function": "get_project_modifications_by_project",

    # ====================================================
    # HANDLER FUNCTIONS
    # ====================================================
    "handler_search_function": "search_project_modifications_v1",
    "handler_key_function": "get_project_modifications_v1",

    # ====================================================
    # DOMAIN MODELS
    # ====================================================
    "response_model": "ProjectModificationResponse",
    "search_response_model": "ProjectModificationSearchServiceResponse",

    # ====================================================
    # HANDLER RESPONSE MODELS
    # ====================================================
    "handler_response_model": "V1ProjectModificationResponseModel",
    "handler_list_response_model": "V1ProjectModificationListResponseModel",

    # ====================================================
    # KEY LOOKUP
    # ====================================================
    "supports_key_lookup": True,

    "key_argument": "proj_id",
    "key_column": "proj_id",
    "key_field": "proj_id",

    "sample_key": "P-1001",

    # ====================================================
    # REPOSITORY SEARCH PARAMETERS
    #
    # get_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # ====================================================
    "repo_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # ====================================================
    # REPOSITORY KEY PARAMETERS
    #
    # get_project_modifications_by_project_id(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ====================================================
    "repo_key_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ====================================================
    # SERVICE SEARCH PARAMETERS
    #
    # search_project_modifications(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # ====================================================
    "service_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # ====================================================
    # SERVICE KEY PARAMETERS
    #
    # get_project_modifications_by_project(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ====================================================
    "service_key_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ====================================================
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
    # ====================================================
    "handler_service_parameters": [
        "proj_id",
        "page",
        "sort",
        "columns",
    ],

    # ====================================================
    # PARAMETER NAMES
    # ====================================================
    "repo_key_parameter": "proj_id",
    "service_key_parameter": "proj_id",
    "handler_key_parameter": "proj_id",

    # ====================================================
    # REPOSITORY KEY FEATURES
    # ====================================================
    "repo_key_uses_page": True,
    "repo_key_uses_sort": True,
    "repo_key_uses_columns": True,

    # ====================================================
    # SERVICE KEY FEATURES
    # ====================================================
    "service_key_uses_page": True,
    "service_key_uses_sort": True,
    "service_key_uses_columns": True,

    # ====================================================
    # HANDLER KEY FEATURES
    # ====================================================
    "handler_key_uses_page": True,
    "handler_key_uses_sort": True,
    "handler_key_uses_columns": True,

    # ====================================================
    # REPOSITORY SEARCH FEATURES
    # ====================================================
    "repo_search_uses_filters": True,
    "repo_search_uses_sort": True,
    "repo_search_uses_page": True,
    "repo_search_uses_columns": True,

    # ====================================================
    # SERVICE SEARCH FEATURES
    # ====================================================
    "service_search_uses_filters": True,
    "service_search_uses_sort": True,
    "service_search_uses_page": True,
    "service_search_uses_columns": True,

    # ====================================================
    # HANDLER SEARCH FEATURES
    # ====================================================
    "handler_search_uses_filters": True,
    "handler_search_uses_sort": True,
    "handler_search_uses_page": True,
    "handler_search_uses_columns": True,

    # ====================================================
    # DEFAULT SORTING
    # ====================================================
    "default_sort_field": "effect_dt",
    "default_sort_order": "desc",
},
