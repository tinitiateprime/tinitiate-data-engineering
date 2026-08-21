from unittest.mock import MagicMock, patch

from domain.services import po_funding_detail_service

# ============================================================
# GET PO FUNDING DETAIL BY PROJECT - EMPTY PROJECT ID
# ============================================================
def test_get_po_funding_detail_by_project_empty():
    result = po_funding_detail_service.get_po_funding_detail_by_project("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None


# ============================================================
# GET PO FUNDING DETAIL BY PROJECT - SUCCESS
# ============================================================
@patch(
    "domain.services.po_funding_detail_service."
    "PoFundingDetailSearchServiceResponse"
)
@patch(
    "domain.services.po_funding_detail_service."
    "PoFundingDetailResponse.model_validate"
)
@patch(
    "domain.services.po_funding_detail_service."
    "po_funding_detail_repo.get_po_funding_detail_by_project_id"
)
def test_get_po_funding_detail_by_project_success(
    mock_repo,
    mock_model_validate,
    mock_service_response,
):
    raw_item = {
        "project_id": "P-1001",
        "order_date": "2026-08-20",
    }

    mock_repo.return_value = {
        "items": [
            raw_item
        ],
        "page": {
            "cursor": "next-cursor",
            "has_more": True,
        },
    }

    validated_item = MagicMock()
    mock_model_validate.return_value = validated_item

    expected_response = MagicMock()
    mock_service_response.return_value = expected_response

    result = (
        po_funding_detail_service
        .get_po_funding_detail_by_project(
            "P-1001"
        )
    )

    assert result is expected_response

    # Repository must be called
    mock_repo.assert_called_once()

    repo_call = mock_repo.call_args

    assert repo_call.kwargs["project_id"] == "P-1001"
    assert repo_call.kwargs["columns"] is None

    # Default pagination
    assert repo_call.kwargs["page"] is not None

    # Default sort
    assert repo_call.kwargs["sort"].field == "order_date"
    assert repo_call.kwargs["sort"].order == "desc"

    # Repository item converted to response model
    mock_model_validate.assert_called_once_with(
        raw_item
    )

    # Service response created
    mock_service_response.assert_called_once()

    response_kwargs = (
        mock_service_response.call_args.kwargs
    )

    assert response_kwargs["items"] == [
        validated_item
    ]

    metadata = response_kwargs["metadata"]

    assert metadata.cursor == "next-cursor"
    assert metadata.has_more is True
    assert metadata.applied_filters is None
