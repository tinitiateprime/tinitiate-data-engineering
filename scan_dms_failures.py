"""
Service layer for IrcCensusReport.
"""

from typing import List, Optional, Union

from core.config import settings
from core.filters import FiltersEnvelope, SortModel
from core.pagination import DEFAULT_PAGE_SIZE, PaginationModel

from db.repositories import irc_census_report_repo

from domain.models.irc_census_report import (
    IrcCensusReportResponse,
    IrcCensusReportSearchServiceResponse,
)

from domain.models.metadata import MetadataModel


# =============================================================================
# SEARCH / LIST IRC CENSUS REPORTS
# =============================================================================

def search_irc_census_reports(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
) -> IrcCensusReportSearchServiceResponse:
    """
    Search/list IRC Census Report records.

    row_id remains the stable pagination/sort key.
    """

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    current_page = page or PaginationModel(
        limit=DEFAULT_PAGE_SIZE
    )

    # -------------------------------------------------------------------------
    # Default sort
    # -------------------------------------------------------------------------
    current_sort = sort or SortModel(
        field="row_id",
        order="asc",
    )

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(
            filters=filters
        )
    elif filters is None:
        validated_filters = FiltersEnvelope(
            filters={}
        )
    else:
        validated_filters = filters

    # -------------------------------------------------------------------------
    # Repository
    # -------------------------------------------------------------------------
    db_result = irc_census_report_repo.get_irc_census_reports(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    # -------------------------------------------------------------------------
    # Convert DB records to domain models
    # -------------------------------------------------------------------------
    items = [
        IrcCensusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    page_result = db_result.get("page", {})

    # -------------------------------------------------------------------------
    # Service response
    # -------------------------------------------------------------------------
    return IrcCensusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=page_result.get("cursor"),
            has_more=page_result.get("has_more", False),
            applied_filters=(
                validated_filters
                if validated_filters.filters
                else None
            ),
        ),
    )


# =============================================================================
# GET IRC CENSUS REPORT BY LAST_FIRST_NAME
# =============================================================================

def get_irc_census_report_details(
    last_first_name: str,
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    limit: int = settings.DEFAULT_PAGE_SIZE,
    cursor: Optional[str] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> IrcCensusReportSearchServiceResponse:
    """
    Get IRC Census Report records for a specific LAST_FIRST_NAME.

    IMPORTANT:
        Employee lookup = last_first_name

        row_id is NOT used as the employee lookup key.
        row_id remains the technical key used for pagination.
    """

    # -------------------------------------------------------------------------
    # Required employee name
    # -------------------------------------------------------------------------
    if not last_first_name:
        return IrcCensusReportSearchServiceResponse(
            items=[],
            metadata=MetadataModel(
                cursor=None,
                has_more=False,
                applied_filters=None,
            ),
        )

    # -------------------------------------------------------------------------
    # Validate filters
    # -------------------------------------------------------------------------
    if isinstance(filters, dict):
        validated_filters = FiltersEnvelope(
            filters=filters
        )
    elif filters is None:
        validated_filters = FiltersEnvelope(
            filters={}
        )
    else:
        validated_filters = filters

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    current_page = PaginationModel(
        limit=limit,
        cursor=cursor,
    )

    # -------------------------------------------------------------------------
    # Sort
    #
    # row_id stays the deterministic pagination key.
    # -------------------------------------------------------------------------
    current_sort = sort or SortModel(
        field="row_id",
        order="asc",
    )

    # -------------------------------------------------------------------------
    # Repository
    #
    # IMPORTANT:
    # Pass last_first_name, not row_id.
    # -------------------------------------------------------------------------
    db_result = irc_census_report_repo.get_irc_census_report_by_id(
        last_first_name=last_first_name,
        filters=validated_filters,
        page=current_page,
        columns=columns,
        sort=current_sort,
    )

    # -------------------------------------------------------------------------
    # Convert DB results to domain models
    # -------------------------------------------------------------------------
    items = [
        IrcCensusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    page_result = db_result.get("page", {})

    # -------------------------------------------------------------------------
    # Service response
    # -------------------------------------------------------------------------
    return IrcCensusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=page_result.get("cursor"),
            has_more=page_result.get("has_more", False),
            applied_filters=(
                validated_filters
                if validated_filters.filters
                else None
            ),
        ),
    )
