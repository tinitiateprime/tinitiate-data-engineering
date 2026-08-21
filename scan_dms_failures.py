import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import ResourceNotFoundError
from v1.handlers import project_status_detail


# ============================================================
# HELPERS
# ============================================================

def _unwrap_handler(func):
    """
    api_handler may wrap the real handler.
    This helper gets the original function so unit tests can
    directly test ValueError / ResourceNotFoundError behavior.
    """
    current = func

    while hasattr(current, "__wrapped__"):
        current = current.__wrapped__

    return current


def _metadata(
    cursor=None,
    has_more=False,
    applied_filters=None,
):
    """
    Lightweight metadata object used by mocked service responses.
    """

    class FakeMetadata:
        def __init__(self):
            self.cursor = cursor
            self.has_more = has_more
            self.applied_filters = applied_filters

        def model_dump(self):
            return {
                "cursor": self.cursor,
                "has_more": self.has_more,
                "applied_filters": self.applied_filters,
            }

    return FakeMetadata()


def _item(
    project_level="P-1001",
    period=1,
):
    """
    Lightweight project-status-detail item.
    """

    class FakeItem:
        def model_dump(self):
            return {
                "project_level": project_level,
                "period": period,
            }

    return FakeItem()


def _service_result(
    items=None,
    cursor=None,
    has_more=False,
):
    return SimpleNamespace(
        items=items if items is not None else [],
        metadata=_metadata(
            cursor=cursor,
            has_more=has_more,
        ),
    )


class FakeResponseItem:
    """
    Replaces V1ProjectStatusDetailResponseModel during handler tests.
    """

    def __init__(self, data):
        self.data = data

    @classmethod
    def model_validate(cls, data):
        return cls(data)

    def model_dump(self):
        return self.data


class FakeMetadataResponse:
    """
    Replaces V1MetadataModel during handler tests.
    """

    def __init__(self, **kwargs):
        self.data = kwargs

    def model_dump(self):
        return self.data


class FakeListResponse:
    """
    Replaces V1ProjectStatusDetailListResponseModel.
    """

    def __init__(self, metadata, data):
        self.metadata = metadata
        self.data = data

    def model_dump(self, by_alias=False):
        metadata = (
            self.metadata.model_dump()
            if hasattr(self.metadata, "model_dump")
            else self.metadata
        )

        data = [
            item.model_dump()
            if hasattr(item, "model_dump")
            else item
            for item in self.data
        ]

        return {
            "metadata": metadata,
            "data": data,
        }


# ============================================================
# GET /v1/projects/status-detail/{project_level}
# ============================================================

@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailListResponseModel",
    FakeListResponse,
)
@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailResponseModel",
    FakeResponseItem,
)
@patch.object(
    project_status_detail,
    "V1MetadataModel",
    FakeMetadataResponse,
)
@patch.object(
    project_status_detail,
    "get_project_status_detail_by_project",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
)
def test_get_project_status_detail_v1_success(
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_metadata_model,
    mock_response_model,
    mock_list_model,
):
    mock_get_path_param.return_value = "P-1001"

    mock_get_all_query_params.return_value = {
        "limit": "10",
        "cursor": None,
        "sortField": "period",
        "sortOrder": "desc",
    }

    mock_get_columns.return_value = None

    mock_service.return_value = _service_result(
        items=[
            _item(
                project_level="P-1001",
                period=1,
            )
        ],
        cursor=None,
        has_more=False,
    )

    handler = _unwrap_handler(
        project_status_detail.get_project_status_detail_v1
    )

    result = handler(
        {"pathParameters": {"project_level": "P-1001"}},
        None,
    )

    assert result is not None
    assert "data" in result
    assert len(result["data"]) == 1
    assert result["data"][0]["project_level"] == "P-1001"
    assert result["data"][0]["period"] == 1

    mock_get_path_param.assert_called_once()

    mock_get_all_query_params.assert_called_once()

    mock_get_columns.assert_called_once()

    mock_service.assert_called_once()

    kwargs = mock_service.call_args.kwargs

    assert kwargs["project_level"] == "P-1001"
    assert kwargs["page"].limit == 10
    assert kwargs["sort"].field == "period"
    assert kwargs["sort"].order == "desc"
    assert kwargs["columns"] is None


