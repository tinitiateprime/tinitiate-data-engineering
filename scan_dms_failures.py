# main-function\mt-dm-lambda-src\db\repositories\employee_profile_synth_repo.py
import time
from typing import List, Optional, Union

from core.config import settings
from core.logging import logger
from db.builders.base_builder import BaseRepositoryBuilder
from db.builders.pypika_builder import QuerySpec, encode_cursor
from db.connection import execute_query
from v1.schemas import FilterOps, FiltersEnvelope, PaginationModel, SortModel


EMPLOYEE_PROFILE_VIEW_SPEC = QuerySpec(
    table="gold.employee_profile_vw",
    column_map={
        # Employee Identity
        "employeeId": {"col": "EMPL_ID", "type": "text"},
        "firstName": {"col": "FIRST_NAME", "type": "text"},
        "lastName": {"col": "LAST_NAME", "type": "text"},
        "lastFirstName": {"col": "LAST_FIRST_NAME", "type": "text"},
        # Position
        "titleDescription": {"col": "TITLE_DESC", "type": "text"},
        "jobCode": {"col": "JOB_CODE", "type": "text"},
        "employmentType": {"col": "S_EMPL_TYPE_CD", "type": "text"},
        # Organization
        "organizationId": {"col": "ORG_ID", "type": "text"},
        "departmentName": {"col": "DEPT_NAME", "type": "text"},
        # Location
        "locationName": {"col": "LOC_NAME", "type": "text"},
        "locationCity": {"col": "LOC_CITY", "type": "text"},
        # Manager
        "managerName": {"col": "MGR_NAME", "type": "text"},
        "managerEmployeeId": {"col": "MGR_EMPL_ID", "type": "text"},
        # Additional Fields from Schema
        "hireDate": {"col": "HIRE_DATE", "type": "text"},
        # NOTE: emailAddress/EMAIL_ADDR removed - the column is absent from the
        # gold.employee_profile_vw view (seed + warehouse), so selecting it 502'd
        # every employee query. Re-add here + in the view when email is available.
        # Clearance
        "clearanceStatus": {"col": "clearance_status", "type": "text"},
        "clearanceStatusDate": {"col": "clearance_status_date", "type": "text"},
        "clearanceEligibility": {"col": "clearance_eligibility", "type": "text"},
    },
    logical_id_field="employeeId",
    allowed_sort_fields={
        "employeeId",
        "lastName",
        "firstName",
        "lastFirstName",
        "titleDescription",
        "departmentName",
        "organizationId",
        "hireDate",
        "managerName",
        "locationCity",
        "clearanceStatus",
    },
    default_select=[
        "employeeId",
        "firstName",
        "lastName",
        "lastFirstName",
        "titleDescription",
        "jobCode",
        "employmentType",
        "organizationId",
        "departmentName",
        "locationName",
        "locationCity",
        "managerName",
        "managerEmployeeId",
        "hireDate",
        "clearanceStatus",
        "clearanceStatusDate",
        "clearanceEligibility",
    ],
)

# Fields HII_Ground portal roster uses
# Logical (column_map) keys the builder validates against - NOT physical column names.
PERSONNEL_ROSTER_SELECT = [
    "employeeId",
    "lastFirstName",
    "lastName",
    "firstName",
    "titleDescription",
    "departmentName",
    "locationCity",
    "managerName",
    "hireDate",
]

# Initialize the builder
_builder = BaseRepositoryBuilder(EMPLOYEE_PROFILE_VIEW_SPEC)


##############################################################################
# Helper Functions
##############################################################################
def _format_paginated_response(items: list, limit: int) -> dict:
    """Helper to process DB results into a standardized response envelope."""
    has_more = len(items) > limit
    next_cursor = None
    if has_more:
        items = items[:limit]
        next_cursor = encode_cursor(items[-1].get("EMPL_ID"))

    for item in items:
        item.pop("total_count_hidden", None)

    return {
        "items": items,
        "page": {"cursor": next_cursor, "has_more": has_more},
    }


