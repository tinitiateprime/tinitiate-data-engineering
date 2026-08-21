from unittest.mock import ANY, MagicMock, patch

from core.filters import FiltersEnvelope
from core.pagination import PaginationModel
from core.filters import SortModel

from db.repositories import contract_analysis_repo


class TestContractAnalysisRepo:

    # ============================================================
    # KEY LOOKUP - SUCCESS
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    def test_get_contract_analysis_by_project_level(self, mock_execute):
        mock_execute.return_value = {
            "items": [
                {
                    "project_level": "PROJ-001",
                    "fy_cd": "2025",
                    "pd_no": 1,
                    "revenue": 1000.0,
                },
                {
                    "project_level": "PROJ-001",
                    "fy_cd": "2025",
                    "pd_no": 2,
                    "revenue": 1200.0,
                },
            ]
        }

        result = contract_analysis_repo.get_contract_analysis_by_project_level(
            "PROJ-001"
        )

        assert len(result["items"]) == 2
        assert all(
            item["project_level"] == "PROJ-001"
            for item in result["items"]
        )

        mock_execute.assert_called_once()

        args, kwargs = mock_execute.call_args
        assert kwargs["limit"] > 0

    # ============================================================
    # KEY LOOKUP - EMPTY KEY
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    def test_get_contract_analysis_by_project_level_empty_input(
        self,
        mock_execute,
    ):
        result = contract_analysis_repo.get_contract_analysis_by_project_level(
            ""
        )

        assert result == {
            "items": [],
            "page": {
                "cursor": None,
                "has_more": False,
            },
        }

        mock_execute.assert_not_called()

    # ============================================================
    # KEY LOOKUP - EMPTY RESULT
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    def test_contract_analysis_empty_result(self, mock_execute):
        mock_execute.return_value = {
            "items": [],
        }

        result = contract_analysis_repo.get_contract_analysis_by_project_level(
            "NONE"
        )

        assert result["items"] == []
        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

        mock_execute.assert_called_once()

    # ============================================================
    # GENERAL SEARCH - SUCCESS
    # Covers get_contract_analysis normal execution path
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_success(
        self,
        mock_get_plan,
        mock_execute,
    ):
        mock_plan = MagicMock()
        mock_plan.sql = "SELECT * FROM generated_test_source"
        mock_plan.params = {}

        mock_get_plan.return_value = mock_plan

        mock_execute.return_value = {
            "items": [
                {
                    "project_level": "PROJ-001",
                    "reorg_level": "R1",
                    "fy_cd": "2025",
                    "pd_no": 1,
                    "revenue": 1000.0,
                    "total_cost": 750.0,
                    "fee": 250.0,
                    "project_name": "Test Project",
                    "customer_name": "Test Customer",
                }
            ]
        }

        filters = FiltersEnvelope(filters={})
        sort = SortModel(
            field="fy_cd",
            order="desc",
        )
        page = PaginationModel(limit=10)

        result = contract_analysis_repo.get_contract_analysis(
            filters=filters,
            sort=sort,
            page=page,
            columns=None,
        )

        assert result is not None
        assert len(result["items"]) == 1

        assert result["items"][0]["project_level"] == "PROJ-001"
        assert result["items"][0]["fy_cd"] == "2025"

        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=ANY,
            page=ANY,
            columns=None,
        )

        mock_execute.assert_called_once_with(
            mock_plan.sql,
            mock_plan.params,
            limit=10,
        )

    # ============================================================
    # GENERAL SEARCH - DICT FILTER
    # Covers:
    #
    # if isinstance(filters, dict):
    #     current_filters = FiltersEnvelope(...)
    #
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_dict_filters(
        self,
        mock_get_plan,
        mock_execute,
    ):
        mock_plan = MagicMock()
        mock_plan.sql = "SELECT * FROM generated_test_source"
        mock_plan.params = {}

        mock_get_plan.return_value = mock_plan

        mock_execute.return_value = {
            "items": [],
        }

        result = contract_analysis_repo.get_contract_analysis(
            filters={},
        )

        assert result["items"] == []
        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

        mock_get_plan.assert_called_once()

        args, kwargs = mock_get_plan.call_args

        assert isinstance(
            kwargs["filters"],
            FiltersEnvelope,
        )

        mock_execute.assert_called_once()

    # ============================================================
    # PAGINATION - HAS MORE
    #
    # Covers missing cursor branch inside:
    # _format_paginated_response()
    #
    # Cursor grain from source:
    #
    # project_level + fy_cd + pd_no
    #
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.encode_cursor")
    def test_format_paginated_response_has_more(
        self,
        mock_encode_cursor,
    ):
        mock_encode_cursor.return_value = "encoded-next-cursor"

        items = [
            {
                "project_level": "PROJ-001",
                "fy_cd": "2025",
                "pd_no": 1,
                "revenue": 1000.0,
                "total_count_hidden": 3,
            },
            {
                "project_level": "PROJ-001",
                "fy_cd": "2025",
                "pd_no": 2,
                "revenue": 1200.0,
                "total_count_hidden": 3,
            },
        ]

        result = contract_analysis_repo._format_paginated_response(
            items,
            limit=1,
        )

        assert len(result["items"]) == 1

        assert result["page"]["has_more"] is True
        assert result["page"]["cursor"] == "encoded-next-cursor"

        assert "total_count_hidden" not in result["items"][0]

        # IMPORTANT:
        # The repository builds:
        #
        # f"{project_level}|{fy_cd}|{pd_no}"
        #
        mock_encode_cursor.assert_called_once_with(
            "PROJ-001|2025|1"
        )

    # ============================================================
    # PAGINATION - NO MORE
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.encode_cursor")
    def test_format_paginated_response_no_more(
        self,
        mock_encode_cursor,
    ):
        items = [
            {
                "project_level": "PROJ-001",
                "fy_cd": "2025",
                "pd_no": 1,
                "revenue": 1000.0,
                "total_count_hidden": 1,
            }
        ]

        result = contract_analysis_repo._format_paginated_response(
            items,
            limit=10,
        )

        assert len(result["items"]) == 1
        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

        assert "total_count_hidden" not in result["items"][0]

        mock_encode_cursor.assert_not_called()

    # ============================================================
    # KEY LOOKUP - CUSTOM PAGE/SORT/COLUMNS
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_by_project_level_custom_options(
        self,
        mock_get_plan,
        mock_execute,
    ):
        mock_plan = MagicMock()
        mock_plan.sql = "SELECT * FROM generated_test_source"
        mock_plan.params = {}

        mock_get_plan.return_value = mock_plan

        mock_execute.return_value = {
            "items": [
                {
                    "project_level": "PROJ-100",
                    "fy_cd": "2026",
                    "pd_no": 3,
                    "revenue": 5000.0,
                }
            ]
        }

        page = PaginationModel(limit=5)

        sort = SortModel(
            field="fy_cd",
            order="asc",
        )

        columns = [
            "project_level",
            "fy_cd",
            "pd_no",
            "revenue",
        ]

        result = (
            contract_analysis_repo
            .get_contract_analysis_by_project_level(
                project_level="PROJ-100",
                page=page,
                sort=sort,
                columns=columns,
            )
        )

        assert len(result["items"]) == 1

        assert result["items"][0]["project_level"] == "PROJ-100"

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=sort,
            page=page,
            columns=columns,
        )

        mock_execute.assert_called_once_with(
            mock_plan.sql,
            mock_plan.params,
            limit=5,
        )
