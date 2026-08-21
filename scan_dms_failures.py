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
    "repo_key_function": None,

    # ----------------------------------------------------
    # Service
    # ----------------------------------------------------
    "service_search_function": "search_po_funding_detail",
    "service_key_function": None,

    # ----------------------------------------------------
    # Handler
    # ----------------------------------------------------
    "handler_search_function": "search_po_funding_detail_v1",
    "handler_key_function": None,
    "handler_list_function": None,

    # ----------------------------------------------------
    # Domain models
    # ----------------------------------------------------
    "response_model": "PoFundingDetailResponse",
    "search_response_model": "PoFundingDetailSearchServiceResponse",

    # ----------------------------------------------------
    # Key configuration
    #
    # QuerySpec logical_id_field = "proj_id"
    # ----------------------------------------------------
    "key_column": "proj_id",
    "key_argument": "proj_id",
    "handler_path_parameter": None,
    "sample_key": "P-1001",

    # Search does NOT require proj_id
    "search_requires_key": False,

    # ----------------------------------------------------
    # Supported operations
    # ----------------------------------------------------
    "supports_search": True,
    "supports_list": False,
    "supports_key_lookup": False,
    "supports_handler_key_lookup": False,

    # ----------------------------------------------------
    # Repository function signature
    #
    # get_po_funding_detail(
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

    # No repository key function
    "repo_key_parameters": [],

    # ----------------------------------------------------
    # Service function signature
    #
    # search_po_funding_detail(
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

    # No service key function
    "service_key_parameters": [],

    # ----------------------------------------------------
    # Handler -> service parameters
    #
    # search_po_funding_detail_v1 calls:
    # search_po_funding_detail(
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

    "handler_key_service_parameters": [],

    # ----------------------------------------------------
    # Repository execute_query behavior
    # ----------------------------------------------------
    "repo_execute_query_passes_limit": True,

    # ----------------------------------------------------
    # Pagination / cursor
    #
    # IMPORTANT:
    # _format_paginated_response() builds the cursor from:
    #
    #     po_id
    #     proj_id
    #
    # This MUST match the actual repository implementation.
    # ----------------------------------------------------
    "repo_cursor_fields": [
        "po_id",
        "proj_id",
    ],

    "repo_cursor_values": [
        "test_po_id",
        "P-1001",
    ],

    "repo_cursor_separator": "_",

    # ----------------------------------------------------
    # Pagination modes
    # ----------------------------------------------------
    "repo_pagination_mode": "page",
    "service_search_pagination_mode": "page",
    "service_key_pagination_mode": "page",

    # ----------------------------------------------------
    # Sample model data
    # ----------------------------------------------------
    "sample_field": "proj_name",
    "sample_value": "Test Project",

    # ----------------------------------------------------
    # Response assertions
    # ----------------------------------------------------
    "response_key_field": "po_id",
    "response_assert_fields": [
        "po_id",
    ],
},
