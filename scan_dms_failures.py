# ========================================================
# PROJECT MODIFICATIONS
# ========================================================
"project_modifications": {
    "module_name": "project_modifications",

    # ----------------------------------------------------
    # MODULES
    # ----------------------------------------------------
    "repo_module": "project_modifications_repo",
    "service_module": "project_modifications_service",
    "handler_module": "project_modifications",

    # ----------------------------------------------------
    # REPOSITORY FUNCTIONS
    # ----------------------------------------------------
    "repo_search_function": "get_project_modifications",
    "repo_key_function": "get_project_modifications_by_project_id",

    # ----------------------------------------------------
    # SERVICE FUNCTIONS
    # ----------------------------------------------------
    "service_search_function": "search_project_modifications",
    "service_key_function": "get_project_modifications_by_project",

    # ----------------------------------------------------
    # HANDLER FUNCTIONS
    # ----------------------------------------------------
    "handler_search_function": "search_project_modifications_v1",
    "handler_key_function": "get_project_modifications_v1",

    # ----------------------------------------------------
    # MODELS
    # ----------------------------------------------------
    "response_model": "ProjectModificationResponse",
    "search_response_model": "ProjectModificationSearchServiceResponse",

    # ----------------------------------------------------
    # HANDLER RESPONSE MODELS
    # ----------------------------------------------------
    "handler_response_model": "V1ProjectModificationResponseModel",
    "handler_list_response_model": "V1ProjectModificationListResponseModel",

    # ----------------------------------------------------
    # KEY LOOKUP
    # ----------------------------------------------------
    "supports_key_lookup": True,
    "key_field": "proj_id",

    # Repository key function
    "repo_key_parameter": "proj_id",

    # Service key function
    "service_key_parameter": "proj_id",

    # Handler path parameter
    "handler_key_parameter": "proj_id",

    # ----------------------------------------------------
    # REPOSITORY KEY PARAMETERS
    # get_project_modifications_by_project_id(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ----------------------------------------------------
    "repo_key_uses_page": True,
    "repo_key_uses_sort": True,
    "repo_key_uses_columns": True,

    # ----------------------------------------------------
    # SERVICE KEY PARAMETERS
    # get_project_modifications_by_project(
    #     proj_id,
    #     page,
    #     sort,
    #     columns
    # )
    # ----------------------------------------------------
    "service_key_uses_page": True,
    "service_key_uses_sort": True,
    "service_key_uses_columns": True,

    # ----------------------------------------------------
    # HANDLER KEY PARAMETERS
    #
    # GET /v1/projects/modifications/{proj_id}
    #
    # Handler creates:
    #   page
    #   sort
    #   columns
    # ----------------------------------------------------
    "handler_key_uses_page": True,
    "handler_key_uses_sort": True,
    "handler_key_uses_columns": True,

    # ----------------------------------------------------
    # SEARCH PARAMETERS
    # ----------------------------------------------------
    "repo_search_uses_filters": True,
    "repo_search_uses_sort": True,
    "repo_search_uses_page": True,
    "repo_search_uses_columns": True,

    "service_search_uses_filters": True,
    "service_search_uses_sort": True,
    "service_search_uses_page": True,
    "service_search_uses_columns": True,

    "handler_search_uses_filters": True,
    "handler_search_uses_sort": True,
    "handler_search_uses_page": True,
    "handler_search_uses_columns": True,

    # ----------------------------------------------------
    # DEFAULTS
    # ----------------------------------------------------
    "default_sort_field": "effect_dt",
    "default_sort_order": "desc",
},


py generate_api_tests.py project_modifications --force --run
