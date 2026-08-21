# ============================================================
# FINANCIALS UPDATED
# ============================================================
"financials_updated": {
    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------
    "module_name": "financials_updated",
    "repo_module": "financials_updated_repo",
    "service_module": "financials_updated_service",
    "handler_module": "financials_updated",

    # --------------------------------------------------------
    # Repository
    # --------------------------------------------------------
    "repo_search_function": "get_financials_updated",
    "repo_key_function": "get_financials_updated_by_id",

    # --------------------------------------------------------
    # Service
    # --------------------------------------------------------
    "service_search_function": "search_financials_updated",
    "service_key_function": "get_financials_updated_by_id",

    # --------------------------------------------------------
    # Handler
    # --------------------------------------------------------
    "handler_search_function": "search_financials_updated_v1",
    "handler_key_function": "get_financials_updated_v1",

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------
    "response_model": "FinancialsUpdatedResponse",
    "search_response_model": "FinancialsUpdatedSearchServiceResponse",

    # --------------------------------------------------------
    # Key configuration
    #
    # Source:
    #   logical_id_field="id"
    #
    # Repo/service Python parameter:
    #   id_: str
    #
    # Handler path:
    #   /v1/financials/funding-forecast/{id}
    # --------------------------------------------------------
    "key_column": "id",
    "key_argument": "id_",
    "handler_path_parameter": "id",
    "sample_key": "TEST-ID-001",

    # --------------------------------------------------------
    # Capabilities
    # --------------------------------------------------------
    "search_requires_key": False,
    "supports_search": True,
    "supports_key_lookup": True,
    "supports_handler_key_lookup": True,

    # There is no separate GET-list handler.
    # POST /search is the list/search endpoint.
    "supports_list_handler": False,

    # --------------------------------------------------------
    # Repository parameters
    #
    # get_financials_updated(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # --------------------------------------------------------
    "repo_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # get_financials_updated_by_id(
    #     id_,
    #     page,
    #     sort,
    #     columns
    # )
    "repo_key_parameters": [
        "id_",
        "page",
        "sort",
        "columns",
    ],

    # --------------------------------------------------------
    # Service parameters
    #
    # search_financials_updated(
    #     filters,
    #     sort,
    #     page,
    #     columns
    # )
    # --------------------------------------------------------
    "service_search_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # get_financials_updated_by_id(
    #     id_,
    #     page,
    #     sort,
    #     columns
    # )
    "service_key_parameters": [
        "id_",
        "page",
        "sort",
        "columns",
    ],

    # --------------------------------------------------------
    # Handler -> service parameters
    #
    # POST search handler calls:
    #
    # search_financials_updated(
    #     filters=filters_data,
    #     sort=sort,
    #     page=page,
    #     columns=columns
    # )
    # --------------------------------------------------------
    "handler_service_parameters": [
        "filters",
        "sort",
        "page",
        "columns",
    ],

    # GET key handler calls:
    #
    # get_financials_updated_by_id(
    #     id_=id_,
    #     page=page,
    #     sort=sort,
    #     columns=columns
    # )
    "handler_key_service_parameters": [
        "id_",
        "page",
        "sort",
        "columns",
    ],

    # --------------------------------------------------------
    # Repository execute_query behavior
    # --------------------------------------------------------
    "repo_execute_query_passes_limit": True,

    # --------------------------------------------------------
    # Test/sample data
    # --------------------------------------------------------
    "sample_field": "clin",
    "sample_value": "TEST-CLIN",

    "response_key_field": "id",
    "response_assert_fields": [
        "id",
        "clin",
    ],

    # --------------------------------------------------------
    # Model field test values
    #
    # FinancialsUpdatedResponse:
    #
    # lvl       -> Optional[str]
    # id        -> Optional[str]
    # clin      -> Optional[str]
    # ceiling   -> Optional[float]
    # funding   -> Optional[float]
    # ltd       -> Optional[float]
    # etc       -> Optional[float]
    # eac       -> Optional[float]
    # date_75   -> Optional[date]
    # date_100  -> Optional[date]
    # --------------------------------------------------------
    "sample_data": {
        "lvl": "1",
        "id": "TEST-ID-001",
        "clin": "TEST-CLIN",
        "ceiling": 1000.0,
        "funding": 800.0,
        "ltd": 500.0,
        "etc": 300.0,
        "eac": 800.0,
        "date_75": "2026-08-01",
        "date_100": "2026-09-01",
    },
},
