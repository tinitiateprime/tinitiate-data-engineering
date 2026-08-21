# ========================================================
# GL DETAILS
# ========================================================
"gl_details": {
    "module_name": "gl_details",
    "repo_module": "gl_details_repo",
    "service_module": "gl_details_service",
    "handler_module": "gl_details",

    # Repository
    "repo_search_function": "get_gl_details",
    "repo_key_function": None,

    # Service
    "service_search_function": "search_gl_details",
    "service_key_function": None,

    # Handler
    "handler_search_function": "search_gl_details_v1",
    "handler_key_function": None,

    # Models
    "response_model": "GlDetailsResponse",
    "search_response_model": "GlDetailsSearchServiceResponse",

    # Logical/API key
    "key_column": "proj_id",
    "key_argument": "proj_id",
    "handler_path_parameter": None,
    "sample_key": "P-1001",

    "search_requires_key": False,

    # Supported operations
    "supports_search": True,
    "supports_list": False,
    "supports_key_lookup": False,
    "supports_handler_key_lookup": False,
    "supports_list_handler": False,

    # Repository function signature
    "repo_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # Service function signature
    "service_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # Handler -> service function signature
    "handler_service_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # Repository execute_query behavior
    "repo_execute_query_passes_limit": True,

    # ====================================================
    # IMPORTANT:
    # gl_details_repo pagination reads DATABASE RESULT
    # keys in uppercase.
    # Do NOT change these to proj_id / vchr_no.
    # ====================================================
    "repo_cursor_fields": [
        "PROJ_ID",
        "VCHR_NO",
    ],

    "repo_cursor_values": [
        "P-1001",
        "test_vchr_no",
    ],

    "repo_cursor_separator": "_",

    # Pagination
    "repo_pagination_mode": "page",
    "service_search_pagination_mode": "page",
    "service_key_pagination_mode": "page",

    # Sample Pydantic/model data
    "sample_field": "name",
    "sample_value": "Test Project",

    # Response/model field remains lowercase
    "response_key_field": "proj_id",
    "response_assert_fields": [
        "proj_id",
    ],
},
