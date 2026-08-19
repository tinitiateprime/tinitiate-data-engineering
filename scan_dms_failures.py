"""
api_test_config.py

Central configuration for API unit-test generation.

IMPORTANT
---------
For a new API, normally you should ONLY add a new entry to APIS.

You should not need to change generate_api_tests.py.

The generator creates:

    tests/unit/db/test_<api>_repo.py
    tests/unit/domain/models/test_<api>.py
    tests/unit/domain/services/test_<api>_service.py
    tests/unit/v1/test_<api>.py
"""

from pathlib import Path


# ============================================================
# PROJECT ROOTS
# ============================================================

API_ROOT = Path(__file__).resolve().parent

MAIN_FUNCTION_ROOT = API_ROOT / "main-function"

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
# TEMPLATE FILES
# ============================================================
#
# We continue to use project_financial as the base template.
#
# These files must already exist and pass.
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
#
# Add future APIs here.
#
# lookup:
#
#   enabled
#       Does this API have a "by key" lookup?
#
#   key_column
#       Actual API/database key.
#
#   key_parameter
#       Python parameter expected by the service/repository.
#
#   repo_function
#       Repository lookup function.
#
#   service_function
#       Service lookup function.
#
#   supports_filters
#       Whether lookup accepts filters.
#
#   supports_page
#       Whether lookup accepts PaginationModel.
#
#   supports_sort
#       Whether lookup accepts SortModel.
#
#   supports_columns
#       Whether lookup accepts columns.
#
#   pagination_style
#       "model" means:
#
#           page=PaginationModel(
#               limit=25,
#               cursor="current-cursor"
#           )
#
#       NOT:
#
#           limit=25,
#           cursor="current-cursor"
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

        "module_name": "po_funding_detail",

        "class_name": "PoFundingDetail",

        "response_model": "PoFundingDetailResponse",

        "search_response_model": (
            "PoFundingDetailSearchServiceResponse"
        ),

        # ----------------------------------------------------
        # Production modules
        # ----------------------------------------------------

        "repo_import": (
            "db.repositories.po_funding_detail_repo"
        ),

        "service_import": (
            "domain.services.po_funding_detail_service"
        ),

        "model_import": (
            "domain.models.po_funding_detail"
        ),

        "handler_import": (
            "v1.po_funding_detail"
        ),

        # ----------------------------------------------------
        # Materialized View / View
        # ----------------------------------------------------

        "source_view": "po_funding_detail_vw",

        # ----------------------------------------------------
        # Search function
        # ----------------------------------------------------

        "search_function": "search_po_funding_detail",

        "repo_search_function": "get_po_funding_detail",

        # Search endpoint supports all of these
        "search_supports_filters": True,
        "search_supports_page": True,
        "search_supports_sort": True,
        "search_supports_columns": True,

        # ----------------------------------------------------
        # Lookup / key function
        # ----------------------------------------------------

        "lookup": {

            "enabled": True,

            # API key exposed to caller
            "key_column": "project_id",

            # Python function argument
            "key_parameter": "project_id",

            # Sample unit-test key
            "sample_key": "P-1001",

            # Repository function
            "repo_function": (
                "get_po_funding_detail_by_project_id"
            ),

            # Service function
            "service_function": (
                "get_po_funding_detail_by_project"
            ),

            # IMPORTANT:
            #
            # Production function currently accepts:
            #
            # project_id
            # page
            # sort
            # columns
            #
            # It does NOT accept filters.
            #

            "supports_filters": False,

            "supports_page": True,
            "supports_sort": True,
            "supports_columns": True,

            "pagination_style": "model",
        },

        # ----------------------------------------------------
        # Default service behavior
        # ----------------------------------------------------

        "defaults": {

            "page_size": 100,

            "sort_field": "order_date",

            "sort_order": "desc",
        },

        # ----------------------------------------------------
        # Sample fields
        # ----------------------------------------------------

        "sample": {

            "field": "vendor_name",

            "value": "Test Vendor",

            "second_value": "Test Vendor - Detail 2",
        },

        # ----------------------------------------------------
        # Handler
        # ----------------------------------------------------

        "handler": {

            "search_function": (
                "search_po_funding_detail_v1"
            ),

            "detail_function": (
                "get_po_funding_detail"
            ),

            "search_path": (
                "/v1/po-funding-detail/search"
            ),

            "detail_path": (
                "/v1/po-funding-detail"
            ),
        },

        # ----------------------------------------------------
        # Additional replacements
        # ----------------------------------------------------
        #
        # Add API-specific text differences here.
        #
        # Generator runs standard replacements first,
        # then these.
        # ----------------------------------------------------

        "replacements": {

            "project financial": "po funding detail",
            "Project Financial": "PO Funding Detail",
            "PROJECT_FINANCIAL": "PO_FUNDING_DETAIL",
        },
    },


    # ========================================================
    # Example future API
    # ========================================================
    #
    # "gl_details": {
    #
    #     "module_name": "gl_details",
    #     "class_name": "GlDetails",
    #     "response_model": "GlDetailsResponse",
    #     "search_response_model": "GlDetailsSearchServiceResponse",
    #
    #     "repo_import": "db.repositories.gl_details_repo",
    #     "service_import": "domain.services.gl_details_service",
    #     "model_import": "domain.models.gl_details",
    #     "handler_import": "v1.gl_details",
    #
    #     "source_view": "gl_details_vw",
    #
    #     "search_function": "search_gl_details",
    #     "repo_search_function": "get_gl_details",
    #
    #     "search_supports_filters": True,
    #     "search_supports_page": True,
    #     "search_supports_sort": True,
    #     "search_supports_columns": True,
    #
    #     "lookup": {
    #         "enabled": True,
    #         "key_column": "proj_id",
    #         "key_parameter": "proj_id",
    #         "sample_key": "1001",
    #         "repo_function": "get_gl_details_by_id",
    #         "service_function": "get_gl_details",
    #         "supports_filters": True,
    #         "supports_page": True,
    #         "supports_sort": True,
    #         "supports_columns": True,
    #         "pagination_style": "model",
    #     },
    #
    #     "defaults": {
    #         "page_size": 100,
    #         "sort_field": "proj_id",
    #         "sort_order": "asc",
    #     },
    #
    #     "sample": {
    #         "field": "description",
    #         "value": "Test GL Detail",
    #         "second_value": "Test GL Detail 2",
    #     },
    #
    #     "handler": {
    #         "search_function": "search_gl_details_v1",
    #         "detail_function": "get_gl_details",
    #         "search_path": "/v1/gl-details/search",
    #         "detail_path": "/v1/gl-details",
    #     },
    #
    #     "replacements": {},
    # },
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


