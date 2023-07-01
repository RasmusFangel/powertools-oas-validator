import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from chocs import HttpHeaders, HttpMethod, HttpQueryString

from powertools_oas_validator.exceptions import InvalidEventError
from powertools_oas_validator.services.request_validator import RequestValidator
from powertools_oas_validator.types import ValidationConfig

function_event_result = [
    ("get_path", {"resource": "test_resource"}, "test_resource"),
    ("get_method", {"httpMethod": "GET"}, HttpMethod.GET),
    ("get_headers", {"headers": {"key": "value"}}, HttpHeaders({"key": "value"})),
    ("get_headers", {}, None),
    (
        "get_query_string",
        {"rawQueryString": "param_1=value_1"},
        HttpQueryString("param_1=value_1"),
    ),
    (
        "get_body",
        {"body": json.dumps({"param_1": "value_1"})},
        '{"param_1": "value_1"}',
    ),
    (
        "get_body",
        {"body": {"param_1": "value_1"}},
        '{"param_1": "value_1"}',
    ),
    ("get_body", {}, None),
]


@patch("powertools_oas_validator.services.request_validator.JsonSchema", MagicMock())
@pytest.mark.parametrize("function, event, result", function_event_result)
def test_getters(function: str, event: Dict, result: Any) -> None:
    v = RequestValidator(file_path="", validation_config=ValidationConfig())
    assert result == getattr(v, function)(event)


function_event_result = [
    ("get_path", {}, InvalidEventError),
    ("get_method", {"resource": "/test-resource"}, InvalidEventError),
]


@patch("powertools_oas_validator.services.request_validator.JsonSchema", MagicMock())
@pytest.mark.parametrize("function, event, result", function_event_result)
def test_mandatory_getters_on_error(
    function: str, event: Dict, result: Exception
) -> None:
    v = RequestValidator(file_path="", validation_config=ValidationConfig())
    with pytest.raises(result):
        getattr(v, function)(event)
