"""
Service layer for IrcCensusReport
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
    Orchestrates the transformation of API inputs into domain objects.
    """

    current_page = page or PaginationModel(
        limit=DEFAULT_PAGE_SIZE
    )

    # row_id remains the technical/default pagination sort field
    current_sort = sort or SortModel(
        field="row_id",
        order="asc",
    )

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

    db_result = irc_census_report_repo.get_irc_census_reports(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    items = [
        IrcCensusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    return IrcCensusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result["page"].get("cursor"),
            has_more=db_result["page"].get(
                "has_more",
                False,
            ),
            applied_filters=(
                validated_filters
                if validated_filters.filters
                else None
            ),
        ),
    )


# =============================================================================
# GET IRC CENSUS REPORT DETAILS BY LAST_FIRST_NAME
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
    Retrieves IRC Census Report records for a specific LAST_FIRST_NAME.

    Employee lookup:
        last_first_name

    Technical pagination key:
        row_id
    """

    # -------------------------------------------------------------------------
    # Required name
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
    # Pagination
    # -------------------------------------------------------------------------
    page = PaginationModel(
        limit=limit,
        cursor=cursor,
    )

    # -------------------------------------------------------------------------
    # Sort
    # Keep row_id as stable pagination/sort key
    # -------------------------------------------------------------------------
    current_sort = sort or SortModel(
        field="row_id",
        order="asc",
    )

    # -------------------------------------------------------------------------
    # Repository lookup
    # IMPORTANT: use last_first_name, not row_id
    # -------------------------------------------------------------------------
    db_result = irc_census_report_repo.get_irc_census_report_by_id(
        last_first_name=last_first_name,
        filters=validated_filters,
        page=page,
        columns=columns,
        sort=current_sort,
    )

    # -------------------------------------------------------------------------
    # Domain model conversion
    # -------------------------------------------------------------------------
    items = [
        IrcCensusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    # -------------------------------------------------------------------------
    # Service response
    # -------------------------------------------------------------------------
    return IrcCensusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result["page"].get("cursor"),
            has_more=db_result["page"].get(
                "has_more",
                False,
            ),
            applied_filters=(
                validated_filters
                if validated_filters.filters
                else None
            ),
        ),
    )
