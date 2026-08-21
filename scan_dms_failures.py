# ============================================================
# GET PO FUNDING DETAIL BY PROJECT ID - EMPTY PROJECT ID
# ============================================================
def test_get_po_funding_detail_by_project_id_empty():
    result = repo.get_po_funding_detail_by_project_id("   ")

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
def test_get_po_funding_detail_by_project_id_success(monkeypatch):
    mock_plan = MagicMock()
    mock_plan.sql = "SELECT * FROM po_funding_detail"
    mock_plan.params = []

    mock_get_list_plan = MagicMock(
        return_value=mock_plan
    )

    mock_execute_query = MagicMock(
        return_value={
            "items": [
                {
                    "project_id": "P-1001",
                    "order_date": "2026-08-20",
                    "total_count_hidden": 1,
                }
            ]
        }
    )

    monkeypatch.setattr(
        repo._builder,
        "get_list_plan",
        mock_get_list_plan,
    )

    monkeypatch.setattr(
        repo,
        "execute_query",
        mock_execute_query,
    )

    result = repo.get_po_funding_detail_by_project_id(
        "P-1001"
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["project_id"] == "P-1001"

    assert result["page"]["has_more"] is False

    mock_get_list_plan.assert_called_once()
    mock_execute_query.assert_called_once()
