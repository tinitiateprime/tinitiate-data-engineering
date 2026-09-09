"""
V1 handler routes for IrcCensusReport.
"""

import json

from core.config import settings
from core.exceptions import ResourceNotFoundError, UnauthorizedError
from core.filters import (
    FiltersEnvelope,
    SortModel,
    parse_filters_from_query_params,
)
from core.pagination import PaginationModel
from core.responses import api_handler
from core.utils import LambdaUtils

from domain.services.irc_census_report_service import (
    get_irc_census_report_details,
    search_irc_census_reports,
)

from v1.logic import router

from v1.schemas.irc_census_reports import (
    IRCCENSUSREPORT_FILTER_CONTEXT,
    V1IrcCensusReportDetailResponseModel,
    V1IrcCensusReportListResponseModel,
    V1IrcCensusReportResponseModel,
    V1MetadataModel,
)


# =============================================================================
# AUTHORIZATION
# =============================================================================

def _authorize_irc_census(event):
    """
    IRC Census Report is restricted to the HR - Special Use PAT.
    """

    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}

    lambda_context = authorizer.get("lambda") or authorizer

    user_id = (
        lambda_context.get("userId")
        or lambda_context.get("user_id")
        or lambda_context.get("userid")
    )

    if user_id != "HR - Special Use":
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )


# =============================================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME
# =============================================================================
#
# Example:
#
# /v1/irc-census-reports/Price%2C%20Kevin%20T
#
# Router extracts:
#
# last_first_name = "Price, Kevin T"
#
# =============================================================================

@router.route(
    "GET",
    r"/v1/irc-census-reports/(?P<last_first_name>[^/]+)",
    is_regex=True,
)
@api_handler
def get_irc_census_report_v1(event, context):

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Get LAST_FIRST_NAME from route
    # -------------------------------------------------------------------------
    last_first_name = LambdaUtils.get_path_param(
        event,
        "last_first_name",
    )

    if not last_first_name:
        raise ValueError(
            "IrcCensusReport last_first_name is required."
        )

    # -------------------------------------------------------------------------
    # Query parameters
    # -------------------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    # -------------------------------------------------------------------------
    # Additional filters
    # -------------------------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    # -------------------------------------------------------------------------
    # Service
    #
    # IMPORTANT:
    # Lookup is by LAST_FIRST_NAME.
    # row_id remains only the technical pagination key.
    # -------------------------------------------------------------------------
    results = get_irc_census_report_details(
        last_first_name=last_first_name,
        filters=filters_envelope,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    # -------------------------------------------------------------------------
    # Not found
    # -------------------------------------------------------------------------
    if not results.items:
        raise ResourceNotFoundError(
            message=(
                f"IrcCensusReport with last_first_name "
                f"'{last_first_name}' not found"
            ),
            details={
                "last_first_name": last_first_name,
            },
        )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------
    results.metadata.applied_filters = filters_envelope

    # -------------------------------------------------------------------------
    # Response
    # -------------------------------------------------------------------------
    response = V1IrcCensusReportDetailResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1IrcCensusReportResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(
        by_alias=True
    )


# =============================================================================
# SEARCH IRC CENSUS REPORT
# =============================================================================

@router.route(
    "POST",
    r"/v1/irc-census-reports/search",
    is_regex=False,
)
@api_handler
def search_irc_census_reports_v1(event, context):

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Body
    # -------------------------------------------------------------------------
    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError(
            "Invalid JSON body provided."
        )

    body = body or {}

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    filters_data = body.get(
        "filters",
        {},
    )

    # -------------------------------------------------------------------------
    # Sort
    # -------------------------------------------------------------------------
    sort = SortModel(
        **body.get(
            "sort",
            {},
        )
    )

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    page = PaginationModel(
        **body.get(
            "page",
            {},
        )
    )

    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------
    columns = LambdaUtils.get_columns_query_parameter(event)

    # -------------------------------------------------------------------------
    # Service
    # -------------------------------------------------------------------------
    results = search_irc_census_reports(
        filters=filters_data,
        sort=sort,
        page=page,
        columns=columns,
    )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------
    results.metadata.applied_filters = FiltersEnvelope(
        filters=filters_data
    )

    # -------------------------------------------------------------------------
    # Response
    # -------------------------------------------------------------------------
    response = V1IrcCensusReportListResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1IrcCensusReportResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(
        by_alias=True
    )


# =============================================================================
# LIST IRC CENSUS REPORTS
# =============================================================================

@router.route(
    "GET",
    r"/v1/irc-census-reports",
    is_regex=False,
)
@api_handler
def list_irc_census_reports_v1(event, context):

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Query parameters
    # -------------------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    # -------------------------------------------------------------------------
    # Service
    # -------------------------------------------------------------------------
    results = search_irc_census_reports(
        filters=filters_envelope,
        page=PaginationModel(
            limit=limit,
            cursor=cursor,
        ),
    )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------
    results.metadata.applied_filters = filters_envelope

    # -------------------------------------------------------------------------
    # Response
    # -------------------------------------------------------------------------
    response = V1IrcCensusReportListResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1IrcCensusReportResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(
        by_alias=True
    )
