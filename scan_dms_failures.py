# main-function\mt-dm-lambda-src\v1\handlers\employees_synth.py
import json

from core.config import settings
from core.exceptions import ResourceNotFoundError
from core.filters import SortModel
from core.pagination import PaginationModel
from core.responses import api_handler
from core.utils import LambdaUtils
from domain.services.employee_profile_synth_service import (
    get_all_employees,
    get_direct_reports,
    get_employee_by_id,
    get_employees_by_clearance,
    get_employees_in_org,
    get_personnel_roster,
)
from v1.logic import router
from v1.schemas.employees import (
    V1EmployeeListResponseModel,
    V1EmployeeResponseModel,
    V1MetadataModel,
)


@router.route("POST", r"/v1/employees/synth/profiles/search", is_regex=False)
@api_handler
def search_employee_profiles_synth_v1(event, context):
    """
    Search for employee profiles in the synth database.

    Args:
        event: Lambda event containing JSON body with 'filters', 'sort', 'page', and 'columns'.
        context: Lambda context.

    Returns:
        Dict containing metadata (cursor, filters, count) and the list of employee profiles.
    """
    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    filters_dict = body.get("filters", {})
    sort = SortModel(**body.get("sort", {}))
    page = PaginationModel(**body.get("page", {}))
    columns = body.get("columns")

    results = get_all_employees(
        filters=filters_dict, sort=sort, page=page, columns=columns
    )

    if not results.items:
        raise ResourceNotFoundError(
            message="Employees with filters not found",
            details={"filters": filters_dict},
        )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


@router.route("POST", r"/v1/employees/synth/profiles/roster", is_regex=False)
@api_handler
def get_personnel_roster_synth_v1(event, context):
    """
    Retrieve the personnel roster (alpha-report fields) via POST search, from the synth database.

    Args:
        event: Lambda event containing JSON body with 'filters', 'sort', 'page', and 'columns'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of personnel-roster records.
    """
    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    filters_dict = body.get("filters", {})
    sort = SortModel(**body.get("sort", {}))
    page = PaginationModel(**body.get("page", {}))
    columns = body.get("columns")

    results = get_personnel_roster(
        filters=filters_dict, sort=sort, page=page, columns=columns
    )

    # Note: no 404 on empty - a bulk sync feed legitimately returns [] and the
    # caller expects a 200 with an empty data array. Matches the mtdm endpoint.
    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


