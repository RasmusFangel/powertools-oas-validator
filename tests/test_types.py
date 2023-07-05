import json
from typing import Dict

from openapi_core.datatypes import RequestParameters

from powertools_oas_validator.services.event_parser import EventParser
from powertools_oas_validator.types import OpenAPIVersion, Request


def test_open_api_version() -> None:
    assert str(OpenAPIVersion(1, 2, 3)) == "1.2.3"


def test_request(mock_event: Dict) -> None:
    mock_event["body"] = json.dumps({"key": "value"})
    request = EventParser(mock_event).event_to_request()

    assert type(request) == Request
    assert request.body == '{"key": "value"}'
    assert request.full_url_pattern == "https://app.host.com/test-path/test-endpoint"
    assert request.host_url == "https://app.host.com"
    assert request.path == "/test-path/test-endpoint"
    assert request.mimetype == "application/json"
    assert type(request.parameters) == RequestParameters
