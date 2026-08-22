"""
V1 employee handlers.
"""

import json

from core.config import settings
from core.exceptions import ResourceNotFoundError
from core.filters import SortModel
from core.pagination import PaginationModel
from core.responses import api_handler
from core.utils import LambdaUtils

from domain.services import (
    get_all_certifications,
    get_all_employees,
    get_all_training,
    get_certifications_by_employee,
    get_certifications_by_org,
    get_certifications_by_status,
    get_direct_reports,
    get_employee_by_id,
    get_employees_by_clearance,
    get_employees_in_org,
    get_personnel_roster,
    get_training_by_employee,
    get_training_by_org,
    get_training_by_status,
    get_training_by_type,
)

from pydantic import ValidationError
from v1.logic import router
from v1.schemas.employees import (
    EMPLOYEE_CERTIFICATION_FILTER_CONTEXT,
    EMPLOYEE_FILTER_CONTEXT,
    V1EmployeeCertificationListResponseModel,
    V1EmployeeCertificationResponseModel,
    V1EmployeeListResponseModel,
    V1EmployeePathParams,
    V1EmployeeResponseModel,
    V1EmployeeTrainingListResponseModel,
    V1EmployeeTrainingResponseModel,
    V1MetadataModel,
)


# =============================================================================
# EMPLOYEE PROFILE SEARCH
# =============================================================================

