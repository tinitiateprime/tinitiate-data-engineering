"""
Auto-generated V1 handler routes for EmployeeProfileComplete
"""

import json

from core.config import settings
from core.exceptions import ResourceNotFoundError
from core.filters import (
    FiltersEnvelope,
    SortModel,
    parse_filters_from_query_params,
)
from core.pagination import PaginationModel
from core.responses import api_handler
from core.utils import LambdaUtils

from domain.services.employee_profile_complete_service import (
    get_employee_profile_complete_details,
    search_employee_profile_completes,
)

from v1.logic import router

from v1.schemas.employee_profile_completes import (
    EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT,
    V1EmployeeProfileCompleteDetailResponseModel,
    V1EmployeeProfileCompleteListResponseModel,
    V1EmployeeProfileCompleteResponseModel,
    V1MetadataModel,
)


# ============================================================
# GET EMPLOYEE PROFILE COMPLETE BY EMPL_ID
# ============================================================

@router.route(
    "GET",
    r"/v1/employee-profile-complete/(?P<empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_profile_complete_v1(event, context):

    # --------------------------------------------------------
    # Path parameter
    # --------------------------------------------------------
    empl_id = LambdaUtils.get_path_param(event, "empl_id")

    if not empl_id:
        raise ValueError(
            "EmployeeProfileComplete empl_id is required."
        )

    # --------------------------------------------------------
    # Query parameters
    # --------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    columns = LambdaUtils.get_columns_query_parameter(event)

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT,
    )

    # --------------------------------------------------------
    # Service call
    #
    # IMPORTANT:
    # Service currently expects employee_key.
    # We pass the new API empl_id value into that existing
    # parameter so we do NOT break service/repo yet.
    # --------------------------------------------------------
    results = get_employee_profile_complete_details(
        employee_key=empl_id,
        filters=filters_envelope,
        limit=limit,
        cursor=cursor,
        columns=columns,
    )

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------
    if not results.items:
        raise ResourceNotFoundError(
            message=(
                f"EmployeeProfileComplete with empl_id "
                f"{empl_id} not found"
            ),
            details={
                "empl_id": empl_id,
            },
        )

    # --------------------------------------------------------
    # Applied filters
    # --------------------------------------------------------
    results.metadata.applied_filters = filters_envelope

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------
    response = V1EmployeeProfileCompleteDetailResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1EmployeeProfileCompleteResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# ============================================================
# SEARCH EMPLOYEE PROFILE COMPLETE
# ============================================================

@router.route(
    "POST",
    r"/v1/employee-profile-complete/search",
    is_regex=False,
)
@api_handler
def search_employee_profile_completes_v1(event, context):

    # --------------------------------------------------------
    # Request body
    # --------------------------------------------------------
    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    # --------------------------------------------------------
    # Search parameters
    # --------------------------------------------------------
    filters_data = body.get("filters", {})

    sort = SortModel(
        **body.get("sort", {})
    )

    page = PaginationModel(
        **body.get("page", {})
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    # --------------------------------------------------------
    # Service call
    # --------------------------------------------------------
    results = search_employee_profile_completes(
        filters=filters_data,
        sort=sort,
        page=page,
        columns=columns,
    )

    # --------------------------------------------------------
    # Applied filters
    # --------------------------------------------------------
    results.metadata.applied_filters = FiltersEnvelope(
        filters=filters_data
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------
    response = V1EmployeeProfileCompleteListResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1EmployeeProfileCompleteResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# ============================================================
# LIST EMPLOYEE PROFILE COMPLETE
# ============================================================

@router.route(
    "GET",
    r"/v1/employee-profile-complete",
    is_regex=False,
)
@api_handler
def list_employee_profile_completes_v1(event, context):

    # --------------------------------------------------------
    # Query parameters
    # --------------------------------------------------------
    query_params = LambdaUtils.get_all_query_params(event)

    limit = int(
        query_params.get(
            "limit",
            settings.DEFAULT_PAGE_SIZE,
        )
    )

    cursor = query_params.get("cursor")

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------
    filters_envelope = parse_filters_from_query_params(
        query_params,
        EMPLOYEEPROFILECOMPLETE_FILTER_CONTEXT,
    )

    # --------------------------------------------------------
    # Service call
    # --------------------------------------------------------
    results = search_employee_profile_completes(
        filters=filters_envelope,
        page=PaginationModel(
            limit=limit,
            cursor=cursor,
        ),
    )

    # --------------------------------------------------------
    # Applied filters
    # --------------------------------------------------------
    results.metadata.applied_filters = filters_envelope

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------
    response = V1EmployeeProfileCompleteListResponseModel(
        metadata=V1MetadataModel(
            **results.metadata.model_dump()
        ),
        data=[
            V1EmployeeProfileCompleteResponseModel.model_validate(item)
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)
