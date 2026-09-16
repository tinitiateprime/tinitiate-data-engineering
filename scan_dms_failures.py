"""
V1 handler routes for IrcCensusReport.
"""

import json
from urllib.parse import unquote

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

IRC_CENSUS_ALLOWED_USER = "HR - Special Use"


def _authorize_irc_census(event):
    """
    Only the HR - Special Use PAT is permitted to access
    IRC Census Report endpoints.
    """

    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}

    # HTTP API Lambda Authorizer context.
    lambda_context = authorizer.get("lambda") or {}

    user_id = lambda_context.get("userId")

    # Defensive fallback in case userId is presented directly
    # under requestContext.authorizer in another event format.
    if not user_id:
        user_id = authorizer.get("userId")

    if user_id != IRC_CENSUS_ALLOWED_USER:
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )


# =============================================================================
# PATH HELPER
# =============================================================================

def _get_last_first_name(event):
    """
    Resolve LAST_FIRST_NAME from the request.

    Primary:
        pathParameters.last_first_name

    Fallbacks:
        pathParameters.id
        pathParameters.name
        rawPath/path

    Example URL:

        /v1/irc-census-reports/Price%2C%20Kevin%20T

    Returns:

        Price, Kevin T
    """

    # -------------------------------------------------------------------------
    # First try the framework helper.
    # -------------------------------------------------------------------------
    last_first_name = (
        LambdaUtils.get_path_param(event, "last_first_name")
        or LambdaUtils.get_path_param(event, "id")
        or LambdaUtils.get_path_param(event, "name")
    )

    if last_first_name:
        return unquote(str(last_first_name)).strip()

    # -------------------------------------------------------------------------
    # Next check pathParameters directly.
    # -------------------------------------------------------------------------
    path_parameters = event.get("pathParameters") or {}

    last_first_name = (
        path_parameters.get("last_first_name")
        or path_parameters.get("id")
        or path_parameters.get("name")
    )

    if last_first_name:
        return unquote(str(last_first_name)).strip()

    # -------------------------------------------------------------------------
    # Final fallback:
    # extract employee name directly from rawPath/path.
    #
    # Handles:
    #
    #   /v1/irc-census-reports/Price%2C%20Kevin%20T
    #
    # and:
    #
    #   /dev/v1/irc-census-reports/Price%2C%20Kevin%20T
    # -------------------------------------------------------------------------
    raw_path = (
        event.get("rawPath")
        or event.get("path")
        or ""
    )

    # Remove query string defensively.
    raw_path = raw_path.split("?", 1)[0]

    marker = "/v1/irc-census-reports/"

    if marker in raw_path:
        value = raw_path.split(marker, 1)[1]

        # Remove a trailing slash if present.
        value = value.strip("/")

        if value:
            return unquote(value).strip()

    return None


# =============================================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME
# =============================================================================

@router.route(
    "GET",
    r"/v1/irc-census-reports/(?P<last_first_name>[^/]+)",
    is_regex=True,
)
@api_handler
def get_irc_census_report_v1(event, context):
    """
    Get IRC Census Report records for a specific LAST_FIRST_NAME.

    Example:

        GET /v1/irc-census-reports/Price%2C%20Kevin%20T

    Employee lookup:
        last_first_name

    Technical pagination key:
        row_id
    """

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Employee name
    # -------------------------------------------------------------------------
    last_first_name = _get_last_first_name(event)

    if not last_first_name:
        raise ValueError(
            "last_first_name is required."
        )

    # -------------------------------------------------------------------------
    # Query parameters
    # -------------------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event) or {}

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
    # Service call
    # IMPORTANT:
    # last_first_name is the employee lookup key.
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
    # API response
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
# SEARCH IRC CENSUS REPORTS
# =============================================================================

@router.route(
    "POST",
    r"/v1/irc-census-reports/search",
    is_regex=False,
)
@api_handler
def search_irc_census_reports_v1(event, context):
    """
    Search IRC Census Reports using filters, sorting and pagination.
    """

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Request body
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
    # Applied filters
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
    """
    List IRC Census Reports.

    Examples:

        GET /v1/irc-census-reports

        GET /v1/irc-census-reports?limit=50
    """

    # -------------------------------------------------------------------------
    # Authorization
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    # -------------------------------------------------------------------------
    # Query parameters
    # -------------------------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event) or {}

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    page = PaginationModel(
        limit=limit,
        cursor=cursor,
    )

    # -------------------------------------------------------------------------
    # Service
    # -------------------------------------------------------------------------
    results = search_irc_census_reports(
        filters=filters_envelope,
        page=page,
        columns=columns,
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
