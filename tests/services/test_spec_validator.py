from unittest.mock import MagicMock, patch

import pytest
from chocs import HttpCookieJar, HttpMethod, HttpRequest
from chocs_middleware.openapi.middleware import Callable, List

from powertools_oas_validator.services.spec_validator import SpecValidator


@patch("powertools_oas_validator.services.spec_validator.oas_validator")
def test_spec_validator_validate_spec(mock_oas_validator: MagicMock) -> None:
    mock_loaded_spec = MagicMock()
    mock_loaded_spec.spec_dict = MagicMock()
    mock_loaded_spec.spec_url = MagicMock()

    mock_spec_loader = MagicMock()
    mock_spec_loader.read_from_file_name = MagicMock(return_value=mock_loaded_spec)

    validator = SpecValidator(
        file_path="",
        event={},
        spec_loader=mock_spec_loader,
        request_validator=MagicMock(),
    )

    validator.validate_spec()

    mock_spec_loader.read_from_file_name.assert_called_once_with("")
    mock_oas_validator.assert_called_once_with(
        spec=mock_loaded_spec.spec_dict, spec_url=mock_loaded_spec.spec_url
    )


@pytest.mark.parametrize("validators", [[MagicMock()], []])
def test_spec_validator_validate_request_against_spec(
    validators: List[Callable],
) -> None:
    mock_request_validator = MagicMock()
    mock_request_validator.get_path = MagicMock(return_value="/placeholder")
    mock_request_validator.get_method = MagicMock(return_value="GET")
    mock_request_validator.get_headers = MagicMock(return_value=None)
    mock_request_validator.get_body = MagicMock(return_value=None)
    mock_request_validator.get_query_string = MagicMock(return_value=None)
    mock_request_validator.get_cookies = MagicMock(return_value=HttpCookieJar())

    mock_request_validator._validators = {}
    mock_request_validator.get_validators_for_uri = MagicMock(return_value=validators)

    validator = SpecValidator(
        file_path="",
        event={"resource": "/placeholder", "httpMethod": "GET", "body": {}},
        spec_loader=MagicMock(),
        request_validator=mock_request_validator,
    )

    validator.validate_request_against_spec()

    mock_request_validator.get_validators_for_uri.assert_called_once_with(
        "/placeholder", HttpMethod.GET, "application/json"
    )

    for mock_validator in validators:
        mock_validator.assert_called_once_with(
            HttpRequest(path="/placeholder", method=HttpMethod.GET)
        )