++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Generator
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


"""
generate_api_tests.py

Generic API unit-test generator.

The generator uses project_financial as a working template,
but API-specific differences are controlled from api_test_config.py.

Usage
-----

List configured APIs:

    py generate_api_tests.py --list


Dry run:

    py generate_api_tests.py po_funding_detail --dry-run


Generate:

    py generate_api_tests.py po_funding_detail


Overwrite existing generated tests:

    py generate_api_tests.py po_funding_detail --force


Generate every configured API:

    py generate_api_tests.py --all


Generate every API and overwrite:

    py generate_api_tests.py --all --force
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple


from api_test_config import (
    APIS,
    TEMPLATE_FILES,
    DESTINATION_DIRS,
    TEST_TYPES,
)


# ============================================================
# STRING HELPERS
# ============================================================


def snake_to_pascal(value: str) -> str:
    """
    po_funding_detail -> PoFundingDetail
    """

    return "".join(
        word.capitalize()
        for word in value.split("_")
    )


def snake_to_title(value: str) -> str:
    """
    po_funding_detail -> PO Funding Detail-ish title.
    """

    return value.replace("_", " ").title()


def safe_replace(
    text: str,
    old: str,
    new: str,
) -> str:

    if not old:
        return text

    return text.replace(old, new)


# ============================================================
# DESTINATION FILE
# ============================================================


def destination_file(
    api_name: str,
    test_type: str,
) -> Path:

    if test_type == "db":

        filename = (
            f"test_{api_name}_repo.py"
        )

    elif test_type == "model":

        filename = (
            f"test_{api_name}.py"
        )

    elif test_type == "service":

        filename = (
            f"test_{api_name}_service.py"
        )

    elif test_type == "handler":

        filename = (
            f"test_{api_name}.py"
        )

    else:

        raise ValueError(
            f"Unknown test type: {test_type}"
        )

    return (
        DESTINATION_DIRS[test_type]
        / filename
    )


# ============================================================
# BASIC PROJECT FINANCIAL REPLACEMENT
# ============================================================


def apply_standard_replacements(
    text: str,
    api_name: str,
    config: Dict[str, Any],
) -> str:

    module_name = config["module_name"]

    class_name = config.get(
        "class_name",
        snake_to_pascal(module_name),
    )

    response_model = config.get(
        "response_model",
        f"{class_name}Response",
    )

    search_response_model = config.get(
        "search_response_model",
        f"{class_name}SearchServiceResponse",
    )

    lookup = config.get(
        "lookup",
        {},
    )

    key_column = lookup.get(
        "key_column",
        "project_id",
    )

    key_parameter = lookup.get(
        "key_parameter",
        key_column,
    )

    sample_key = lookup.get(
        "sample_key",
        "P-1001",
    )

    sample = config.get(
        "sample",
        {},
    )

    sample_field = sample.get(
        "field",
        "name",
    )

    sample_value = sample.get(
        "value",
        f"Test {class_name}",
    )

    source_view = config.get(
        "source_view",
        module_name + "_vw",
    )

    # --------------------------------------------------------
    # Core module/file names
    # --------------------------------------------------------

    replacements: Tuple[Tuple[str, str], ...] = (

        (
            "project_financial",
            module_name,
        ),

        (
            "ProjectFinancial",
            class_name,
        ),

        (
            "PROJECT_FINANCIAL",
            module_name.upper(),
        ),

        (
            "Project Financial",
            snake_to_title(module_name),
        ),

        (
            "project financial",
            module_name.replace("_", " "),
        ),

        # Models

        (
            "ProjectFinancialResponse",
            response_model,
        ),

        (
            "ProjectFinancialSearchServiceResponse",
            search_response_model,
        ),

        # Sample key

        (
            "P-1001",
            sample_key,
        ),

        # Sample field

        (
            "proj_name",
            sample_field,
        ),

        (
            "Test Project",
            sample_value,
        ),

        # View

        (
            "project_financial_vw",
            source_view,
        ),
    )

    for old, new in replacements:

        text = safe_replace(
            text,
            old,
            new,
        )

    # --------------------------------------------------------
    # Replace project key
    # --------------------------------------------------------

    if key_column != "project_id":

        text = re.sub(
            r"\bproject_id\b",
            key_column,
            text,
        )

    # --------------------------------------------------------
    # API-specific custom replacements
    # --------------------------------------------------------

    for old, new in config.get(
        "replacements",
        {},
    ).items():

        text = safe_replace(
            text,
            old,
            new,
        )

    return text


# ============================================================
# IMPORT FIXES
# ============================================================


def fix_imports(
    text: str,
    config: Dict[str, Any],
    test_type: str,
) -> str:

    module_name = config["module_name"]

    class_name = config["class_name"]

    response_model = config[
        "response_model"
    ]

    search_response_model = config[
        "search_response_model"
    ]

    repo_import = config[
        "repo_import"
    ]

    service_import = config[
        "service_import"
    ]

    model_import = config[
        "model_import"
    ]

    # --------------------------------------------------------
    # Repository
    # --------------------------------------------------------

    if test_type == "db":

        text = re.sub(
            r"from\s+db\.repositories\s+import\s+[A-Za-z0-9_]+",
            f"from db.repositories import {module_name}_repo",
            text,
        )

    # --------------------------------------------------------
    # Model / Service
    # --------------------------------------------------------

    if test_type in (
        "model",
        "service",
    ):

        text = re.sub(
            r"from\s+domain\.services\.[A-Za-z0-9_]+\s+import",
            (
                f"from {service_import} import"
            ),
            text,
        )

        text = re.sub(
            r"from\s+domain\.models\.[A-Za-z0-9_]+\s+import",
            (
                f"from {model_import} import"
            ),
            text,
        )

    return text


# ============================================================
# LOOKUP FUNCTION REPLACEMENTS
# ============================================================


def apply_lookup_function_names(
    text: str,
    config: Dict[str, Any],
) -> str:

    lookup = config.get(
        "lookup",
        {},
    )

    if not lookup.get(
        "enabled",
        False,
    ):

        return text

    repo_function = lookup[
        "repo_function"
    ]

    service_function = lookup[
        "service_function"
    ]

    # Existing project_financial template names
    # may use either of these.

    old_repo_names = (

        "get_project_financial_by_id",

        "get_project_financial_details_by_id",

        "get_project_financial_by_project_id",
    )

    old_service_names = (

        "get_project_financial_details",

        "get_project_financial_by_project",

        "get_project_financial",
    )

    for old_name in old_repo_names:

        text = safe_replace(
            text,
            old_name,
            repo_function,
        )

    for old_name in old_service_names:

        text = safe_replace(
            text,
            old_name,
            service_function,
        )

    return text


# ============================================================
# SEARCH FUNCTION REPLACEMENTS
# ============================================================


def apply_search_function_names(
    text: str,
    config: Dict[str, Any],
) -> str:

    search_function = config[
        "search_function"
    ]

    repo_search_function = config[
        "repo_search_function"
    ]

    text = safe_replace(
        text,
        "search_project_financials",
        search_function,
    )

    text = safe_replace(
        text,
        "search_project_financial",
        search_function,
    )

    text = safe_replace(
        text,
        "get_project_financial",
        repo_search_function,
    )

    return text


# ============================================================
# GENERIC SERVICE TEST
# ============================================================
#
# The service test is where almost all of the problems
# have occurred.
#
# Rather than blindly copying the Project Financial
# expectations, generate service behavior based on config.
# ============================================================


def build_service_test(
    api_name: str,
    config: Dict[str, Any],
) -> str:

    module_name = config[
        "module_name"
    ]

    class_name = config[
        "class_name"
    ]

    response_model = config[
        "response_model"
    ]

    search_response_model = config[
        "search_response_model"
    ]

    search_function = config[
        "search_function"
    ]

    repo_search_function = config[
        "repo_search_function"
    ]

    lookup = config[
        "lookup"
    ]

    key_parameter = lookup[
        "key_parameter"
    ]

    sample_key = lookup[
        "sample_key"
    ]

    repo_lookup_function = lookup[
        "repo_function"
    ]

    service_lookup_function = lookup[
        "service_function"
    ]

    supports_lookup_filters = lookup.get(
        "supports_filters",
        False,
    )

    supports_lookup_page = lookup.get(
        "supports_page",
        True,
    )

    supports_lookup_sort = lookup.get(
        "supports_sort",
        True,
    )

    supports_lookup_columns = lookup.get(
        "supports_columns",
        True,
    )

    defaults = config.get(
        "defaults",
        {},
    )

    page_size = defaults.get(
        "page_size",
        100,
    )

    sort_field = defaults.get(
        "sort_field",
        key_parameter,
    )

    sort_order = defaults.get(
        "sort_order",
        "asc",
    )

    sample = config[
        "sample"
    ]

    sample_field = sample[
        "field"
    ]

    sample_value = sample[
        "value"
    ]

    second_value = sample.get(
        "second_value",
        sample_value + " 2",
    )

    # --------------------------------------------------------
    # Lookup repository assertion args
    # --------------------------------------------------------

    default_lookup_assertions = []

    default_lookup_assertions.append(
        f'    assert kwargs["{key_parameter}"] == "{sample_key}"'
    )

    if supports_lookup_page:

        default_lookup_assertions.extend(
            [
                "",
                '    assert isinstance(kwargs["page"], PaginationModel)',
                f'    assert kwargs["page"].limit == {page_size}',
            ]
        )

    if supports_lookup_sort:

        default_lookup_assertions.extend(
            [
                "",
                '    assert isinstance(kwargs["sort"], SortModel)',
                f'    assert kwargs["sort"].field == "{sort_field}"',
                f'    assert kwargs["sort"].order == "{sort_order}"',
            ]
        )

    if supports_lookup_columns:

        default_lookup_assertions.extend(
            [
                "",
                '    assert kwargs["columns"] is None',
            ]
        )

    if supports_lookup_filters:

        default_lookup_assertions.extend(
            [
                "",
                '    assert "filters" in kwargs',
            ]
        )

    default_lookup_assertions_text = "\n".join(
        default_lookup_assertions
    )

    # --------------------------------------------------------
    # Lookup call custom parameters
    # --------------------------------------------------------

    lookup_custom_args = [
        f'{key_parameter}="{sample_key}"',
    ]

    if supports_lookup_page:

        lookup_custom_args.append(
            "page=page"
        )

    if supports_lookup_sort:

        lookup_custom_args.append(
            "sort=sort"
        )

    if supports_lookup_columns:

        lookup_custom_args.append(
            "columns=columns"
        )

    if supports_lookup_filters:

        lookup_custom_args.append(
            "filters=filters"
        )

    lookup_custom_call = ",\n        ".join(
        lookup_custom_args
    )

    # --------------------------------------------------------
    # Custom assertion
    # --------------------------------------------------------

    custom_assertions = [
        f'    assert kwargs["{key_parameter}"] == "{sample_key}"',
    ]

    if supports_lookup_page:

        custom_assertions.extend(
            [
                '    assert kwargs["page"] == page',
                '    assert kwargs["page"].limit == 25',
                '    assert kwargs["page"].cursor == "current-cursor"',
            ]
        )

    if supports_lookup_sort:

        custom_assertions.extend(
            [
                '    assert kwargs["sort"] == sort',
                f'    assert kwargs["sort"].field == "{sample_field}"',
                '    assert kwargs["sort"].order == "asc"',
            ]
        )

    if supports_lookup_columns:

        custom_assertions.append(
            '    assert kwargs["columns"] == columns'
        )

    if supports_lookup_filters:

        custom_assertions.append(
            '    assert kwargs["filters"] == filters'
        )

    custom_assertions_text = "\n".join(
        custom_assertions
    )

    filter_setup = ""

    if supports_lookup_filters:

        filter_setup = f'''
    filters = FiltersEnvelope(
        filters={{
            "{sample_field}": FilterOps(
                eq="{sample_value}",
            )
        }}
    )
'''

    # --------------------------------------------------------
    # Complete generated file
    # --------------------------------------------------------

    return f'''"""
