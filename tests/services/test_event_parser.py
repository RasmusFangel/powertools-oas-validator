from typing import Any, Dict

import pytest
from openapi_core.datatypes import RequestParameters
from werkzeug.datastructures import Headers, ImmutableMultiDict

from powertools_oas_validator.exceptions import InvalidEventError
from powertools_oas_validator.services.event_parser import EventParser

function_event_result = [
    ("get_path", {"path": "test_path"}, "test_path"),
    (
        "get_host_url",
        {"headers": {"X-Forwarded-Proto": "test proto", "Host": "Host"}},
        "test proto://Host",
    ),
    ("get_method", {"httpMethod": "POST"}, "post"),
    ("get_mimetype", {"headers": {"Content-Type": "test mimetype"}}, "test mimetype"),
    (
        "get_full_url_pattern",
        {
            "headers": {"X-Forwarded-Proto": "test proto", "Host": "Host"},
            "path": "/path",
        },
        "test proto://Host/path",
    ),
    (
        "get_parameters",
        {
            "headers": {"test": "header"},
            "queryStringParameters": {"query": "param"},
            "pathParameters": {"path": "parameter"},
        },
        RequestParameters(
            query=ImmutableMultiDict({"query": "param"}),
            header=Headers({"test": "header"}),
            cookie=ImmutableMultiDict({}),
            path={"path": "parameter"},
        ),
    ),
    ("get_body", {"body": {"test": "body"}}, '{"test": "body"}'),
    ("get_body", {"body": '{"test": "body"}'}, '{"test": "body"}'),
]


@pytest.mark.parametrize("function, event, result", function_event_result)
def test_getters(function: str, event: Dict, result: Any) -> None:
    event_parser = EventParser(event)

    assert result == getattr(event_parser, function)()


function_event_result = [
    ("get_path", {}, InvalidEventError),
    ("get_method", {}, InvalidEventError),
    ("get_mimetype", {"headers": {}}, InvalidEventError),
    ("get_host_url", {"headers": {}}, InvalidEventError),
    ("get_host_url", {"headers": {"X-Forwarded-Proto": "dummy"}}, InvalidEventError),
    (
        "get_full_url_pattern",
        {"headers": {"X-Forwarded-Proto": "dummy", "Host": "dummy"}},
        InvalidEventError,
    ),
    ("get_parameters", {}, InvalidEventError),
    (
        "get_parameters",
        {"queryStringParameters": {"para": "meter", "headers": {}}},
        InvalidEventError,
    ),
    ("get_body", {}, Exception),
]


@pytest.mark.parametrize("function, event, result", function_event_result)
def test_mandatory_getters_on_error(
    function: str, event: Dict, result: Exception
) -> None:
    event_parser = EventParser(event)

    if function == "get_body":
        assert getattr(event_parser, function)() == ""
    else:
        with pytest.raises(result):  # type: ignore
            getattr(event_parser, function)()
