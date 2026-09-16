"""
Unit tests for domain.services.irc_census_report_service
"""

from unittest.mock import MagicMock, patch

from core.filters import FiltersEnvelope, SortModel
from core.pagination import PaginationModel

from domain.services import irc_census_report_service


# =============================================================================
# TEST DATA
# =============================================================================

LAST_FIRST_NAME = "Price, Kevin T"

SAMPLE_ITEM = {
    "row_id": 16698,
    "my_id": "X83855",
    "last_first_name": LAST_FIRST_NAME,
    "prir_name": "",
    "s_empl_status_cd": "ACT",
    "hire_dt": "2014-03-01",
    "reh_dt": "2022-10-01",
    "term_dt": None,
    "seniority_dt": "2014-03-01",
    "term_reason_cd": "",
    "taxble_entity_id": "525",
    "locator_cd": "HYBRID",
    "empl_class_cd": "E1",
    "pto_accrl_cd": None,
    "bu_name": None,
    "dept_num": None,
    "detl_job_cd": None,
    "title_desc": "Dir Technology 1",
    "mgr_name": "Sosa, Marc",
}


def _db_result(items=None, cursor=None, has_more=False):
    """
    Helper that returns the structure expected from the repository.
    """
    return {
        "items": items if items is not None else [],
        "page": {
            "cursor": cursor,
            "has_more": has_more,
        },
    }


# =============================================================================
# SEARCH TESTS
# =============================================================================

@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_reports"
)
def test_search_irc_census_reports_success(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM],
        cursor=None,
        has_more=False,
    )

    filters = FiltersEnvelope(filters={})

    result = irc_census_report_service.search_irc_census_reports(
        filters=filters,
        sort=None,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert len(result.items) == 1
    assert result.items[0].row_id == 16698
    assert result.items[0].last_first_name == LAST_FIRST_NAME

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_reports"
)
def test_search_irc_census_reports_dict_filters(mock_repo):
    mock_repo.return_value = _db_result(items=[])

    filters = {
        "last_first_name": {
            "eq": LAST_FIRST_NAME
        }
    }

    result = irc_census_report_service.search_irc_census_reports(
        filters=filters,
        sort=None,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result.items == []
    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_reports"
)
def test_search_irc_census_reports_none_filters(mock_repo):
    mock_repo.return_value = _db_result(items=[])

    result = irc_census_report_service.search_irc_census_reports(
        filters=None,
        sort=None,
        page=None,
        columns=None,
    )

    assert result.items == []
    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_reports"
)
def test_search_irc_census_reports_custom_sort(mock_repo):
    mock_repo.return_value = _db_result(items=[])

    sort = SortModel(
        field="last_first_name",
        order="asc",
    )

    result = irc_census_report_service.search_irc_census_reports(
        filters=None,
        sort=sort,
        page=PaginationModel(limit=10),
        columns=None,
    )

    assert result.items == []

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["sort"] == sort


# =============================================================================
# DETAIL TESTS
# =============================================================================

@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_success(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM],
        cursor=None,
        has_more=False,
    )

    filters = FiltersEnvelope(filters={})

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name=LAST_FIRST_NAME,
        filters=filters,
        limit=10,
        cursor=None,
        columns=None,
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.row_id == 16698
    assert item.my_id == "X83855"
    assert item.last_first_name == LAST_FIRST_NAME
    assert item.title_desc == "Dir Technology 1"
    assert item.mgr_name == "Sosa, Marc"

    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert (
        call_kwargs["last_first_name"]
        == LAST_FIRST_NAME
    )

    # row_id should NOT be the detail lookup parameter anymore.
    assert "row_id" not in call_kwargs


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_not_found(mock_repo):
    mock_repo.return_value = _db_result(
        items=[],
        cursor=None,
        has_more=False,
    )

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name="Does Not Exist",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert (
        call_kwargs["last_first_name"]
        == "Does Not Exist"
    )


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_missing_key(mock_repo):
    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name="",
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
    )

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None

    # Repository must not be called if the name is missing.
    mock_repo.assert_not_called()


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_dict_filters(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM],
        cursor=None,
        has_more=False,
    )

    filters = {
        "s_empl_status_cd": {
            "eq": "ACT"
        }
    }

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name=LAST_FIRST_NAME,
        filters=filters,
        limit=10,
        cursor=None,
        columns=None,
    )

    assert len(result.items) == 1
    assert result.items[0].last_first_name == LAST_FIRST_NAME

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )

    assert (
        call_kwargs["last_first_name"]
        == LAST_FIRST_NAME
    )


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_none_filters(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM],
        cursor=None,
        has_more=False,
    )

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name=LAST_FIRST_NAME,
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
    )

    assert len(result.items) == 1
    assert result.items[0].row_id == 16698
    assert result.items[0].last_first_name == LAST_FIRST_NAME

    mock_repo.assert_called_once()

    call_kwargs = mock_repo.call_args.kwargs

    assert isinstance(
        call_kwargs["filters"],
        FiltersEnvelope,
    )

    assert (
        call_kwargs["last_first_name"]
        == LAST_FIRST_NAME
    )


# =============================================================================
# DETAIL PAGINATION / SORT
# =============================================================================

@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_pagination(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM],
        cursor="next-cursor",
        has_more=True,
    )

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name=LAST_FIRST_NAME,
        filters=None,
        limit=1,
        cursor="current-cursor",
        columns=None,
    )

    assert len(result.items) == 1
    assert result.metadata.cursor == "next-cursor"
    assert result.metadata.has_more is True

    call_kwargs = mock_repo.call_args.kwargs

    assert (
        call_kwargs["last_first_name"]
        == LAST_FIRST_NAME
    )

    assert call_kwargs["page"].limit == 1
    assert call_kwargs["page"].cursor == "current-cursor"


@patch(
    "domain.services.irc_census_report_service."
    "irc_census_report_repo.get_irc_census_report_by_id"
)
def test_get_irc_census_report_details_custom_sort(mock_repo):
    mock_repo.return_value = _db_result(
        items=[SAMPLE_ITEM]
    )

    sort = SortModel(
        field="last_first_name",
        order="asc",
    )

    result = irc_census_report_service.get_irc_census_report_details(
        last_first_name=LAST_FIRST_NAME,
        filters=None,
        limit=10,
        cursor=None,
        columns=None,
        sort=sort,
    )

    assert len(result.items) == 1

    call_kwargs = mock_repo.call_args.kwargs

    assert call_kwargs["sort"] == sort