Unit tests for {module_name} service.

AUTO-GENERATED.

DO NOT EDIT THIS FILE DIRECTLY.

Update api_test_config.py or generate_api_tests.py instead.
"""

from unittest.mock import MagicMock

import pytest


from core.config import settings
from core.filters import (
    FiltersEnvelope,
    FilterOps,
    SortModel,
)
from core.pagination import PaginationModel


from db.repositories import {module_name}_repo


from domain.models.{module_name} import (
    {response_model},
    {search_response_model},
)


from domain.services.{module_name}_service import (
    {search_function},
    {service_lookup_function},
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def mock_{module_name}_repo(monkeypatch):

    search_mock = MagicMock()
    lookup_mock = MagicMock()

    monkeypatch.setattr(
        {module_name}_repo,
        "{repo_search_function}",
        search_mock,
    )

    monkeypatch.setattr(
        {module_name}_repo,
        "{repo_lookup_function}",
        lookup_mock,
    )

    repo = MagicMock()

    repo.{repo_search_function} = search_mock
    repo.{repo_lookup_function} = lookup_mock

    return repo


@pytest.fixture
def sample_{module_name}_dict():

    return {{
        "{key_parameter}": "{sample_key}",
        "{sample_field}": "{sample_value}",
    }}


# ============================================================
# SEARCH
# ============================================================


def test_search_{module_name}_no_filters(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_search_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    result = {search_function}(
        filters=None,
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_search_function}
        .call_args
        .kwargs
    )

    # None filters remain None.
    assert kwargs["filters"] is None

    assert isinstance(
        kwargs["page"],
        PaginationModel,
    )

    assert kwargs["page"].limit == {page_size}

    assert isinstance(
        kwargs["sort"],
        SortModel,
    )

    assert kwargs["sort"].field == "{sort_field}"
    assert kwargs["sort"].order == "{sort_order}"

    assert kwargs["columns"] is None

    assert len(result.items) == 1

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None


def test_search_{module_name}_dictionary_filter(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_search_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    result = {search_function}(
        filters={{
            "{sample_field}": {{
                "eq": "{sample_value}",
            }}
        }}
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_search_function}
        .call_args
        .kwargs
    )

    assert isinstance(
        kwargs["filters"],
        FiltersEnvelope,
    )

    assert (
        kwargs["filters"]
        .filters["{sample_field}"]
        .eq
        == "{sample_value}"
    )

    assert len(result.items) == 1


def test_search_{module_name}_existing_filter_envelope(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    envelope = FiltersEnvelope(
        filters={{
            "{sample_field}": FilterOps(
                eq="{sample_value}",
            )
        }}
    )

    mock_{module_name}_repo.{repo_search_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    {search_function}(
        filters=envelope,
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_search_function}
        .call_args
        .kwargs
    )

    assert kwargs["filters"] is envelope


def test_search_{module_name}_pagination_sort_columns(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_search_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": "next-cursor",
            "has_more": True,
        }},
    }}

    page = PaginationModel(
        limit=25,
        cursor="current-cursor",
    )

    sort = SortModel(
        field="{sample_field}",
        order="asc",
    )

    columns = [
        "{key_parameter}",
        "{sample_field}",
    ]

    result = {search_function}(
        filters=None,
        page=page,
        sort=sort,
        columns=columns,
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_search_function}
        .call_args
        .kwargs
    )

    assert kwargs["page"] == page
    assert kwargs["sort"] == sort
    assert kwargs["columns"] == columns

    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True


# ============================================================
# LOOKUP
# ============================================================


def test_{service_lookup_function}_success(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    second_record = sample_{module_name}_dict.copy()

    second_record["{sample_field}"] = (
        "{second_value}"
    )

    mock_{module_name}_repo.{repo_lookup_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
            second_record,
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    result = {service_lookup_function}(
        "{sample_key}"
    )

    assert len(result.items) == 2

    assert isinstance(
        result.items[0],
        {response_model},
    )

    assert (
        result.items[0].{key_parameter}
        == "{sample_key}"
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_lookup_function}
        .call_args
        .kwargs
    )

{default_lookup_assertions_text}

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_{service_lookup_function}_not_found(
    mock_{module_name}_repo,
):

    mock_{module_name}_repo.{repo_lookup_function}.return_value = {{
        "items": [],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    result = {service_lookup_function}(
        "NON-EXISTENT"
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False


def test_{service_lookup_function}_metadata_has_more_default(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_lookup_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": "xyz",
        }},
    }}

    result = {service_lookup_function}(
        "{sample_key}"
    )

    assert result.metadata.cursor == "xyz"
    assert result.metadata.has_more is False


def test_{service_lookup_function}_default_page_and_sort(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_lookup_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": None,
            "has_more": False,
        }},
    }}

    {service_lookup_function}(
        "{sample_key}"
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_lookup_function}
        .call_args
        .kwargs
    )

{default_lookup_assertions_text}


def test_{service_lookup_function}_pagination_sort_columns(
    mock_{module_name}_repo,
    sample_{module_name}_dict,
):

    mock_{module_name}_repo.{repo_lookup_function}.return_value = {{
        "items": [
            sample_{module_name}_dict,
        ],
        "page": {{
            "cursor": "next-cursor",
            "has_more": True,
        }},
    }}

    page = PaginationModel(
        limit=25,
        cursor="current-cursor",
    )

    sort = SortModel(
        field="{sample_field}",
        order="asc",
    )

    columns = [
        "{key_parameter}",
        "{sample_field}",
    ]
{filter_setup}
    result = {service_lookup_function}(
        {lookup_custom_call}
    )

    kwargs = (
        mock_{module_name}_repo
        .{repo_lookup_function}
        .call_args
        .kwargs
    )

{custom_assertions_text}

    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True
'''


# ============================================================
# TRANSFORM FILE
# ============================================================


def transform_template(
    api_name: str,
    config: Dict[str, Any],
    test_type: str,
) -> str:

    template_path = (
        TEMPLATE_FILES[test_type]
    )

    if not template_path.exists():

        raise FileNotFoundError(
            f"Missing template file: "
            f"{template_path}"
        )

    # --------------------------------------------------------
    # Service tests are generated structurally.
    #
    # This solves:
    #
    # filters=ANY mismatch
    # page=ANY mismatch
    # sort=None mismatch
    # limit/cursor mismatch
    # default PaginationModel mismatch
    # default SortModel mismatch
    # --------------------------------------------------------

    if test_type == "service":

        return build_service_test(
            api_name,
            config,
        )

    # --------------------------------------------------------
    # Other layers still use known-good template
    # --------------------------------------------------------

    text = template_path.read_text(
        encoding="utf-8"
    )

    text = apply_standard_replacements(
        text,
        api_name,
        config,
    )

    text = apply_lookup_function_names(
        text,
        config,
    )

    text = apply_search_function_names(
        text,
        config,
    )

    text = fix_imports(
        text,
        config,
        test_type,
    )

    header = f'''"""
