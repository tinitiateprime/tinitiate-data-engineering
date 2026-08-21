from unittest.mock import ANY, MagicMock, patch

from db.repositories import contract_program_managers_repo
from v1.schemas import FiltersEnvelope, PaginationModel, SortModel


class TestContractProgramManagersRepo:
    # ============================================================
    # get_program_managers_by_employee_id
    # ============================================================

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_get_program_managers_by_employee_id(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM HRIS.contract_program_managers_vw"
        plan.params = {"empl_id": "123456"}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [
                {
                    "EMPL_ID": "123456",
                    "contract_title": "Contract A",
                },
                {
                    "EMPL_ID": "123456",
                    "contract_title": "Contract B",
                },
            ]
        }

        result = (
            contract_program_managers_repo
            .get_program_managers_by_employee_id(
                "123456"
            )
        )

        assert result is not None
        assert len(result["items"]) == 2

        assert all(
            item["EMPL_ID"] == "123456"
            for item in result["items"]
        )

        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

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

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    def test_get_program_managers_by_employee_id_empty_input(
        self,
        mock_execute,
    ):
        result = (
            contract_program_managers_repo
            .get_program_managers_by_employee_id("")
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

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    def test_get_program_managers_by_employee_id_whitespace_input(
        self,
        mock_execute,
    ):
        result = (
            contract_program_managers_repo
            .get_program_managers_by_employee_id("   ")
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

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_program_managers_empty_result(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM HRIS.contract_program_managers_vw"
        plan.params = {}

        mock_get_plan.return_value = plan
        mock_execute.return_value = {
            "items": []
        }

        result = (
            contract_program_managers_repo
            .get_program_managers_by_employee_id(
                "NONE"
            )
        )

        assert result["items"] == []
        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

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
    # get_program_managers - generic search
    # ============================================================

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_get_program_managers_success(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM HRIS.contract_program_managers_vw"
        plan.params = {}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [
                {
                    "EMPL_ID": "123456",
                    "first_name": "John",
                    "last_name": "Smith",
                    "contract_title": "Contract A",
                }
            ]
        }

        result = (
            contract_program_managers_repo
            .get_program_managers()
        )

        assert result is not None
        assert len(result["items"]) == 1
        assert result["items"][0]["EMPL_ID"] == "123456"

        assert result["page"]["has_more"] is False
        assert result["page"]["cursor"] is None

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

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_get_program_managers_empty(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM HRIS.contract_program_managers_vw"
        plan.params = {}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": []
        }

        result = (
            contract_program_managers_repo
            .get_program_managers()
        )

        assert result["items"] == []
        assert result["page"]["cursor"] is None
        assert result["page"]["has_more"] is False

        mock_get_plan.assert_called_once()

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=ANY,
        )

    # ============================================================

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_get_program_managers_dict_filters(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT * FROM HRIS.contract_program_managers_vw"
        plan.params = {}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": []
        }

        filters = {
            "empl_id": {
                "eq": "123456"
            }
        }

        result = (
            contract_program_managers_repo
            .get_program_managers(
                filters=filters
            )
        )

        assert result is not None
        assert result["items"] == []

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

    @patch(
        "db.repositories.contract_program_managers_repo.execute_query"
    )
    @patch(
        "db.repositories.contract_program_managers_repo._builder.get_list_plan"
    )
    def test_get_program_managers_custom_options(
        self,
        mock_get_plan,
        mock_execute,
    ):
        plan = MagicMock()
        plan.sql = "SELECT custom"
        plan.params = {"x": 1}

        mock_get_plan.return_value = plan

        mock_execute.return_value = {
            "items": [
                {
                    "EMPL_ID": "123456",
                    "contract_title": "Contract A",
                }
            ]
        }

        filters = FiltersEnvelope(filters={})

        sort = SortModel(
            field="empl_id",
            order="asc",
        )

        page = PaginationModel(
            limit=5
        )

        columns = [
            "empl_id",
            "contract_title",
        ]

        result = (
            contract_program_managers_repo
            .get_program_managers(
                filters=filters,
                sort=sort,
                page=page,
                columns=columns,
            )
        )

        assert result is not None
        assert len(result["items"]) == 1

        mock_get_plan.assert_called_once_with(
            filters=filters,
            sort=sort,
            page=page,
            columns=columns,
        )

        mock_execute.assert_called_once_with(
            plan.sql,
            plan.params,
            limit=5,
        )

    # ============================================================
    # _format_paginated_response
    # ============================================================

    @patch(
        "db.repositories.contract_program_managers_repo.encode_cursor"
    )
    def test_format_paginated_response_has_more(
        self,
        mock_encode_cursor,
    ):
        mock_encode_cursor.return_value = (
            "encoded-next-cursor"
        )

        items = [
            {
                "EMPL_ID": "123456",
                "contract_title": "Contract A",
                "total_count_hidden": 3,
            },
            {
                "EMPL_ID": "123456",
                "contract_title": "Contract B",
                "total_count_hidden": 3,
            },
        ]

        result = (
            contract_program_managers_repo
            ._format_paginated_response(
                items,
                limit=1,
            )
        )

        assert len(result["items"]) == 1

        assert result["page"]["has_more"] is True

        assert (
            result["page"]["cursor"]
            == "encoded-next-cursor"
        )

        assert (
            "total_count_hidden"
            not in result["items"][0]
        )

        # Repository cursor format:
        # EMPL_ID|contract_title
        mock_encode_cursor.assert_called_once_with(
            "123456|Contract A"
        )

    # ============================================================

    @patch(
        "db.repositories.contract_program_managers_repo.encode_cursor"
    )
    def test_format_paginated_response_no_more(
        self,
        mock_encode_cursor,
    ):
        items = [
            {
                "EMPL_ID": "123456",
                "contract_title": "Contract A",
                "total_count_hidden": 1,
            }
        ]

        result = (
            contract_program_managers_repo
            ._format_paginated_response(
                items,
                limit=10,
            )
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

    def test_format_paginated_response_empty(self):
        result = (
            contract_program_managers_repo
            ._format_paginated_response(
                [],
                limit=10,
            )
        )

        assert result == {
            "items": [],
            "page": {
                "cursor": None,
                "has_more": False,
            },
        }

    # ============================================================
    # QuerySpec sanity checks
    # ============================================================

    def test_contract_program_managers_view_spec(self):
        spec = (
            contract_program_managers_repo
            .CONTRACT_PROGRAM_MANAGERS_VIEW_SPEC
        )

        assert (
            spec.table
            == "HRIS.contract_program_managers_vw"
        )

        assert spec.logical_id_field == "empl_id"

    # ============================================================

    def test_repository_builder_exists(self):
        assert (
            contract_program_managers_repo._builder
            is not None
        )

py -m pytest .\main-function\tests\unit\db\test_contract_program_managers_repo.py -v --cov=db.repositories.contract_program_managers_repo --cov-report=term-missing
