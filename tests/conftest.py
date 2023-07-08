from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from powertools_oas_validator.services.event_parser import EventParser
from powertools_oas_validator.types import Request
from tests.files.event import event


@dataclass
class MockValidationError:
    absolute_path: List
    absolute_schema_path: List
    cause: Optional[str]
    context: List[str]
    instance: str
    json_path: str
    message: str
    parent: Optional[str]
    path: List
    relative_path: List
    relative_schema_path: List
    schema: Dict
    schema_path: List
    validator: str
    validator_value: str


@pytest.fixture
def mock_event() -> Dict:
    return event


@pytest.fixture
def mock_request(mock_event) -> Request:
    mock_event["body"] = {}

    return EventParser(mock_event).event_to_request()


@pytest.fixture
def validation_errors(errs: List[MockValidationError]) -> List[MagicMock]:
    res: List[MagicMock] = []
    for err in errs:
        error = MagicMock()

        error.absolute_path = err.absolute_path
        error.absolute_schema_path = deque(err.schema_path)
        error.cause = err.cause
        error.context = err.context
        error.instance = err.instance
        error.json_path = f"$.{err.json_path}"
        error.message = err.message
        error.parent = err.parent
        error.path = deque(err.path)
        error.relative_path = deque(err.relative_path)
        error.relative_schema_path = deque(err.relative_schema_path)
        error.schema = err.schema
        error.schema_path = deque(err.schema_path)
        error.validator = err.validator
        error.validator_value = err.validator_value

        res.append(error)

    return res
