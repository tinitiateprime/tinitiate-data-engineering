# ============================================================
# api_test_config.py
#
# Central configuration for API unit-test generation.
#
# IMPORTANT:
# The generator should read everything from this file.
# For a new API, normally you should only add a new entry
# inside APIS.
# ============================================================

from pathlib import Path


# ============================================================
# ROOT DIRECTORIES
# ============================================================

# Folder where this config file exists
API_ROOT = Path(__file__).resolve().parent


# ------------------------------------------------------------
# Main application/test folder
#
# Expected structure:
#
# API/
# ├── api_test_config.py
# ├── generate_api_tests.py
# └── main-function/
#     ├── mt-dm-lambda-src/
#     └── tests/
#         └── unit/
#
# ------------------------------------------------------------

MAIN_FUNCTION_ROOT = API_ROOT / "main-function"

TEST_ROOT = (
    MAIN_FUNCTION_ROOT
    / "tests"
    / "unit"
)


# ============================================================
# SOURCE CODE ROOT
# ============================================================

SOURCE_ROOT = (
    MAIN_FUNCTION_ROOT
    / "mt-dm-lambda-src"
)


# ============================================================
# PROJECT FINANCIAL TEMPLATE FILES
#
# These are the existing working tests that we use as the
# base/template for generating tests for other APIs.
# ============================================================

TEMPLATE_FILES = {

    # --------------------------------------------------------
    # Repository test template
    # --------------------------------------------------------
    "db": (
        TEST_ROOT
        / "db"
        / "test_project_financial_repo.py"
    ),

    # --------------------------------------------------------
    # Domain model test template
    # --------------------------------------------------------
    "model": (
        TEST_ROOT
        / "domain"
        / "models"
        / "test_project_financial.py"
    ),

    # --------------------------------------------------------
    # Service test template
    # --------------------------------------------------------
    "service": (
        TEST_ROOT
        / "domain"
        / "services"
        / "test_project_financial_service.py"
    ),

    # --------------------------------------------------------
    # Handler test template
    # --------------------------------------------------------
    "handler": (
        TEST_ROOT
        / "v1"
        / "test_project_financial.py"
    ),
}


# ============================================================
# DESTINATION DIRECTORIES
#
# Generated tests are written into these directories.
# ============================================================

DESTINATION_DIRS = {

    "db": (
        TEST_ROOT
        / "db"
    ),

    "model": (
        TEST_ROOT
        / "domain"
        / "models"
    ),

    "service": (
        TEST_ROOT
        / "domain"
        / "services"
    ),

    "handler": (
        TEST_ROOT
        / "v1"
    ),
}


# ============================================================
# TEST TYPES
# ============================================================

TEST_TYPES = (
    "db",
    "model",
    "service",
    "handler",
)


# ============================================================
# TEMPLATE API
#
# This tells the generator what the original template API is.
# We are using project_financial as the master working example.
# ============================================================

TEMPLATE_API = {

    "module_name": "project_financial",

    "route_name": "project-financials",

    "singular_name": "project_financial",

    "plural_name": "project_financials",

    "source_view": "project_financial_vw",

    # Key used by the Project Financial API
    "key_column": "project_id",

    "key_argument": "project_id",

    # Repository functions
    "repo_search_function":
        "get_project_financial",

    "repo_key_function":
        "get_project_financial_by_project_id",

    # Service functions
    "service_search_function":
        "search_project_financials",

    "service_key_function":
        "get_project_financial_by_project",

    # Handler functions
    "handler_search_function":
        "search_project_financials_v1",

    "handler_key_function":
        "get_project_financial_details",

    # Models
    "response_model":
        "ProjectFinancialResponse",

    "search_response_model":
        "ProjectFinancialSearchServiceResponse",

    # Defaults
    "default_page_size": 100,

    "default_sort_field":
        "order_date",

    "default_sort_order":
        "desc",
}


# ============================================================
# API CONFIGURATION
#
# For every new API:
#
# 1. Add one entry here.
# 2. Do NOT modify the generator.
#
# Example:
#
# py generate_api_tests.py po_funding_detail
#
# ============================================================

