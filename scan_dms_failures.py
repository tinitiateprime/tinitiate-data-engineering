# api_test_config.py
"""
Configuration for API unit-test generation.

The generator should remain generic.
Any API-specific naming, key columns, sample values,
function names, or replacements belong in this file.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MAIN_FUNCTION_ROOT = BASE_DIR / "main-function"

SOURCE_ROOT = (
    MAIN_FUNCTION_ROOT
    / "mt-dm-lambda-src"
)

TEST_ROOT = (
    MAIN_FUNCTION_ROOT
    / "tests"
    / "unit"
)


# ============================================================
# PROJECT FINANCIAL TEMPLATE FILES
#
# These are the working tests used as templates.
# ============================================================

TEMPLATE_FILES = {
    "db": (
        TEST_ROOT
        / "db"
        / "test_project_financial_repo.py"
    ),

    "model": (
        TEST_ROOT
        / "domain"
        / "models"
        / "test_project_financial.py"
    ),

    "service": (
        TEST_ROOT
        / "domain"
        / "services"
        / "test_project_financial_service.py"
    ),

    "handler": (
        TEST_ROOT
        / "v1"
        / "test_project_financial.py"
    ),
}


# ============================================================
# DESTINATION DIRECTORIES
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
# API CONFIGURATION
# ============================================================

APIS = {

    # ========================================================
    # PO FUNDING DETAIL
    # ========================================================

    "po_funding_detail": {

        # ----------------------------------------------------
        # BASIC NAMING
        # ----------------------------------------------------

        "module_name": "po_funding_detail",

        "route_name": "po-funding-detail",

        "plural_name": "po_funding_detail",

        "source_view": "po_funding_detail_vw",


        # ----------------------------------------------------
        # KEY INFORMATION
        # ----------------------------------------------------

        # Actual field in API/model
        "key_column": "project_id",

        # Sample unit-test value
        "sample_key": "P-1001",

        # Field that can be used for filter tests
        "sample_field": "vendor_name",

        "sample_value": "Test Vendor",


        # ----------------------------------------------------
        # DATABASE / VIEW COLUMN
        # ----------------------------------------------------

        # Actual output alias from gold.po_funding_detail_vw
        "db_key_column": "project_id",

        # The view also contains po_id.
        # But project_id is what your API method uses.
        "secondary_key_column": "po_id",

        "secondary_sample_key": "0000000014",


        # ----------------------------------------------------
        # FUNCTION NAMES
        #
        # IMPORTANT:
        # Each layer has a different method name.
        # Do NOT let the generator guess these names.
        # ----------------------------------------------------

        "functions": {

            # ---------------- REPOSITORY ----------------

            # Search/list method
            "repo_list":
                "get_po_funding_detail",

            # Project-specific repository method
            "repo_by_key":
                "get_po_funding_detail_by_project_id",


            # ---------------- SERVICE ----------------

            # Actual function found in:
            #
            # domain/services/po_funding_detail_service.py
            #
            # def get_po_funding_detail_by_project(
            #     project_id: str,
            #     page=...,
            #     sort=...,
            #     columns=...
            # )
            #
            "service_by_key":
                "get_po_funding_detail_by_project",


            # Search service function, if used
            "service_search":
                "search_po_funding_detail",


            # ---------------- HANDLER ----------------

            "handler_search":
                "search_po_funding_detail_v1",

            "handler_details":
                "get_po_funding_detail_details",
        },


        # ----------------------------------------------------
        # FUNCTION ARGUMENT NAMES
        # ----------------------------------------------------

        "arguments": {

            # Repository function
            "repo_key_argument":
                "project_id",

            # Service function
            "service_key_argument":
                "project_id",

            # Handler/path parameter
            "handler_key_argument":
                "project_id",
        },


        # ----------------------------------------------------
        # MOCK SQL
        # ----------------------------------------------------

        "mock_sql": {

            "list":
                "SELECT * FROM po_funding_detail_vw",

            "by_key":
                "SELECT * FROM po_funding_detail_vw",
        },


        # ----------------------------------------------------
        # MOCK PARAMETERS
        # ----------------------------------------------------

        "mock_params": {

            # What repository builder produces when filtering
            # by project_id.
            "by_key": {
                "p0": "P-1001",
            },
        },


        # ----------------------------------------------------
        # MOCK RECORD
        # ----------------------------------------------------

        "sample_record": {
            "project_id": "P-1001",
            "po_id": "0000000014",
            "vendor_name": "Test Vendor",
        },


        # ----------------------------------------------------
        # TEMPLATE REPLACEMENTS
        #
        # Replacement happens AFTER general
        # project_financial -> po_funding_detail conversion.
        # ----------------------------------------------------

        "replacements": {

            # =================================================
            # Fix model/service naming
            # =================================================

            "get_project_financial_details":
                "get_po_funding_detail_by_project",

            "get_project_financial_by_id":
                "get_po_funding_detail_by_project",

            "get_project_financials_by_id":
                "get_po_funding_detail_by_project",


            # =================================================
            # Clean up incorrectly generated names
            # =================================================

            "get_po_funding_detail_details":
                "get_po_funding_detail_by_project",

            "get_po_funding_detail_by_project_id_details":
                "get_po_funding_detail_by_project",

            "get_po_funding_detail_by_id":
                "get_po_funding_detail_by_project",


            # =================================================
            # Parameter naming
            # =================================================

            "proj_id=":
                "project_id=",

            '"proj_id"':
                '"project_id"',

            "'proj_id'":
                "'project_id'",


            # =================================================
            # Project Financial field -> PO Funding field
            # =================================================

            '"proj_id": "P-1001"':
                '"project_id": "P-1001"',

            '"proj_name": "Test Project"':
                '"vendor_name": "Test Vendor"',

            '"cust_name": "Test Customer"':
                '"vendor_name": "Test Vendor"',


            # =================================================
            # Filter fields
            # =================================================

            '"proj_name"':
                '"vendor_name"',

            "'proj_name'":
                "'vendor_name'",

            '"Test Project"':
                '"Test Vendor"',

            "'Test Project'":
                "'Test Vendor'",


            # =================================================
            # SQL view
            # =================================================

            "project_financials_source_vw":
                "po_funding_detail_vw",

            "project_financial_vw":
                "po_funding_detail_vw",


            # =================================================
            # Module names
            # =================================================

            "project_financial_repo":
                "po_funding_detail_repo",

            "project_financial_service":
                "po_funding_detail_service",

            "project_financial":
                "po_funding_detail",
        },
    },
}
