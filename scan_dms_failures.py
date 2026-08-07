# domain/services/employee_profile_synth_service.py
from typing import List, Optional, Union

from core.config import settings
from core.filters import FilterOps, FiltersEnvelope, SortModel
from core.logging import logger
from core.pagination import PaginationModel
from db.repositories import employee_profile_synth_repo as employee_profile_repo
from domain.models.employee_profile import (
    EmployeeProfileResponse,
    EmployeeProfileSearchServiceResponse,
)
from domain.models.metadata import MetadataModel


# This empty response is often used when a parameter provided is invalid or empty
def _empty_response() -> EmployeeProfileSearchServiceResponse:
    """Helper to return a standard empty search response."""
    return EmployeeProfileSearchServiceResponse(
        items=[],
        metadata=MetadataModel(
            cursor=None,
            has_more=False,
            applied_filters=None,
        ),
    )


def get_all_employees(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Get all employee profiles with optional filtering, sorting, and pagination.

    Args:
        filters: Filter criteria
        sort: Sort configuration
        page: Pagination settings
        columns: Specific columns to return

    Returns:
        Service response with items and metadata
    """

    # Normalize filters to ensure we have a FiltersEnvelope object
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters

    # Set defaults
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Call repository
    db_result = employee_profile_repo.get_employee_profiles(
        filters=current_filters, sort=current_sort, page=current_page, columns=columns
    )
    logger.debug(f"SERVICE: Got {len(db_result.get('items', []))} items from repo")

    # Transform to Domain Objects
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=current_filters
            if current_filters and current_filters.filters
            else None,
        ),
    )


def get_employee_by_id(
    empl_id: str,
    columns: Optional[List[str]] = None,
):
    """
    Get a single employee profile by ID.

    Args:
        empl_id: Employee ID (required)
        columns: Specific columns to return

    Returns:
        Service response with items and metadata
    """
    logger.debug(f"SERVICE: get_employee_by_id called for empl_id={empl_id}")

    # Early exit if empty parameter
    if not empl_id:
        logger.warning("SERVICE: Empty empl_id provided")
        return _empty_response()

    # Call repository
    db_result = employee_profile_repo.get_employee_profile_by_id(
        empl_id=empl_id, columns=columns
    )

    # TODO: Validation needed for only 1 response or does DB do that?

    # Transform to Domain Object
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]
    logger.debug(f"SERVICE: Got {len(items)} items from repo")

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=FiltersEnvelope(
                filters={"employeeId": FilterOps(eq=empl_id)}
            ),
        ),
    )


def get_direct_reports(
    mgr_empl_id: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Get all employees reporting to a specific manager.

    Args:
        mgr_empl_id: Manager's employee ID (required)
        page: Pagination settings
        sort: Sort configuration
        columns: Specific columns to return

    Returns:
        Service response with items and metadata
    """
    logger.info(f"SERVICE: get_direct_reports called for mgr_empl_id={mgr_empl_id}")

    # Early exit if empty parameter
    if not mgr_empl_id:
        logger.warning("SERVICE: Empty mgr_empl_id provided")
        return _empty_response()

    # Set defaults
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Call repository
    db_result = employee_profile_repo.get_employees_by_manager(
        mgr_empl_id=mgr_empl_id, page=current_page, sort=current_sort, columns=columns
    )

    # Transform to Domain Object
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]
    employee_count = len(items)
    logger.info(f"SERVICE: Got {employee_count} items from repo")

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=None,
        ),
    )


def get_employees_in_org(
    org_id: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Get all employees in a specific organization.

    Args:
        org_id: Organization ID (required)
        page: Pagination settings
        sort: Sort configuration
        columns: Specific columns to return

    Returns:
        Service response with items and metadata
    """
    logger.debug(f"SERVICE: get_employees_in_org called for org_id={org_id}")

    # Early Return for invalid IDs
    if not org_id:
        logger.warning("Empty org_id provided to get_employees_in_org.")
        return _empty_response()

    # Set defaults
    current_page = page or PaginationModel()
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Call repository
    db_result = employee_profile_repo.get_employees_by_org(
        org_id=org_id, page=current_page, sort=current_sort, columns=columns
    )

    # Transform to Domain Object
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]
    employee_count = len(items)
    logger.debug(f"SERVICE: Got {employee_count} items from repo")

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=None,
        ),
    )


def get_employees_by_clearance(
    clearance_status: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Get all employees with a specific clearance status.

    Args:
        clearance_status: Clearance status (required)
        page: Pagination settings
        sort: Sort configuration
        columns: Specific columns to return

    Returns:
        Service response with items and metadata
    """
    logger.debug(
        f"SERVICE: get_employees_by_clearance called for status={clearance_status}"
    )

    # Early Return for empty parameter
    if not clearance_status:
        logger.warning("SERVICE: Empty clearance_status provided")
        return _empty_response()

    # Set defaults
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Call repository
    db_result = employee_profile_repo.get_employees_by_clearance(
        clearance_status=clearance_status,
        page=current_page,
        sort=current_sort,
        columns=columns,
    )

    # Transform to Domain Object
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]
    employee_count = len(items)
    logger.info(f"SERVICE: Got {employee_count} items from repo")

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=None,
        ),
    )


def get_personnel_roster(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
):
    """Get personnel-roster (alpha-report) fields, filtered by entity-derived criteria."""
    logger.info("SERVICE: get_personnel_roster called")

    # Normalize filters to ensure we have a FiltersEnvelope object
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters

    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    db_result = employee_profile_repo.get_personnel_roster(
        filters=current_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    # Transform to Domain Objects
    items = [
        EmployeeProfileResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]
    logger.info(f"SERVICE: Got {len(items)} items from repo")

    return EmployeeProfileSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get("page", {}).get("cursor"),
            has_more=db_result.get("page", {}).get("has_more", False),
            applied_filters=current_filters
            if current_filters and current_filters.filters
            else None,
        ),
    )
