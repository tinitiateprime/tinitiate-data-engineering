from unittest.mock import MagicMock, patch

from db.repositories import gl_details_repo


# ============================================================
# GET GL DETAILS BY PROJECT ID - EMPTY PROJECT ID
# ============================================================
def test_get_gl_details_by_project_id_empty():
    result = gl_details_repo.get_gl_details_by_project_id("   ")

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# ============================================================
# GET GL DETAILS BY PROJECT ID - SUCCESS
# ============================================================
@patch(
    "db.repositories.gl_details_repo.execute_query"
)
@patch(
    "db.repositories.gl_details_repo._builder.get_list_plan"
)
def test_get_gl_details_by_project_id_success(
    mock_get_plan,
    mock_execute,
):
    mock_get_plan.return_value = MagicMock(
        sql="SELECT * FROM gl_details",
        params=[],
    )

    mock_execute.return_value = {
        "items": [
            {
                "proj_id": "P-1001",
                "vchr_no": "V-1001",
                "time_stamp": "2026-08-20",
                "total_count_hidden": 1,
            }
        ]
    }

    result = gl_details_repo.get_gl_details_by_project_id(
        "P-1001"
    )

    assert isinstance(result, dict)
    assert len(result["items"]) == 1
    assert result["items"][0]["proj_id"] == "P-1001"
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once()

    plan_call = mock_get_plan.call_args

    assert plan_call.kwargs["columns"] is None
    assert plan_call.kwargs["page"] is not None
    assert plan_call.kwargs["sort"].field == "time_stamp"
    assert plan_call.kwargs["sort"].order == "desc"

    mock_execute.assert_called_once()


py -m pytest tests\unit\db\test_gl_details_repo.py -v --cov=db.repositories.gl_details_repo --cov-report=term-missing
