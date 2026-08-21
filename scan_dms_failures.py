from unittest.mock import ANY, MagicMock, patch

from db.repositories import contract_analysis_repo
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


class TestContractAnalysisRepo:

    # ============================================================
    # get_contract_analysis_by_project_level
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_by_project_level(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM gold.contract_analysis_vw"
        plan.params = {"project_level": "PROJ-001"}

        mock_get_plan.return_value = plan

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

        assert result is not None
        assert "items" in result
        assert "page" in result
        assert len(result["items"]) == 2

        assert all(
            item["project_level"] == "PROJ-001"
            for item in result["items"]
        )

        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

        mock_get_plan.assert_called_once()

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )

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
    # get_contract_analysis
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_contract_analysis_empty_result(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM gold.contract_analysis_vw"
        plan.params = {}

        mock_get_plan.return_value = plan
        mock_execute.return_value = {
            "items": [],
        }

        result = contract_analysis_repo.get_contract_analysis()

        assert result == {
            "items": [],
            "page": {
                "cursor": None,
                "has_more": False,
            },
        }

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=ANY,
            page=ANY,
            columns=None,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )

    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_success(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM gold.contract_analysis_vw"
        plan.params = {}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [
                {
                    "project_level": "PROJ-001",
                    "fy_cd": "2025",
                    "pd_no": 1,
                    "revenue": 1000.0,
                }
            ]
        }

        result = contract_analysis_repo.get_contract_analysis()

        assert result is not None
        assert "items" in result
        assert "page" in result
        assert len(result["items"]) == 1

        assert result["items"][0]["project_level"] == "PROJ-001"
        assert result["items"][0]["fy_cd"] == "2025"
        assert result["items"][0]["pd_no"] == 1

        assert result["page"]["cursor"] is None
        assert result["page"]["has_more"] is False

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=ANY,
            page=ANY,
            columns=None,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )

    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_dict_filters(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM gold.contract_analysis_vw"
        plan.params = {}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [],
        }

        filters = {
            "project_level": {
                "eq": "PROJ-001",
            }
        }

        result = contract_analysis_repo.get_contract_analysis(
            filters=filters
        )

        assert result is not None
        assert result["items"] == []
        assert result["page"]["cursor"] is None
        assert result["page"]["has_more"] is False

        mock_get_plan.assert_called_once()

        call_kwargs = mock_get_plan.call_args.kwargs

        assert isinstance(
            call_kwargs["filters"],
            FiltersEnvelope,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )

    # ============================================================
    # _format_paginated_response
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

        assert (
            "total_count_hidden"
            not in result["items"][0]
        )

        # IMPORTANT:
        # contract_analysis_repo.py builds:
        #
        # f"{project_level}_{fy_cd}_{pd_no}"
        #
        # so the expected cursor input uses underscores.
        mock_encode_cursor.assert_called_once_with(
            "PROJ-001_2025_1"
        )

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

        assert (
            "total_count_hidden"
            not in result["items"][0]
        )

        mock_encode_cursor.assert_not_called()

    # ============================================================
    # Custom pagination / sort / columns
    # ============================================================

    @patch("db.repositories.contract_analysis_repo.execute_query")
    @patch("db.repositories.contract_analysis_repo._builder.get_list_plan")
    def test_get_contract_analysis_by_project_level_custom_options(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM gold.contract_analysis_vw"
        plan.params = {
            "project_level": "PROJ-001",
        }

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [
                {
                    "project_level": "PROJ-001",
                    "fy_cd": "2025",
                    "pd_no": 1,
                    "revenue": 1000.0,
                }
            ]
        }

        page = PaginationModel(
            limit=5,
        )

        sort = SortModel(
            field="fy_cd",
            order="desc",
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
                project_level="PROJ-001",
                page=page,
                sort=sort,
                columns=columns,
            )
        )

        assert result is not None
        assert len(result["items"]) == 1

        mock_get_plan.assert_called_once_with(
            filters=ANY,
            sort=sort,
            page=page,
            columns=columns,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=5,
        )