@router.route(
    "GET", r"/v1/employees/synth/profiles/manager/?$", is_regex=True
)
@api_handler
def get_employee_direct_reports_blank_synth_v1(event, context):
    """
    Handle requests to the synth direct reports endpoint missing an ID.
    Raises:
        ValueError: Always, as manager ID is a required path parameter.
    """
    err = ValueError("Manager ID Missing.")
    err.add_note(
        "Manager ID is required, e.g. /v1/employees/synth/profiles/manager/12345"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/synth/profiles/manager/(?P<mgr_empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_direct_reports_synth_v1(event, context):
    """
    Retrieve direct reports for a specific manager, from the synth database.

    Args:
        event: Lambda event containing 'mgr_empl_id' path parameter and optional query params
               for 'limit', 'cursor', 'sortField', and 'sortOrder'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of direct reports.
    """
    mgr_empl_id = LambdaUtils.get_path_param(event, "mgr_empl_id")
    query_params = LambdaUtils.get_all_query_params(event)

    # Quick exit required parameter is missing for this route
    if not mgr_empl_id:
        raise ValueError("Manager Employee ID is required.")

    page = PaginationModel(
        limit=int(query_params.get("limit", settings.DEFAULT_PAGE_SIZE)),
        cursor=query_params.get("cursor"),
    )
    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_direct_reports(
        mgr_empl_id=mgr_empl_id, page=page, sort=sort, columns=columns
    )

    if not results.items:
        raise ResourceNotFoundError(
            message=f"Employees with Manager ID {mgr_empl_id} not found.",
            details={"mgr_empl_id": mgr_empl_id},
        )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


@router.route("GET", r"/v1/employees/synth/profiles/org/?$", is_regex=True)
@api_handler
def get_org_blank_synth_v1(event, context):
    """
    Handle requests to the synth organization profiles endpoint missing an ID.
    Raises:
        ValueError: Always, as organization ID is a required path parameter.
    """
    err = ValueError("Organization ID is Missing.")
    err.add_note(
        "Organization ID is required, e.g. /v1/employees/synth/profiles/org/01.626.N32.10"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/synth/profiles/org/(?P<org_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employees_by_org_synth_v1(event, context):
    """
    Retrieve all employees belonging to a specific organization, from the synth database.

    Args:
        event: Lambda event containing 'org_id' path parameter and optional query params
               for pagination and sorting.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of employees in the organization.
    """
    org_id = LambdaUtils.get_path_param(event, "org_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not org_id:
        err = ValueError("Organization ID Missing.")
        err.add_note(
            "Organization ID is required, e.g. /v1/employees/synth/profiles/org/01.626.N32.10"
        )
        raise err

    page = PaginationModel(
        limit=int(query_params.get("limit", settings.DEFAULT_PAGE_SIZE)),
        cursor=query_params.get("cursor"),
    )
    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )
    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employees_in_org(org_id=org_id, page=page, sort=sort, columns=columns)

    if not results.items:
        raise ResourceNotFoundError(
            message=f"Employees with Org ID {org_id} not found.",
            details={"org_id": org_id},
        )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


@router.route(
    "GET", r"/v1/employees/synth/profiles/clearance/?$", is_regex=True
)
@api_handler
def get_employees_by_clearance_blank_synth_v1(event, context):
    """
    Handle requests to the synth clearance profiles endpoint missing a clearance status.
    Raises:
        ValueError: Always, as clearance status is a required path parameter.
    """
    err = ValueError("Clearance Status is Missing.")
    err.add_note(
        "Clearance Status is required, e.g. /v1/employees/synth/profiles/clearance/active"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/synth/profiles/clearance/(?P<status>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employees_by_clearance_synth_v1(event, context):
    """
    Retrieve employees filtered by their clearance status, from the synth database.

    Args:
        event: Lambda event containing 'status' path parameter and optional query params
               for pagination and sorting.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of matching employees.
    """
    status = LambdaUtils.get_path_param(event, "status")
    query_params = LambdaUtils.get_all_query_params(event)

    if not status:
        raise ValueError("Clearance status is required.")

    page = PaginationModel(
        limit=int(query_params.get("limit", settings.DEFAULT_PAGE_SIZE)),
        cursor=query_params.get("cursor"),
    )
    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )
    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employees_by_clearance(
        clearance_status=status, page=page, sort=sort, columns=columns
    )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


@router.route("GET", r"/v1/employees/synth/profiles/?$", is_regex=True)
@api_handler
def get_employee_profile_blank_synth_v1(event, context):
    """Handle requests to the synth employee profiles endpoint missing an employee id."""
    err = ValueError("Employee ID is Missing.")
    err.add_note("Employee ID is required, e.g. /v1/employees/synth/profiles/12345")
    raise err


@router.route(
    "GET",
    r"/v1/employees/synth/profiles/(?P<empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_profile_synth_v1(event, context):
    """
    Retrieve a single employee's profile by their employee ID, from the synth database.

    Args:
        event: Lambda event containing 'empl_id' path parameter.
        context: Lambda context.

    Returns:
        Dict containing metadata and the employee profile data.
    """
    empl_id = LambdaUtils.get_path_param(event, "empl_id")
    if not empl_id:
        raise ValueError(
            "Employee ID is required as path parameter. e.g. /v1/employees/synth/profiles/E12345."
        )
    elif empl_id == "search":
        # Protects for accidental GET when it's more likely they wanted to POST
        raise ValueError(
            "Employee ID sent as 'search', did you mean to POST? "
            "/v1/employees/synth/profiles/search"
        )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employee_by_id(empl_id=empl_id, columns=columns)

    if not results.items:
        raise ResourceNotFoundError(
            message=f"Employee with ID {empl_id} not found",
            details={"empl_id": empl_id, "columns": columns},
        )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)