AUTO-GENERATED UNIT TEST.

API:
    {api_name}

DO NOT EDIT THIS FILE DIRECTLY.

Update:

    api_test_config.py

or:

    generate_api_tests.py
"""

'''

    # Remove an existing initial docstring when convenient.
    # Keep template otherwise untouched.

    return (
        header
        + text
    )


# ============================================================
# VALIDATION
# ============================================================


def validate_config(
    api_name: str,
    config: Dict[str, Any],
) -> None:

    required = (

        "module_name",
        "class_name",

        "response_model",
        "search_response_model",

        "repo_import",
        "service_import",
        "model_import",

        "source_view",

        "search_function",
        "repo_search_function",

        "lookup",
        "defaults",
        "sample",
    )

    missing = [
        name
        for name in required
        if name not in config
    ]

    if missing:

        raise ValueError(
            f"{api_name}: missing configuration: "
            + ", ".join(missing)
        )

    lookup = config["lookup"]

    lookup_required = (

        "enabled",
        "key_column",
        "key_parameter",
        "sample_key",
        "repo_function",
        "service_function",
    )

    lookup_missing = [
        name
        for name in lookup_required
        if name not in lookup
    ]

    if lookup_missing:

        raise ValueError(
            f"{api_name}.lookup missing: "
            + ", ".join(lookup_missing)
        )


# ============================================================
# GENERATE ONE API
# ============================================================


def generate_api(
    api_name: str,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, int]:

    if api_name not in APIS:

        raise KeyError(
            f"Unknown API: {api_name}"
        )

    config = APIS[api_name]

    validate_config(
        api_name,
        config,
    )

    lookup = config["lookup"]

    print()
    print("=" * 78)
    print(
        f"Generating tests for API: "
        f"{api_name}"
    )
    print(
        f"Key column: "
        f"{lookup['key_column']}"
    )
    print(
        f"Key parameter: "
        f"{lookup['key_parameter']}"
    )
    print(
        f"Lookup repo function: "
        f"{lookup['repo_function']}"
    )
    print(
        f"Lookup service function: "
        f"{lookup['service_function']}"
    )
    print("=" * 78)

    generated = 0
    skipped = 0

    for test_type in TEST_TYPES:

        destination = destination_file(
            api_name,
            test_type,
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if (
            destination.exists()
            and not force
            and not dry_run
        ):

            print(
                f"SKIP   "
                f"[{test_type:<7}] "
                f"{destination}"
            )

            skipped += 1

            continue

        content = transform_template(
            api_name,
            config,
            test_type,
        )

        if dry_run:

            print(
                f"DRY    "
                f"[{test_type:<7}] "
                f"{destination}"
            )

            generated += 1

            continue

        destination.write_text(
            content,
            encoding="utf-8",
        )

        print(
            f"CREATE "
            f"[{test_type:<7}] "
            f"{destination}"
        )

        generated += 1

    print()
    print(
        f"Generated: {generated}"
    )

    print(
        f"Skipped:   {skipped}"
    )

    return (
        generated,
        skipped,
    )


# ============================================================
# LIST
# ============================================================


def list_apis() -> None:

    print()
    print("Configured APIs")
    print("=" * 78)

    if not APIS:

        print(
            "No APIs configured."
        )

        return

    for name, config in APIS.items():

        lookup = config.get(
            "lookup",
            {},
        )

        key = lookup.get(
            "key_column",
            "-",
        )

        function = lookup.get(
            "repo_function",
            "-",
        )

        print(
            f"{name:<30} "
            f"key={key:<20} "
            f"lookup={function}"
        )


# ============================================================
# VALIDATE TEMPLATE FILES
# ============================================================


def validate_templates() -> bool:

    missing = []

    for test_type in TEST_TYPES:

        # Service is structurally generated.
        # The service template doesn't technically have
        # to exist anymore.

        if test_type == "service":

            continue

        path = TEMPLATE_FILES[
            test_type
        ]

        if not path.exists():

            missing.append(
                (
                    test_type,
                    path,
                )
            )

    if not missing:

        return True

    print()
    print(
        "ERROR: Missing template files:"
    )

    for (
        test_type,
        path,
    ) in missing:

        print(
            f"  {test_type}: {path}"
        )

    return False


# ============================================================
# COMMAND LINE
# ============================================================


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Generate unit tests for APIs."
        )
    )

    parser.add_argument(
        "api",
        nargs="?",
        help=(
            "API name defined in "
            "api_test_config.py"
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "List configured APIs."
        ),
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Generate every configured API."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing tests."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show generated paths without "
            "writing files."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    args = parse_args()

    if args.list:

        list_apis()

        return

    if not validate_templates():

        sys.exit(1)

    if args.all:

        total_generated = 0
        total_skipped = 0

        for api_name in APIS:

            generated, skipped = (
                generate_api(
                    api_name,
                    force=args.force,
                    dry_run=args.dry_run,
                )
            )

            total_generated += generated
            total_skipped += skipped

        print()
        print("=" * 78)
        print(
            f"TOTAL GENERATED: "
            f"{total_generated}"
        )
        print(
            f"TOTAL SKIPPED:   "
            f"{total_skipped}"
        )
        print("=" * 78)

        return

    if not args.api:

        print(
            "ERROR: Supply an API name "
            "or use --list / --all."
        )

        print()
        print(
            "Example:"
        )

        print(
            "  py generate_api_tests.py "
            "po_funding_detail"
        )

        sys.exit(1)

    generate_api(
        args.api,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":

    main()