APIS = {


    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================

    "po_funding_detail": {

        # ----------------------------------------------------
        # Naming
        # ----------------------------------------------------

        "module_name":
            "po_funding_detail",

        "route_name":
            "po-funding-detail",

        "singular_name":
            "po_funding_detail",

        "plural_name":
            "po_funding_detail",


        # ----------------------------------------------------
        # View / Materialized View
        # ----------------------------------------------------

        "source_schema":
            "gold",

        "source_view":
            "po_funding_detail_vw",


        # ----------------------------------------------------
        # Key column
        #
        # Based on your actual code:
        #
        # get_po_funding_detail_by_project_id(
        #     project_id: str,
        #     ...
        # )
        #
        # ----------------------------------------------------

        "key_column":
            "project_id",

        "key_argument":
            "project_id",

        "sample_key":
            "P-1001",


        # ----------------------------------------------------
        # Sample field/value
        #
        # Used when generating filter tests.
        # ----------------------------------------------------

        "sample_field":
            "vendor_name",

        "sample_value":
            "Test Vendor",


        # ----------------------------------------------------
        # Repository
        #
        # Actual functions:
        #
        # get_po_funding_detail(...)
        #
        # get_po_funding_detail_by_project_id(...)
        #
        # ----------------------------------------------------

        "repo_module":
            "po_funding_detail_repo",

        "repo_search_function":
            "get_po_funding_detail",

        "repo_key_function":
            "get_po_funding_detail_by_project_id",


        # ----------------------------------------------------
        # Service
        #
        # From your actual service file:
        #
        # search_po_funding_detail(...)
        #
        # get_po_funding_detail_by_project(...)
        #
        # ----------------------------------------------------

        "service_module":
            "po_funding_detail_service",

        "service_search_function":
            "search_po_funding_detail",

        "service_key_function":
            "get_po_funding_detail_by_project",


        # ----------------------------------------------------
        # Handler
        #
        # Your screenshot showed the handler function is:
        #
        # search_po_funding_detail_v1
        #
        # There does NOT appear to be a separate details
        # function.
        #
        # ----------------------------------------------------

        "handler_module":
            "po_funding_detail",

        "handler_search_function":
            "search_po_funding_detail_v1",

        "handler_key_function":
            None,


        # ----------------------------------------------------
        # Pydantic response models
        # ----------------------------------------------------

        "response_model":
            "PoFundingDetailResponse",

        "search_response_model":
            "PoFundingDetailSearchServiceResponse",


        # ----------------------------------------------------
        # Pagination defaults
        #
        # Your service uses:
        #
        # PaginationModel(
        #     limit=settings.DEFAULT_PAGE_SIZE
        # )
        #
        # Your tests showed DEFAULT_PAGE_SIZE = 100.
        #
        # ----------------------------------------------------

        "default_page_size":
            100,


        # ----------------------------------------------------
        # Default sorting
        #
        # Your service showed:
        #
        # SortModel(
        #     field="order_date",
        #     order="desc"
        # )
        #
        # ----------------------------------------------------

        "default_sort_field":
            "order_date",

        "default_sort_order":
            "desc",


        # ----------------------------------------------------
        # Function capabilities
        #
        # This allows the generator to decide which tests
        # should exist.
        # ----------------------------------------------------

        "supports_search":
            True,

        "supports_key_lookup":
            True,

        "supports_filters":
            True,

        "supports_sort":
            True,

        "supports_pagination":
            True,

        "supports_columns":
            True,

        # No separate handler GET/details endpoint
        "supports_handler_key_lookup":
            False,


        # ----------------------------------------------------
        # Search function behavior
        #
        # search_po_funding_detail supports:
        #
        # filters
        # sort
        # page
        # columns
        #
        # ----------------------------------------------------

        "search_parameters": [
            "filters",
            "sort",
            "page",
            "columns",
        ],


        # ----------------------------------------------------
        # Key lookup SERVICE behavior
        #
        # Your actual service function:
        #
        # get_po_funding_detail_by_project(
        #     project_id,
        #     page=None,
        #     sort=None,
        #     columns=None
        # )
        #
        # IMPORTANT:
        #
        # It does NOT accept filters.
        # It does NOT accept limit directly.
        # It does NOT accept cursor directly.
        #
        # Pagination is passed through PaginationModel.
        #
        # ----------------------------------------------------

        "service_key_parameters": [
            "project_id",
            "page",
            "sort",
            "columns",
        ],


        # ----------------------------------------------------
        # Repository key lookup behavior
        #
        # Actual repository call generated by the service:
        #
        # get_po_funding_detail_by_project_id(
        #     project_id=project_id,
        #     page=current_page,
        #     sort=current_sort,
        #     columns=columns
        # )
        #
        # ----------------------------------------------------

        "repo_key_parameters": [
            "project_id",
            "page",
            "sort",
            "columns",
        ],


        # ----------------------------------------------------
        # Handler search behavior
        # ----------------------------------------------------

        "handler_search_parameters": [
            "event",
            "context",
        ],


        # ----------------------------------------------------
        # Sample record
        #
        # IMPORTANT:
        #
        # Add more fields here if your
        # PoFundingDetailResponse requires them.
        #
        # ----------------------------------------------------

        "sample_record": {

            "project_id":
                "P-1001",

            "vendor_name":
                "Test Vendor",

            "order_date":
                "2026-01-01",
        },


        # ----------------------------------------------------
        # Explicit replacements
        #
        # This handles names that cannot safely be derived
        # automatically.
        # ----------------------------------------------------

        "replacements": {

            # ------------------------------------------------
            # Repository functions
            # ------------------------------------------------

            "get_project_financial":
                "get_po_funding_detail",

            "get_project_financial_by_project_id":
                "get_po_funding_detail_by_project_id",


            # ------------------------------------------------
            # Service functions
            # ------------------------------------------------

            "search_project_financials":
                "search_po_funding_detail",

            "search_project_financial":
                "search_po_funding_detail",

            "get_project_financial_by_project":
                "get_po_funding_detail_by_project",


            # ------------------------------------------------
            # Handler function
            # ------------------------------------------------

            "search_project_financials_v1":
                "search_po_funding_detail_v1",

            "search_project_financial_v1":
                "search_po_funding_detail_v1",


            # ------------------------------------------------
            # Models
            # ------------------------------------------------

            "ProjectFinancialSearchServiceResponse":
                "PoFundingDetailSearchServiceResponse",

            "ProjectFinancialResponse":
                "PoFundingDetailResponse",


            # ------------------------------------------------
            # Module names
            # ------------------------------------------------

            "project_financial_service":
                "po_funding_detail_service",

            "project_financial_repo":
                "po_funding_detail_repo",


            # ------------------------------------------------
            # View
            # ------------------------------------------------

            "project_financial_vw":
                "po_funding_detail_vw",


            # ------------------------------------------------
            # API names
            # ------------------------------------------------

            "project_financials":
                "po_funding_detail",

            "project_financial":
                "po_funding_detail",

            "project-financials":
                "po-funding-detail",

            "project-financial":
                "po-funding-detail",


            # ------------------------------------------------
            # Sample filter data
            # ------------------------------------------------

            "cust_name":
                "vendor_name",

            "customer_name":
                "vendor_name",

            "Test Customer":
                "Test Vendor",
        },
    },


    # ========================================================
    # NEXT API
    #
    # Copy the PO Funding Detail section and modify only
    # these values for your next API.
    #
    # Example:
    #
    # "employee_profile": {
    #     ...
    # }
    #
    # ========================================================

}


