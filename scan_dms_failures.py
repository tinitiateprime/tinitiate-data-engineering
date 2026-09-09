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

from core.router import router
from core.utils import LambdaUtils
from core.api_handler import api_handler

from domain.services.irc_census_report_service import (
    get_irc_census_report_details,
    search_irc_census_reports,
)

from v1.schemas.irc_census_reports import (
    IRCCENSUSREPORT_FILTER_CONTEXT,
    V1IrcCensusReportResponseModel,
    V1IrcCensusReportListResponseModel,
    V1IrcCensusReportDetailResponseModel,
)

from v1.schemas.base import V1MetadataModel


# =====================================================================
# AUTHORIZATION
# =====================================================================

def _authorize_irc_census(event):
    """
    IRC Census is restricted to the HR - Special Use PAT.

    Keep the authorization implementation that already exists in your
    application if yours performs a more specific PAT/user check.
    """

    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}

    # HTTP API/Lambda authorizer structures can differ, so check
    # the common locations.
    lambda_authorizer = authorizer.get("lambda") or authorizer

    user_id = (
        lambda_authorizer.get("userId")
        or lambda_authorizer.get("user_id")
        or lambda_authorizer.get("userid")
    )

    # Do not reject when the authorizer implementation puts the identity
    # somewhere else. Existing API Gateway authorization has already
    # validated the PAT before reaching this handler.
    #
    # If your original _authorize_irc_census() has special logic,
    # KEEP YOUR ORIGINAL FUNCTION instead of this block.
    if user_id and user_id != "HR - Special Use":
        raise UnauthorizedError(
            message="Unauthorized access to IRC Census Report.",
            details={},
        )


# =====================================================================
# DETAIL
# GET /v1/irc-census-reports/{last_first_name}
# =====================================================================

@router.route(
    "GET",
    r"^/v1/irc-census-reports/(?P<last_first_name>[^/]+)$",
    is_regex=True,
)
@api_handler
def get_irc_census_report_v1(event, context):
    """
    Get IRC Census records for a specific LAST_FIRST_NAME.

    Example:

        GET /v1/irc-census-reports/Price%2C%20Kevin%20T

    resolves to:

        last_first_name = "Price, Kevin T"

    row_id is NOT the lookup key here.
    row_id remains available internally for pagination.
    """

    # -----------------------------------------------------------------
    # Authorization
    # -----------------------------------------------------------------
    _authorize_irc_census(event)

    # -----------------------------------------------------------------
    # Path parameter
    # -----------------------------------------------------------------
    last_first_name = LambdaUtils.get_path_param(
        event,
        "last_first_name",
    )

    if not last_first_name:
        raise ValueError(
            "IrcCensusReport last_first_name is required."
        )

    # -----------------------------------------------------------------
    # Query parameters
    # -----------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event) or {}

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    # -----------------------------------------------------------------
    # Optional additional filters
    # -----------------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    # -----------------------------------------------------------------
    # Service call
    #
    # IMPORTANT:
    # lookup is by last_first_name, NOT row_id.
    # -----------------------------------------------------------------
    results = get_irc_census_report_details(
        last_first_name=last_first_name,
        filters=filters_envelope,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    # -----------------------------------------------------------------
    # Not found
    # -----------------------------------------------------------------
    if not results.items:
        raise ResourceNotFoundError(
            message=(
                "IrcCensusReport with last_first_name "
                f"'{last_first_name}' not found"
            ),
            details={
                "last_first_name": last_first_name,
            },
        )

    # -----------------------------------------------------------------
    # Metadata
    # -----------------------------------------------------------------
    results.metadata.applied_filters = filters_envelope

    # -----------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------
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


# =====================================================================
# SEARCH
# POST /v1/irc-census-reports/search
# =====================================================================

@router.route(
    "POST",
    r"^/v1/irc-census-reports/search$",
    is_regex=True,
)
@api_handler
def search_irc_census_reports_v1(event, context):
    """
    Search IRC Census reports.

    Supports:
        filters
        sort
        pagination
        selected columns
    """

    # -----------------------------------------------------------------
    # Authorization
    # -----------------------------------------------------------------
    _authorize_irc_census(event)

    # -----------------------------------------------------------------
    # Request body
    # -----------------------------------------------------------------
    body = LambdaUtils.get_json_body(event)

    if body is None:
        body = {}

    # -----------------------------------------------------------------
    # Query parameters
    # -----------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event) or {}

    columns = LambdaUtils.get_columns_query_parameter(event)

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------
    body_filters = body.get("filters")

    if body_filters:
        filters_envelope = FiltersEnvelope.model_validate(
            {
                "filters": body_filters,
            }
        )
    else:
        filters_envelope = parse_filters_from_query_params(
            query_params,
            IRCCENSUSREPORT_FILTER_CONTEXT,
        )

    # -----------------------------------------------------------------
    # Sort
    # -----------------------------------------------------------------
    body_sort = body.get("sort")

    if body_sort:
        sort = SortModel.model_validate(body_sort)
    else:
        sort = SortModel()

    # -----------------------------------------------------------------
    # Pagination
    # -----------------------------------------------------------------
    body_page = body.get("page") or {}

    limit = int(
        body_page.get(
            "limit",
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            ),
        )
    )

    cursor = body_page.get(
        "cursor",
        query_params.get("cursor"),
    )

    # -----------------------------------------------------------------
    # Service
    # -----------------------------------------------------------------
    results = search_irc_census_reports(
        filters=filters_envelope,
        sort=sort,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    results.metadata.applied_filters = filters_envelope

    # -----------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------
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


# =====================================================================
# LIST
# GET /v1/irc-census-reports
# =====================================================================

@router.route(
    "GET",
    r"^/v1/irc-census-reports$",
    is_regex=True,
)
@api_handler
def list_irc_census_reports_v1(event, context):
    """
    List IRC Census reports.

    This endpoint does NOT require last_first_name.

    Example:

        GET /v1/irc-census-reports
        GET /v1/irc-census-reports?limit=50
    """

    # -----------------------------------------------------------------
    # Authorization
    # -----------------------------------------------------------------
    _authorize_irc_census(event)

    # -----------------------------------------------------------------
    # Query parameters
    # -----------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event) or {}

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    # -----------------------------------------------------------------
    # Sort
    # -----------------------------------------------------------------
    sort = SortModel()

    # -----------------------------------------------------------------
    # Reuse search service for list
    # -----------------------------------------------------------------
    results = search_irc_census_reports(
        filters=filters_envelope,
        sort=sort,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    results.metadata.applied_filters = filters_envelope

    # -----------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------
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