##############################################################################
# Repository Functions
##############################################################################
def get_employee_profiles(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Retrieves employee profiles from the view.
    Handles POST body JSON containing filters, sort, and page config.

    Args:
        filters: Filter criteria (e.g., {"ORG_ID": {"eq": "MT"}, "clearance_status": {"eq": "Active"}})
        sort: Sort configuration (default: LAST_NAME ASC)
        page: Pagination settings
        columns: Optional list of specific columns to return (None = all)

    Returns:
        dict with 'items' (list of employee profiles) and 'page' keys

    Example:
        # Get all employees in a department
        get_employee_profiles(filters={"DEPT_NAME": {"eq": "Engineering"}})

        # Get employees by manager
        get_employee_profiles(filters={"MGR_EMPL_ID": {"eq": "12345"}})

        # Get employees with specific clearance
        get_employee_profiles(filters={"clearance_status": {"eq": "Active"}})
    """
    # start_time = time.time()

    # 1. Normalize Inputs
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters or FiltersEnvelope(filters={})

    current_sort = sort or SortModel(field="lastName", order="asc")
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)

    # 2. Generate Plan
    plan_start = time.time()
    plan = _builder.get_list_plan(
        filters=current_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )
    logger.info(f"REPO: Plan generation took {time.time() - plan_start:.3f}s")

    # 3. Execute Query
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
        db_key="synth",  # <-- routes to synth db
    )

    items = raw_results.get("items", [])
    logger.debug(f"REPO: Got {len(items)} items")

    # 4. Format response
    return _format_paginated_response(items, current_page.limit)


def get_employee_profile_by_id(
    empl_id: str,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Fetches a single employee profile by employee ID.

    Args:
        empl_id: The employee ID (REQUIRED)
        columns: Optional list of specific columns to return

    Returns:
        dict with 'items' containing single employee or empty list if not found

    Example:
        get_employee_profile_by_id("12345")
    """
    logger.debug(f"REPO: get_employee_profile_by_id called for empl_id={empl_id}")

    # Validation
    if not empl_id or not empl_id.strip():
        logger.warning("REPO: Empty empl_id provided")
        return {"items": [], "page": {"cursor": None, "has_more": False}}

    # Build filter for specific employee
    filter_dict = {"employeeId": FilterOps(eq=empl_id.strip())}
    filters = FiltersEnvelope(filters=filter_dict)

    # Generate Plan
    plan = _builder.get_list_plan(
        filters=filters,
        sort=SortModel(),
        page=PaginationModel(limit=1),
        columns=columns,
    )

    # Execute Query
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=1,
        db_key="synth",  # <-- routes to synth db
    )
    items = raw_results.get("items", [])

    logger.debug(f"REPO: Found {len(items)} employee(s).")
    logger.debug(items)

    return _format_paginated_response(items, 1)  # Limit is 1


def get_employees_by_manager(
    mgr_empl_id: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Fetches all employees reporting to a specific manager.

    Args:
        mgr_empl_id: The manager's employee ID (REQUIRED)
        page: Pagination settings
        sort: Sort configuration (default: LAST_NAME ASC)
        columns: Optional list of specific columns to return

    Returns:
        dict with 'items' (list of employees) and 'page' keys

    Example:
        get_employees_by_manager("12345")
    """
    start_time = time.time()
    logger.info(f"REPO: get_employees_by_manager called for mgr_empl_id={mgr_empl_id}")

    # Validation
    if not mgr_empl_id or not mgr_empl_id.strip():
        logger.warning("REPO: Empty mgr_empl_id provided")
        return {"items": [], "page": {"cursor": None, "has_more": False}}

    # Build filter for manager's direct reports
    filter_dict = {"managerEmployeeId": FilterOps(eq=mgr_empl_id.strip())}
    filters = FiltersEnvelope(filters=filter_dict)

    # Defaults
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Generate Plan
    plan = _builder.get_list_plan(
        filters=filters, sort=current_sort, page=current_page, columns=columns
    )

    # Execute Query
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
        db_key="synth",  # <-- routes to synth db
    )
    items = raw_results.get("items", [])

    logger.info(
        f"REPO: Found {len(items)} direct reports in {time.time() - start_time:.3f}s"
    )

    return _format_paginated_response(items, current_page.limit)


def get_employees_by_org(
    org_id: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Fetches all employees in a specific organization.

    Args:
        org_id: The organization ID (REQUIRED)
        page: Pagination settings
        sort: Sort configuration (default: LAST_NAME ASC)
        columns: Optional list of specific columns to return

    Returns:
        dict with 'items' (list of employees) and 'page' keys

    Example:
        get_employees_by_org("01.525.146.10")
    """
    logger.debug(f"REPO: get_employees_by_org called for org_id={org_id}")

    # Early Return for invalid IDs TODO: Determine if this should be an error
    if not org_id or not org_id.strip():
        logger.warning("REPO: Empty org_id provided")
        return {"items": [], "page": {"cursor": None, "has_more": False}}

    # Build filter for organization
    filters = FiltersEnvelope(filters={"organizationId": FilterOps(eq=org_id.strip())})

    # Defaults
    current_page = page or PaginationModel()
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Generate Plan
    plan = _builder.get_list_plan(
        filters=filters, sort=current_sort, page=current_page, columns=columns
    )

    # Execute Query
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
        db_key="synth",  # <-- routes to synth db
    )
    items = raw_results.get("items", [])

    logger.debug(f"REPO: Found {len(items)} employees in org.")

    return _format_paginated_response(items, current_page.limit)


