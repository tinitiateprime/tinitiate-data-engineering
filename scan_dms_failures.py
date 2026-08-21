# domain/services/project_status_report_service.py

from typing import List, Optional, Union

from core.config import settings
from core.filters import FiltersEnvelope, SortModel
from core.logging import logger
from core.pagination import PaginationModel
from db.repositories import project_status_report_repo
from domain.models.metadata import MetadataModel
from domain.models.project_status_report import (
    ProjectStatusReportResponse,
    ProjectStatusReportSearchServiceResponse,
)


def search_project_status_report(
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    sort: Optional[SortModel] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Search the full project status history
    (all fiscal years/periods).
    """

    logger.debug(
        "SERVICE: search_project_status_report called"
    )

    current_filters = (
        FiltersEnvelope(filters=filters)
        if isinstance(filters, dict)
        else filters
    )

    current_page = (
        page
        or PaginationModel(
            limit=settings.DEFAULT_PAGE_SIZE
        )
    )

    current_sort = (
        sort
        or SortModel(
            field="fiscal_year",
            order="desc",
        )
    )

    db_result = (
        project_status_report_repo.search_project_status_report(
            filters=current_filters,
            sort=current_sort,
            page=current_page,
            columns=columns,
        )
    )

    items = [
        ProjectStatusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    return ProjectStatusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get(
                "page", {}
            ).get("cursor"),
            has_more=db_result.get(
                "page", {}
            ).get(
                "has_more",
                False,
            ),
            applied_filters=(
                current_filters
                if current_filters
                and current_filters.filters
                else None
            ),
        ),
    )


def get_project_status_report_history(
    proj_id: str,
    page: Optional[PaginationModel] = None,
    sort: Optional[SortModel] = None,
    columns: Optional[List[str]] = None,
):
    """
    Get the full status history
    (every fiscal year/period on record)
    for a project.
    """

    logger.debug(
        f"SERVICE: "
        f"get_project_status_report_history "
        f"called for proj_id={proj_id}"
    )

    if not proj_id:
        return ProjectStatusReportSearchServiceResponse(
            items=[],
            metadata=MetadataModel(
                cursor=None,
                has_more=False,
                applied_filters=None,
            ),
        )

    current_page = (
        page
        or PaginationModel(
            limit=settings.DEFAULT_PAGE_SIZE
        )
    )

    current_sort = (
        sort
        or SortModel(
            field="fiscal_year",
            order="desc",
        )
    )

    db_result = (
        project_status_report_repo
        .get_project_status_report_history(
            proj_id=proj_id,
            page=current_page,
            sort=current_sort,
            columns=columns,
        )
    )

    items = [
        ProjectStatusReportResponse.model_validate(item)
        for item in db_result.get("items", [])
    ]

    return ProjectStatusReportSearchServiceResponse(
        items=items,
        metadata=MetadataModel(
            cursor=db_result.get(
                "page", {}
            ).get("cursor"),
            has_more=db_result.get(
                "page", {}
            ).get(
                "has_more",
                False,
            ),
            applied_filters=None,
        ),
    )
