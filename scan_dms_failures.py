"""
V1 handler routes for IrcCensusReport
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
# IRC CENSUS REPORT AUTHORIZATION
# =============================================================================

IRC_CENSUS_ALLOWED_USER = "HR - Special Use"


def _authorize_irc_census(event):
    """
    Restrict IRC Census Report endpoints to the dedicated
    HR - Special Use PAT identity.

    Normal PAT authentication happens in the API Gateway Lambda Authorizer.

    The authorizer validates the PAT against DynamoDB and passes the userId
    to the main Lambda through requestContext.authorizer.lambda.

    Only:
        userId = "HR - Special Use"

    is permitted to access IRC Census Report endpoints.
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
# GET IRC CENSUS REPORT BY ROW ID
# =============================================================================

@router.route(
    "GET",
    r"^/v1/irc-census-reports/(?P<row_id>[^/]+)$",
    is_regex=True,
)
@api_handler
def get_irc_census_report_v1(event, context):

    # -------------------------------------------------------------------------
    # Only HR - Special Use PAT is permitted.
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    row_id = LambdaUtils.get_path_param(
        event,
        "row_id",
    )

    if not row_id:
        raise ValueError(
            "IrcCensusReport ID is required."
        )

    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    results = get_irc_census_report_details(
        row_id=row_id,
        filters=filters_envelope,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    if not results.items:
        raise ResourceNotFoundError(
            message=f"IrcCensusReport with ID {row_id} not found",
            details={
                "row_id": row_id,
            },
        )

    results.metadata.applied_filters = filters_envelope

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

    # -------------------------------------------------------------------------
    # Only HR - Special Use PAT is permitted.
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    try:
        body = LambdaUtils.get_json_body(event)

    except json.JSONDecodeError:
        raise ValueError(
            "Invalid JSON body provided."
        )

    filters_data = body.get(
        "filters",
        {},
    )

    sort = SortModel(
        **body.get(
            "sort",
            {},
        )
    )

    page = PaginationModel(
        **body.get(
            "page",
            {},
        )
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = search_irc_census_reports(
        filters=filters_data,
        sort=sort,
        page=page,
        columns=columns,
    )

    results.metadata.applied_filters = FiltersEnvelope(
        filters=filters_data
    )

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
    # Only HR - Special Use PAT is permitted.
    # -------------------------------------------------------------------------
    _authorize_irc_census(event)

    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    filters_envelope = parse_filters_from_query_params(
        query_params,
        IRCCENSUSREPORT_FILTER_CONTEXT,
    )

    results = search_irc_census_reports(
        filters=filters_envelope,
        page=PaginationModel(
            limit=limit,
            cursor=cursor,
        ),
    )

    results.metadata.applied_filters = filters_envelope

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



python -m pytest tests -k "irc_census" -v
