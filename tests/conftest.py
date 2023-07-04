from typing import Dict

import pytest

from powertools_oas_validator.services.event_parser import EventParser
from powertools_oas_validator.types import Request
from tests.files.event import event


@pytest.fixture()
def mock_event() -> Dict:
    return event


@pytest.fixture()
def mock_request(mock_event) -> Request:
    mock_event["body"] = {}

    return EventParser(mock_event).event_to_request()
