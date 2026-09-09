"""
V1 handler routes for IrcCensusReport
"""

import hashlib
import hmac
import json
import os

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
# IRC CENSUS REPORT - DEDICATED PAT AUTHORIZATION
# =============================================================================

def _authorize_irc_census_pat(event):
    """
    Restrict IRC Census Report endpoints to exactly one dedicated PAT.

    Normal PAT authentication is already performed by the API Gateway
    Lambda authorizer.

    This additional check ensures that only the specifically configured
    IRC Census PAT can access these endpoints.

    The clear-text PAT is never stored in Lambda configuration.

    Environment variable required:

        IRC_CENSUS_PAT_HASH=<SHA256 hash of permitted PAT>
    """

    headers = event.get("headers") or {}

    # API Gateway can provide header keys with different casing.
    auth_header = (
        headers.get("authorization")
        or headers.get("Authorization")
        or ""
    ).strip()

    if not auth_header:
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )

    parts = auth_header.split()

    # Support:
    # Authorization: Bearer mt-dm-xxxx
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1].strip()

    # Also support:
    # Authorization: mt-dm-xxxx
    elif len(parts) == 1:
        token = parts[0].strip()

    else:
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )

    if not token:
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )

    # -------------------------------------------------------------------------
    # This endpoint must be PAT-only.
    #
    # Your Lambda authorizer identifies application PATs by mt-dm- prefix.
    # This also prevents an Okta JWT from being used for this restricted API.
    # -------------------------------------------------------------------------
    if not token.startswith("mt-dm-"):
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )

    # -------------------------------------------------------------------------
    # Hash the incoming PAT exactly the same way as the Lambda Authorizer.
    # -------------------------------------------------------------------------
    actual_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    # -------------------------------------------------------------------------
    # Load the ONLY permitted PAT hash from Lambda environment configuration.
    # -------------------------------------------------------------------------
    expected_hash = os.environ.get(
        "IRC_CENSUS_PAT_HASH",
        "",
    ).strip()

    # Fail closed if configuration is missing.
    if not expected_hash:
        raise UnauthorizedError(
            message="Forbidden",
            status_code=403,
        )

    # -------------------------------------------------------------------------
    # Constant-time comparison.
    # -------------------------------------------------------------------------
    if not hmac.compare_digest(
        actual_hash,
        expected_hash,
    ):
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

    # Only the dedicated IRC Census PAT is allowed.
    _authorize_irc_census_pat(event)

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

    # Only the dedicated IRC Census PAT is allowed.
    _authorize_irc_census_pat(event)

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

    # Only the dedicated IRC Census PAT is allowed.
    _authorize_irc_census_pat(event)

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