@patch.object(
    project_status_detail.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
)
def test_get_project_status_detail_v1_default_query_parameters(
    mock_get_path_param,
    mock_get_all_query_params,
):
    mock_get_path_param.return_value = "P-1001"
    mock_get_all_query_params.return_value = {}

    with patch.object(
        project_status_detail.LambdaUtils,
        "get_columns_query_parameter",
        return_value=None,
    ), patch.object(
        project_status_detail,
        "get_project_status_detail_by_project",
        return_value=_service_result(
            items=[_item()]
        ),
    ), patch.object(
        project_status_detail,
        "V1ProjectStatusDetailListResponseModel",
        FakeListResponse,
    ), patch.object(
        project_status_detail,
        "V1ProjectStatusDetailResponseModel",
        FakeResponseItem,
    ), patch.object(
        project_status_detail,
        "V1MetadataModel",
        FakeMetadataResponse,
    ):

        handler = _unwrap_handler(
            project_status_detail.get_project_status_detail_v1
        )

        result = handler(
            {"pathParameters": {"project_level": "P-1001"}},
            None,
        )

        assert result is not None
        assert len(result["data"]) == 1


@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
    return_value=None,
)
def test_get_project_status_detail_v1_missing_project_level(
    mock_get_path_param,
):
    handler = _unwrap_handler(
        project_status_detail.get_project_status_detail_v1
    )

    with pytest.raises(
        ValueError,
        match="Project ID is required",
    ):
        handler({}, None)


@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
    return_value="search",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_all_query_params",
    return_value={},
)
def test_get_project_status_detail_v1_search_used_as_project_level(
    mock_get_all_query_params,
    mock_get_path_param,
):
    handler = _unwrap_handler(
        project_status_detail.get_project_status_detail_v1
    )

    with pytest.raises(ValueError):
        handler(
            {
                "pathParameters": {
                    "project_level": "search",
                }
            },
            None,
        )


@patch.object(
    project_status_detail,
    "get_project_status_detail_by_project",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_columns_query_parameter",
    return_value=None,
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_all_query_params",
    return_value={},
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
    return_value="P-9999",
)
def test_get_project_status_detail_v1_not_found(
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
):
    mock_service.return_value = _service_result(
        items=[]
    )

    handler = _unwrap_handler(
        project_status_detail.get_project_status_detail_v1
    )

    with pytest.raises(ResourceNotFoundError):
        handler(
            {
                "pathParameters": {
                    "project_level": "P-9999",
                }
            },
            None,
        )


@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailListResponseModel",
    FakeListResponse,
)
@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailResponseModel",
    FakeResponseItem,
)
@patch.object(
    project_status_detail,
    "V1MetadataModel",
    FakeMetadataResponse,
)
@patch.object(
    project_status_detail,
    "get_project_status_detail_by_project",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_columns_query_parameter",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_all_query_params",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_path_param",
)
def test_get_project_status_detail_v1_query_parameters(
    mock_get_path_param,
    mock_get_all_query_params,
    mock_get_columns,
    mock_service,
    mock_metadata_model,
    mock_response_model,
    mock_list_model,
):
    mock_get_path_param.return_value = "P-2001"

    mock_get_all_query_params.return_value = {
        "limit": "25",
        "cursor": "abc123",
        "sortField": "period",
        "sortOrder": "asc",
    }

    mock_get_columns.return_value = [
        "project_level",
        "period",
    ]

    mock_service.return_value = _service_result(
        items=[
            _item(
                project_level="P-2001",
                period=2,
            )
        ]
    )

    handler = _unwrap_handler(
        project_status_detail.get_project_status_detail_v1
    )

    result = handler({}, None)

    assert result["data"][0]["project_level"] == "P-2001"

    kwargs = mock_service.call_args.kwargs

    assert kwargs["project_level"] == "P-2001"
    assert kwargs["page"].limit == 25
    assert kwargs["page"].cursor == "abc123"
    assert kwargs["sort"].field == "period"
    assert kwargs["sort"].order == "asc"
    assert kwargs["columns"] == [
        "project_level",
        "period",
    ]


# ============================================================
# POST /v1/projects/status-detail/search
# ============================================================

@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailListResponseModel",
    FakeListResponse,
)
@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailResponseModel",
    FakeResponseItem,
)
@patch.object(
    project_status_detail,
    "V1MetadataModel",
    FakeMetadataResponse,
)
@patch.object(
    project_status_detail,
    "FiltersEnvelope",
)
@patch.object(
    project_status_detail,
    "search_project_status_detail",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_json_body",
)
def test_search_project_status_detail_v1_success(
    mock_get_json_body,
    mock_search,
    mock_filters_envelope,
    mock_metadata_model,
    mock_response_model,
    mock_list_model,
):
    body = {
        "filters": {
            "project_level": {
                "eq": "P-1001",
            }
        },
        "sort": {
            "field": "period",
            "order": "desc",
        },
        "page": {
            "limit": 10,
        },
        "columns": [
            "project_level",
            "period",
        ],
    }

    mock_get_json_body.return_value = body

    mock_filters_envelope.return_value = MagicMock()

    mock_search.return_value = _service_result(
        items=[
            _item(
                project_level="P-1001",
                period=1,
            )
        ]
    )

    handler = _unwrap_handler(
        project_status_detail.search_project_status_detail_v1
    )

    result = handler({}, None)

    assert result is not None
    assert "data" in result
    assert len(result["data"]) == 1
    assert result["data"][0]["project_level"] == "P-1001"

    mock_search.assert_called_once()

    kwargs = mock_search.call_args.kwargs

    assert kwargs["filters"] == body["filters"]
    assert kwargs["sort"].field == "period"
    assert kwargs["sort"].order == "desc"
    assert kwargs["page"].limit == 10
    assert kwargs["columns"] == [
        "project_level",
        "period",
    ]