# ============================================================
# HELPER FUNCTIONS
#
# Generator can use these instead of duplicating config logic.
# ============================================================

def get_api_config(api_name: str) -> dict:
    """
    Return configuration for an API.
    """

    if api_name not in APIS:
        available = ", ".join(APIS.keys())

        raise KeyError(
            f"Unknown API '{api_name}'. "
            f"Available APIs: {available}"
        )

    return APIS[api_name]


def get_template_file(test_type: str) -> Path:
    """
    Return template file path.
    """

    if test_type not in TEMPLATE_FILES:
        raise KeyError(
            f"Unknown test type: {test_type}"
        )

    return TEMPLATE_FILES[test_type]


def get_destination_dir(test_type: str) -> Path:
    """
    Return destination test directory.
    """

    if test_type not in DESTINATION_DIRS:
        raise KeyError(
            f"Unknown test type: {test_type}"
        )

    return DESTINATION_DIRS[test_type]


def validate_config() -> None:
    """
    Basic startup validation.
    """

    required_api_fields = [

        "module_name",

        "key_column",

        "sample_key",

        "repo_search_function",

        "repo_key_function",

        "service_search_function",

        "service_key_function",

        "handler_search_function",

        "response_model",

        "search_response_model",
    ]

    errors = []

    for api_name, config in APIS.items():

        for field in required_api_fields:

            if field not in config:

                errors.append(
                    f"{api_name}: missing '{field}'"
                )

    if errors:

        raise ValueError(
            "Invalid api_test_config.py:\n"
            + "\n".join(errors)
        )


# ============================================================
# OPTIONAL DEBUG
#
# You can run:
#
# py api_test_config.py
#
# to verify the config.
# ============================================================

if __name__ == "__main__":

    validate_config()

    print()
    print("=" * 80)
    print("API TEST CONFIGURATION")
    print("=" * 80)

    print()
    print(f"API_ROOT:           {API_ROOT}")
    print(f"MAIN_FUNCTION_ROOT: {MAIN_FUNCTION_ROOT}")
    print(f"TEST_ROOT:          {TEST_ROOT}")
    print(f"SOURCE_ROOT:        {SOURCE_ROOT}")

    print()
    print("Template files")
    print("-" * 80)

    for test_type, path in TEMPLATE_FILES.items():

        print(
            f"{test_type:<10} "
            f"{path} "
            f"exists={path.exists()}"
        )

    print()
    print("Configured APIs")
    print("-" * 80)

    for api_name, config in APIS.items():

        print(
            f"{api_name:<30} "
            f"key={config['key_column']:<20} "
            f"repo={config['repo_key_function']}"
        )

    print()
    print("Configuration OK")
