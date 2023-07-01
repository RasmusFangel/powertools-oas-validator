from typing import Dict

import pytest

from tests.files.event import event


@pytest.fixture()
def mock_event() -> Dict:
    return event
