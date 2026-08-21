# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - EMPTY PROJECT ID
# ============================================================
def test_get_po_funding_detail_by_project_id_empty():
    result = get_po_funding_detail_by_project_id("   ")

    assert result == {
        "items": [],
        "page": {
            "cursor": None,
            "has_more": False,
        },
    }


# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - SUCCESS
# ============================================================
@patch(
    "db.repositories.po_funding_detail_repo.execute_query"
)
@patch(
    "db.repositories.po_funding_detail_repo._builder.get_list_plan"
)
def test_get_po_funding_detail_by_project_id_success(
    mock_get_plan,
    mock_execute,
):
    mock_get_plan.return_value = MagicMock(
        sql="SELECT * FROM po_funding_detail",
        params=[],
    )

    mock_execute.return_value = {
        "items": [
            {
                "project_id": "P-1001",
                "order_date": "2026-08-20",
                "total_count_hidden": 1,
            }
        ]
    }

    result = get_po_funding_detail_by_project_id(
        "P-1001"
    )

    assert isinstance(result, dict)
    assert len(result["items"]) == 1
    assert result["items"][0]["project_id"] == "P-1001"
    assert result["page"]["has_more"] is False

    mock_get_plan.assert_called_once()
    mock_execute.assert_called_once()