def get_employees_by_clearance(
    clearance_status: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Fetches all employees with a specific clearance status.

    Args:
        clearance_status: The clearance status (e.g., "Active", "Inactive")
        page: Pagination settings
        sort: Sort configuration (default: LAST_NAME ASC)
        columns: Optional list of specific columns to return

    Returns:
        dict with 'items' (list of employees) and 'page' keys

    Example:
        get_employees_by_clearance("Active")
    """
    start_time = time.time()
    logger.info(
        f"REPO: get_employees_by_clearance called for status={clearance_status}"
    )

    # Validation
    if not clearance_status or not clearance_status.strip():
        logger.warning("REPO: Empty clearance_status provided")
        return {"items": [], "page": {"cursor": None, "has_more": False}}

    # Build filter for clearance status
    filter_dict = {"clearanceStatus": FilterOps(eq=clearance_status.strip())}
    filters = FiltersEnvelope(filters=filter_dict)

    # Defaults
    current_page = page or PaginationModel(limit=settings.DEFAULT_PAGE_SIZE)
    current_sort = sort or SortModel(field="lastName", order="asc")

    # Generate Plan
    plan = _builder.get_list_plan(
        filters=filters, sort=current_sort, page=current_page, columns=columns
    )

    # Execute Query
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
        db_key="synth",  # <-- routes to synth db
    )
    items = raw_results.get("items", [])

    logger.info(
        f"REPO: Found {len(items)} employees with clearance in {time.time() - start_time:.3f}s"
    )

    return _format_paginated_response(items, current_page.limit)


def get_personnel_roster(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> dict:
    """
    Retrieves the personnel-roster (alpha-report) fields from the view.
    Callers filter by entity-derived criteria passed in `filters`.

    Args:
        filters: Filter criteria (e.g., {"EMPL_ID": {"in": ["E-101", "E-102"]}})
        sort: Sort configuration (default: LAST_NAME ASC)
        page: Pagination settings
        columns: Optional list of specific columns to return
                 (None = PERSONNEL_ROSTER_SELECT)

    Returns:
        dict with 'items' (list of roster rows) and 'page' keys

    Example:
        # Roster for an entity's employees
        get_personnel_roster(filters={"EMPL_ID": {"in": ["E-101", "E-102"]}})
    """
    start_time = time.time()
    logger.info("REPO: get_personnel_roster called")

    # 1. Normalize Inputs
    if isinstance(filters, dict):
        current_filters = FiltersEnvelope(filters=filters)
    else:
        current_filters = filters or FiltersEnvelope(filters={})

    current_sort = sort or SortModel(field="lastName", order="asc")
    current_page = page or PaginationModel(limit=100)

    # 2. Generate Plan
    plan_start = time.time()
    plan = _builder.get_list_plan(
        filters=current_filters,
        sort=current_sort,
        page=current_page,
        columns=columns or PERSONNEL_ROSTER_SELECT,
    )
    logger.info(f"REPO: Plan generation took {time.time() - plan_start:.3f}s")

    # 3. Execute Query
    exec_start = time.time()
    raw_results = execute_query(
        plan.sql,
        plan.params,
        limit=current_page.limit,
        db_key="synth",  # <-- routes to synth db
    )
    logger.info(f"REPO: Query execution took {time.time() - exec_start:.3f}s")

    items = raw_results.get("items", [])
    logger.info(
        f"REPO: Got {len(items)} items in {time.time() - start_time:.3f}s total"
    )

    # 4. Format response
    return _format_paginated_response(items, current_page.limit)
