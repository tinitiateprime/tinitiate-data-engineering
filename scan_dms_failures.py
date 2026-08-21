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
        "proj_id",
        "vchr_no",
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