@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailListResponseModel",
    FakeListResponse,
)
@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailResponseModel",
    FakeResponseItem,
)
@patch.object(
    project_status_detail,
    "V1MetadataModel",
    FakeMetadataResponse,
)
@patch.object(
    project_status_detail,
    "FiltersEnvelope",
)
@patch.object(
    project_status_detail,
    "search_project_status_detail",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_json_body",
)
def test_search_project_status_detail_v1_empty_body(
    mock_get_json_body,
    mock_search,
    mock_filters_envelope,
    mock_metadata_model,
    mock_response_model,
    mock_list_model,
):
    mock_get_json_body.return_value = {}

    mock_filters_envelope.return_value = MagicMock()

    mock_search.return_value = _service_result(
        items=[]
    )

    handler = _unwrap_handler(
        project_status_detail.search_project_status_detail_v1
    )

    result = handler({}, None)

    assert result is not None
    assert result["data"] == []

    mock_search.assert_called_once()

    kwargs = mock_search.call_args.kwargs

    assert kwargs["filters"] == {}
    assert kwargs["columns"] is None


@patch.object(
    project_status_detail.LambdaUtils,
    "get_json_body",
)
def test_search_project_status_detail_v1_invalid_json(
    mock_get_json_body,
):
    mock_get_json_body.side_effect = json.JSONDecodeError(
        "Invalid JSON",
        "{}",
        0,
    )

    handler = _unwrap_handler(
        project_status_detail.search_project_status_detail_v1
    )

    with pytest.raises(
        ValueError,
        match="Invalid JSON body provided",
    ):
        handler({}, None)


@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailListResponseModel",
    FakeListResponse,
)
@patch.object(
    project_status_detail,
    "V1ProjectStatusDetailResponseModel",
    FakeResponseItem,
)
@patch.object(
    project_status_detail,
    "V1MetadataModel",
    FakeMetadataResponse,
)
@patch.object(
    project_status_detail,
    "FiltersEnvelope",
)
@patch.object(
    project_status_detail,
    "search_project_status_detail",
)
@patch.object(
    project_status_detail.LambdaUtils,
    "get_json_body",
)
def test_search_project_status_detail_v1_custom_page_and_sort(
    mock_get_json_body,
    mock_search,
    mock_filters_envelope,
    mock_metadata_model,
    mock_response_model,
    mock_list_model,
):
    mock_get_json_body.return_value = {
        "filters": {},
        "sort": {
            "field": "period",
            "order": "asc",
        },
        "page": {
            "limit": 5,
            "cursor": "cursor-123",
        },
        "columns": [
            "project_level",
            "period",
        ],
    }

    mock_filters_envelope.return_value = MagicMock()

    mock_search.return_value = _service_result(
        items=[
            _item(
                project_level="P-3001",
                period=3,
            )
        ],
        cursor="next-cursor",
        has_more=True,
    )

    handler = _unwrap_handler(
        project_status_detail.search_project_status_detail_v1
    )

    result = handler({}, None)

    assert result is not None
    assert len(result["data"]) == 1

    kwargs = mock_search.call_args.kwargs

    assert kwargs["page"].limit == 5
    assert kwargs["page"].cursor == "cursor-123"
    assert kwargs["sort"].field == "period"
    assert kwargs["sort"].order == "asc"


# ============================================================
# ROUTE / FUNCTION EXISTENCE
# ============================================================

def test_get_project_status_detail_handler_exists():
    assert hasattr(
        project_status_detail,
        "get_project_status_detail_v1",
    )

    assert callable(
        project_status_detail.get_project_status_detail_v1
    )


def test_search_project_status_detail_handler_exists():
    assert hasattr(
        project_status_detail,
        "search_project_status_detail_v1",
    )

    assert callable(
        project_status_detail.search_project_status_detail_v1
    )
