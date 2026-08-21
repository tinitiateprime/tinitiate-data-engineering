from unittest.mock import MagicMock, patch

from domain.services import gl_details_service

# ============================================================
# GET GL DETAILS BY PROJECT - EMPTY PROJECT ID
# ============================================================
def test_get_gl_details_by_project_empty():
    result = gl_details_service.get_gl_details_by_project("")

    assert result.items == []
    assert result.metadata.cursor is None
    assert result.metadata.has_more is False
    assert result.metadata.applied_filters is None


# ============================================================
# GET GL DETAILS BY PROJECT - SUCCESS
# ============================================================
@patch(
    "domain.services.gl_details_service."
    "GlDetailsSearchServiceResponse"
)
@patch(
    "domain.services.gl_details_service."
    "GlDetailsResponse.model_validate"
)
@patch(
    "domain.services.gl_details_service."
    "gl_details_repo.get_gl_details_by_project_id"
)
def test_get_gl_details_by_project_success(
    mock_repo,
    mock_model_validate,
    mock_service_response,
):
    raw_item = {
        "proj_id": "P-1001",
        "time_stamp": "2026-08-20",
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

    result = gl_details_service.get_gl_details_by_project(
        "P-1001"
    )

    assert result is expected_response

    # Repository call
    mock_repo.assert_called_once()

    repo_call = mock_repo.call_args

    assert repo_call.kwargs["proj_id"] == "P-1001"
    assert repo_call.kwargs["columns"] is None

    # Default pagination
    assert repo_call.kwargs["page"] is not None

    # Default GL sort
    assert repo_call.kwargs["sort"].field == "time_stamp"
    assert repo_call.kwargs["sort"].order == "desc"

    # Validate DB item
    mock_model_validate.assert_called_once_with(
        raw_item
    )

    # Validate service response
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

py -m pytest tests\unit\domain\services\test_gl_details_service.py -v --cov=domain.services.gl_details_service --cov-report=term-missing
