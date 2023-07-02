from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from jsonschema.exceptions import ValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.overrides.unmarshallers import V30RequestUnmarshaller
from powertools_oas_validator.services.spec_validator import SpecValidator


@patch("powertools_oas_validator.services.spec_validator.validate_request")
def test_validate_request_against_spec(mock_validate_request: MagicMock) -> None:
    spec_mock = MagicMock()

    spec_mock.accessor = MagicMock()
    spec_mock.accessor.lookup = {"openapi": "3.0.0"}

    mock_loader = MagicMock()
    mock_loader.read_from_file_name = MagicMock(return_value=spec_mock)

    mock_request = MagicMock()
    mock_request.host_url = "host_url"

    mock_parser = MagicMock()
    mock_parser.event_to_request = MagicMock(return_value=mock_request)

    spec_validator = SpecValidator("", {}, mock_loader, mock_parser)

    spec_validator.validate_request_against_spec()

    mock_validate_request.assert_called_once_with(
        mock_request,
        spec=spec_mock,
        base_url="host_url",
        cls=V30RequestUnmarshaller,
    )


@patch("powertools_oas_validator.services.spec_validator.validate_request")
def test_validate_request_against_spec_on_error(
    mock_validate_request: MagicMock,
) -> None:
    expected_error = InvalidSchemaValue(
        "",
        schema_errors=[
            ValidationError(
                message="required property 'test'",
            )
        ],
        type=MagicMock(),
    )
    mock_validate_request.side_effect = [expected_error]
    spec_mock = MagicMock()

    spec_mock.accessor = MagicMock()
    spec_mock.accessor.lookup = {"openapi": "3.0.0"}

    mock_loader = MagicMock()
    mock_loader.read_from_file_name = MagicMock(return_value=spec_mock)

    mock_request = MagicMock()
    mock_request.host_url = "host_url"

    mock_parser = MagicMock()
    mock_parser.event_to_request = MagicMock(return_value=mock_request)

    spec_validator = SpecValidator("", {}, mock_loader, mock_parser)

    with pytest.raises(SchemaValidationError):
        spec_validator.validate_request_against_spec()

    mock_validate_request.assert_called_once_with(
        mock_request,
        spec=spec_mock,
        base_url="host_url",
        cls=V30RequestUnmarshaller,
    )