@router.route(
    "POST",
    r"/v1/employees/profiles/search",
    is_regex=False,
)
@api_handler
def search_employee_profiles_v1(event, context):
    """
    Search for employee profiles.

    Args:
        event: Lambda event containing JSON body with
               'filters', 'sort', 'page', and 'columns'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of employee profiles.
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
        filters=filters_dict,
        sort=sort,
        page=page,
        columns=columns,
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


# =============================================================================
# PERSONNEL ROSTER
# =============================================================================

@router.route(
    "POST",
    r"/v1/employees/profiles/roster",
    is_regex=False,
)
@api_handler
def get_personnel_roster_v1(event, context):
    """
    Retrieve the personnel roster (alpha-report fields) via POST search.

    Args:
        event: Lambda event containing JSON body with
               'filters', 'sort', 'page', and 'columns'.
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
        filters=filters_dict,
        sort=sort,
        page=page,
        columns=columns,
    )

    # No 404 on empty - bulk sync feed.
    # The caller expects a 200 with an empty data array.
    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# DIRECT REPORTS
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/profiles/manager/?$",
    is_regex=True,
)
@api_handler
def get_employee_direct_reports_blank_v1(event, context):
    """
    Handle requests to the employee direct reports endpoint missing an ID.

    Raises:
        ValueError: Always, as manager ID is a required path parameter.
    """

    err = ValueError("Manager ID Missing.")
    err.add_note(
        "Manager ID is required, e.g. /v1/employees/profiles/manager/12345"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/profiles/manager/(?P<mgr_empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_direct_reports_v1(event, context):
    """
    Retrieve direct reports for a specific manager.

    Args:
        event: Lambda event containing 'mgr_empl_id' path parameter and
               optional query params for 'limit', 'cursor',
               'sortField', and 'sortOrder'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of direct reports.
    """

    mgr_empl_id = LambdaUtils.get_path_param(event, "mgr_empl_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not mgr_empl_id:
        raise ValueError("Manager Employee ID is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_direct_reports(
        mgr_empl_id=mgr_empl_id,
        page=page,
        sort=sort,
        columns=columns,
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


# =============================================================================
# EMPLOYEES BY ORGANIZATION
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/profiles/org/?$",
    is_regex=True,
)
@api_handler
def get_org_blank_v1(event, context):
    """
    Handle requests to the organization profiles endpoint missing an ID.

    Raises:
        ValueError: Always, as organization ID is a required path parameter.
    """

    err = ValueError("Organization ID is Missing.")
    err.add_note(
        "Organization ID is required, e.g. "
        "/v1/employees/profiles/org/01.626.N32.10"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/profiles/org/(?P<org_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employees_by_org_v1(event, context):
    """
    Retrieve all employees belonging to a specific organization.

    Args:
        event: Lambda event containing 'org_id' path parameter and
               optional query params for pagination and sorting.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of employees in the organization.
    """

    org_id = LambdaUtils.get_path_param(event, "org_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not org_id:
        err = ValueError("Organization ID Missing.")
        err.add_note(
            "Organization ID is required, e.g. "
            "/v1/employees/profiles/org/01.626.N32.10"
        )
        raise err

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employees_in_org(
        org_id=org_id,
        page=page,
        sort=sort,
        columns=columns,
    )

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


# =============================================================================
# EMPLOYEES BY CLEARANCE
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/profiles/clearance/?$",
    is_regex=True,
)
@api_handler
def get_employees_by_clearance_blank_v1(event, context):
    """
    Handle requests to the clearance profiles endpoint missing a clearance
    status.

    Raises:
        ValueError: Always.
    """

    err = ValueError("Clearance Status is Missing.")
    err.add_note(
        "Clearance Status is required, e.g. "
        "/v1/employees/profiles/clearance/active"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/profiles/clearance/(?P<status>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employees_by_clearance_v1(event, context):
    """
    Retrieve employees filtered by their clearance status.

    Args:
        event: Lambda event containing 'status' path parameter and
               optional query params for pagination and sorting.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of matching employees.
    """

    status = LambdaUtils.get_path_param(event, "status")
    query_params = LambdaUtils.get_all_query_params(event)

    if not status:
        raise ValueError("Clearance status is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "LAST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employees_by_clearance(
        clearance_status=status,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# EMPLOYEE BY ID
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/profiles/?$",
    is_regex=True,
)
@api_handler
def get_employee_profile_blank_v1(event, context):
    """
    Handle requests to the employee profiles endpoint missing an employee ID.
    """

    err = ValueError("Employee ID is Missing.")
    err.add_note(
        "Employee ID is required, e.g. /v1/employees/profiles/12345"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/profiles/(?P<empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_profile_v1(event, context):
    """
    Retrieve a single employee's profile by employee ID.

    Args:
        event: Lambda event containing 'empl_id' path parameter.
        context: Lambda context.

    Returns:
        Dict containing metadata and employee profile data.
    """

    empl_id = LambdaUtils.get_path_param(event, "empl_id")

    if not empl_id:
        raise ValueError(
            "Employee ID is required as path parameter, "
            "e.g. /v1/employees/profiles/12345."
        )
    elif empl_id == "search":
        # Protects against accidental GET when caller likely wanted POST
        # /v1/employees/profiles/search.
        raise ValueError(
            "Employee ID sent as 'search'; did you mean to POST?"
        )
    else:
        try:
            validated_params = V1EmployeePathParams(empl_id=empl_id)
            clean_empl_id = validated_params.empl_id
        except ValidationError as e:
            raise ValueError(
                f"Invalid Employee ID format: {e.errors()[0]['msg']}"
            )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_employee_by_id(
        clean_empl_id,
        columns=columns,
    )

    if not results.items:
        raise ResourceNotFoundError(
            message=f"Employee with ID {empl_id} not found",
            details={
                "empl_id": empl_id,
                "columns": columns,
            },
        )

    response = V1EmployeeListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeResponseModel.model_validate(item.model_dump())
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# EMPLOYEE TRAINING SEARCH
# =============================================================================

@router.route(
    "POST",
    r"/v1/employees/training/search",
    is_regex=False,
)
@api_handler
def search_employee_training_v1(event, context):
    """
    Search for employee training records using filters, sorting,
    and pagination.

    Args:
        event: Lambda event containing JSON body with
               'filters', 'sort', 'page', and 'columns'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of training records.
    """

    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    filters_data = body.get("filters", {})
    sort = SortModel(**body.get("sort", {}))
    page = PaginationModel(**body.get("page", {}))
    columns = body.get("columns")

    results = get_all_training(
        filters=filters_data,
        sort=sort,
        page=page,
        columns=columns,
    )

    response = V1EmployeeTrainingListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeTrainingResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# TRAINING BY STATUS
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/training/status/?$",
    is_regex=True,
)
@api_handler
def get_training_by_status_blank_v1(event, context):
    """
    Handle requests to the endpoint missing a training status.
    """

    err = ValueError("Training Status is Missing.")
    err.add_note(
        "Training Status is required, e.g. "
        "/v1/employees/training/status/CURRENT"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/training/status/(?P<status>[^/]+)",
    is_regex=True,
)
@api_handler
def get_training_by_status_v1(event, context):
    """
    Retrieve training records filtered by status.

    Args:
        event: Lambda event containing 'status' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of training records.
    """

    status = LambdaUtils.get_path_param(event, "status")
    query_params = LambdaUtils.get_all_query_params(event)

    if not status:
        raise ValueError("Training status is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "expiration_date"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_training_by_status(
        status=status,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeTrainingListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeTrainingResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# TRAINING BY ORGANIZATION
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/training/org/?$",
    is_regex=True,
)
@api_handler
def get_training_by_org_blank_v1(event, context):
    """
    Handle requests to the endpoint missing an organization ID.
    """

    err = ValueError("Organization ID is Missing.")
    err.add_note(
        "Organization ID is required, e.g. "
        "/v1/employees/training/org/01.626.N32.10"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/training/org/(?P<org_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_training_by_org_v1(event, context):
    """
    Retrieve all training records for employees within a specific
    organization.

    Args:
        event: Lambda event containing 'org_id' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of training records.
    """

    org_id = LambdaUtils.get_path_param(event, "org_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not org_id:
        raise ValueError("Organization ID is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "LAST_FIRST_NAME"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_training_by_org(
        org_id=org_id,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeTrainingListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeTrainingResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# TRAINING BY TYPE
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/training/type/?$",
    is_regex=True,
)
@api_handler
def get_training_by_type_blank_v1(event, context):
    """
    Handle requests to the endpoint missing a Record Type.
    """

    err = ValueError("Record Type is Missing.")
    err.add_note(
        "Record Type is required, e.g. "
        "/v1/employees/training/type/TRAINING"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/training/type/(?P<record_type>[^/]+)",
    is_regex=True,
)
@api_handler
def get_training_by_type_v1(event, context):
    """
    Retrieve training records filtered by record type.

    Args:
        event: Lambda event containing 'record_type' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of training records.
    """

    record_type = LambdaUtils.get_path_param(event, "record_type")
    query_params = LambdaUtils.get_all_query_params(event)

    if not record_type:
        raise ValueError("Training record type is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "completed_date"),
        order=query_params.get("sortOrder", "desc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_training_by_type(
        record_type=record_type,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeTrainingListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeTrainingResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# TRAINING BY EMPLOYEE
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/training/?$",
    is_regex=True,
)
@api_handler
def get_employee_training_blank_v1(event, context):
    """
    Handle requests to the endpoint missing an employee ID.
    """

    err = ValueError("Employee ID is Missing.")
    err.add_note(
        "Employee ID is required, e.g. /v1/employees/training/12345"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/training/(?P<empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_training_v1(event, context):
    """
    Retrieve all training records for a specific employee.

    Args:
        event: Lambda event containing 'empl_id' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of training records
        for the employee.
    """

    empl_id = LambdaUtils.get_path_param(event, "empl_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not empl_id:
        raise ValueError("Employee ID is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "completed_date"),
        order=query_params.get("sortOrder", "desc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_training_by_employee(
        empl_id=empl_id,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeTrainingListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeTrainingResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# EMPLOYEE CERTIFICATIONS
# =============================================================================

@router.route(
    "POST",
    r"/v1/employees/certifications/search",
    is_regex=False,
)
@api_handler
def search_employee_certifications_v1(event, context):
    """
    Search for employee certification records using filters, sorting,
    and pagination.

    Args:
        event: Lambda event containing JSON body with
               'filters', 'sort', 'page', and 'columns'.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of certification records.
    """

    try:
        body = LambdaUtils.get_json_body(event)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body provided.")

    filters_data = body.get("filters", {})
    sort = SortModel(**body.get("sort", {}))
    page = PaginationModel(**body.get("page", {}))
    columns = body.get("columns")

    results = get_all_certifications(
        filters=filters_data,
        sort=sort,
        page=page,
        columns=columns,
    )

    response = V1EmployeeCertificationListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeCertificationResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# CERTIFICATIONS BY STATUS
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/certifications/status/?$",
    is_regex=True,
)
@api_handler
def get_certifications_by_status_blank_v1(event, context):
    """
    Handle requests to the endpoint missing a certification status.
    """

    err = ValueError("Certification Status is Missing.")
    err.add_note(
        "Certification Status is required, e.g. "
        "/v1/employees/certifications/status/EXPIRED"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/certifications/status/(?P<status>[^/]+)",
    is_regex=True,
)
@api_handler
def get_certifications_by_status_v1(event, context):
    """
    Retrieve certification records filtered by status
    (CURRENT, EXPIRED, EXPIRING_SOON).

    Args:
        event: Lambda event containing 'status' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of certification records.
    """

    status = LambdaUtils.get_path_param(event, "status")
    query_params = LambdaUtils.get_all_query_params(event)

    if not status:
        raise ValueError("Certification status is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "expiration_date"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_certifications_by_status(
        status=status,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeCertificationListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeCertificationResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# CERTIFICATIONS BY ORGANIZATION
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/certifications/org/?$",
    is_regex=True,
)
@api_handler
def get_certifications_by_org_blank_v1(event, context):
    """
    Handle requests to the endpoint missing an organization ID.
    """

    err = ValueError("Organization ID is Missing.")
    err.add_note(
        "Organization ID is required, e.g. "
        "/v1/employees/certifications/org/01.626.N32.10"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/certifications/org/(?P<org_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_certifications_by_org_v1(event, context):
    """
    Retrieve all certification records for employees within a specific
    organization.

    Args:
        event: Lambda event containing 'org_id' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of certification records.
    """

    org_id = LambdaUtils.get_path_param(event, "org_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not org_id:
        raise ValueError("Organization ID is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "employee_name"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_certifications_by_org(
        org_id=org_id,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeCertificationListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeCertificationResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)


# =============================================================================
# CERTIFICATIONS BY EMPLOYEE
# =============================================================================

@router.route(
    "GET",
    r"/v1/employees/certifications/?$",
    is_regex=True,
)
@api_handler
def get_employee_certifications_blank_v1(event, context):
    """
    Handle requests to the endpoint missing an employee ID.
    """

    err = ValueError("Employee ID is Missing.")
    err.add_note(
        "Employee ID is required, e.g. "
        "/v1/employees/certifications/12345"
    )
    raise err


@router.route(
    "GET",
    r"/v1/employees/certifications/(?P<empl_id>[^/]+)",
    is_regex=True,
)
@api_handler
def get_employee_certifications_v1(event, context):
    """
    Retrieve all certification records for a specific employee.

    Args:
        event: Lambda event containing 'empl_id' path parameter and
               optional query params.
        context: Lambda context.

    Returns:
        Dict containing metadata and the list of certification records
        for the employee.
    """

    empl_id = LambdaUtils.get_path_param(event, "empl_id")
    query_params = LambdaUtils.get_all_query_params(event)

    if not empl_id:
        raise ValueError("Employee ID is required.")

    page = PaginationModel(
        limit=int(
            query_params.get(
                "limit",
                settings.DEFAULT_PAGE_SIZE,
            )
        ),
        cursor=query_params.get("cursor"),
    )

    sort = SortModel(
        field=query_params.get("sortField", "expiration_date"),
        order=query_params.get("sortOrder", "asc"),
    )

    columns = LambdaUtils.get_columns_query_parameter(event)

    results = get_certifications_by_employee(
        empl_id=empl_id,
        page=page,
        sort=sort,
        columns=columns,
    )

    response = V1EmployeeCertificationListResponseModel(
        metadata=V1MetadataModel(**results.metadata.model_dump()),
        data=[
            V1EmployeeCertificationResponseModel.model_validate(
                item.model_dump()
            )
            for item in results.items
        ],
    )

    return response.model_dump(by_alias=True)
