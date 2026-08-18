# api_test_config.py

"""
Configuration for generate_api_tests.py.

Normal workflow:
1. Add or update APIs in this file.
2. Do NOT modify the generator.
3. Run:
       py generate_api_tests.py <api_name> --dry-run
4. Then:
       py generate_api_tests.py <api_name>
"""

APIS = {

    # ==========================================================
    # PO FUNDING DETAIL
    # ==========================================================
    "po_funding_detail": {

        # Key column used for lookup/filter tests
        "key_column": "po_id",

        # Sample value used only in generated unit tests
        "sample_key": "0000000014",

        # A normal column used for filter/assertion tests
        "sample_field": "vendor_name",

        # Sample test value for that field
        "sample_value": "Test Vendor",

        # ------------------------------------------------------
        # Naming
        # ------------------------------------------------------

        # Python module name
        "module_name": "po_funding_detail",

        # API route name
        "route_name": "po-funding-detail",

        # Used when replacing plural project_financials naming
        "plural_name": "po_funding_detail",

        # Materialized view / view name used in mocked SQL
        "source_view": "po_funding_detail_vw",

        # ------------------------------------------------------
        # API-SPECIFIC REPLACEMENTS
        #
        # The generator performs its normal project_financial
        # replacements first, then applies these overrides.
        #
        # Add differences here instead of changing the generator.
        # ------------------------------------------------------

        "replacements": {

            # Project Financial template normally generates:
            #
            # get_po_funding_detail_by_id(...)
            #
            # If the actual repository exposes:
            #
            # get_po_funding_detail(...)
            #
            # this changes the generated tests accordingly.
            "get_po_funding_detail_by_id":
                "get_po_funding_detail",

            # If service/model names later differ, add them here.
            #
            # Examples:
            #
            # "get_po_funding_detail_details":
            #     "get_po_funding_detail",
            #
            # "search_po_funding_details":
            #     "search_po_funding_detail",
        },
    },


    # ==========================================================
    # GL DETAILS
    #
    # Keep this commented while gl_details_vw is still loading.
    # Uncomment later when you want to continue testing it.
    # ==========================================================

    # "gl_details": {
    #
    #     "key_column": "proj_id",
    #
    #     "sample_key": "1001",
    #
    #     "sample_field": "description",
    #
    #     "sample_value": "Test GL Detail",
    #
    #     "module_name": "gl_details",
    #
    #     "route_name": "gl-details",
    #
    #     "plural_name": "gl_details",
    #
    #     "source_view": "gl_details_vw",
    #
    #     "replacements": {
    #
    #         "get_gl_details_by_id":
    #             "get_gl_details",
    #
    #     },
    # },

}
