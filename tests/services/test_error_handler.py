from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
    ParameterValidationError,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.exceptions import UnhandledValidationError
from powertools_oas_validator.services.error_handler import ErrorHandler
from powertools_oas_validator.services.event_parser import EventParser
from tests.conftest import MockValidationError

validation_errors = [
    MockValidationError(
        absolute_path=["param_3"],
        absolute_schema_path=["properties", "param_3", "type"],
        cause=None,
        context=[],
        instance="not an integer",
        json_path="param_3",
        message="'not an integer' is not of type 'integer'",
        parent=None,
        path=["param_3"],
        relative_path=["param_3"],
        relative_schema_path=["properties", "param_3", "type"],
        schema={"description": "Param 3 (int)", "type": "integer"},
        schema_path=["properties", "param_3", "type"],
        validator="type",
        validator_value="int",
    )
]


@pytest.mark.parametrize("validation_errors", [validation_errors])
def test_invalid_property_requestbody(
    mock_event: Dict, validation_errors: List[MagicMock]
) -> None:
    request = EventParser(mock_event).event_to_request()
    ex = InvalidSchemaValue(
        {  # type: ignore
            "param_1": "Param 1",
            "param_2": "Param 2",
            "param_3": "not an integer",
        },
        schema_errors=validation_errors,
        type="object",
    )

    try:
        ErrorHandler.raise_schema_validation_error(ex, request)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.message == "'not an integer' is not of type 'integer'"
        assert ex.path == [
            "requestBody",
            "content",
            "application/json",
            "schema",
            "properties",
            "param_3",
        ]
        assert ex.rule == "int"
        assert ex.rule_definition == "type"
        assert ex.validation_message == "'not an integer' is not of type 'integer'."
        assert ex.value == "not an integer"
        assert (
            ex.name == "requestBody.content.application/json.schema.properties[param_3]"
        )


def test_missing_required_requestBody(mock_event: Dict) -> None:
    request = EventParser(mock_event).event_to_request()
    ex = MissingRequiredRequestBody()

    try:
        ErrorHandler.raise_schema_validation_error(ex, request)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.message == "Missing required 'requestBody'"
        assert ex.validation_message == "Missing required 'requestBody'."


def test_invalid_parameter(mock_event: Dict) -> None:
    request = EventParser(mock_event).event_to_request()

    ex = CastError("not an integer", "integer")

    try:
        ErrorHandler.raise_schema_validation_error(ex, request)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.message == "Parameter 'not an integer' is not of type: 'integer'"
        assert (
            ex.validation_message
            == "Parameter 'not an integer' is not of type: 'integer'."
        )


def test_missing_required_parameter(mock_event: Dict) -> None:
    request = EventParser(mock_event).event_to_request()

    ex = ParameterValidationError(name="param_1", location="query")

    try:
        ErrorHandler.raise_schema_validation_error(ex, request)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.message == "'param_1' is a required 'query' parameter"
        assert ex.validation_message == "'param_1' is a required 'query' parameter."


def test_invalid_security(mock_event: Dict) -> None:
    request = EventParser(mock_event).event_to_request()

    ex = SecurityNotFound([["BasicAuth"]])

    try:
        ErrorHandler.raise_schema_validation_error(ex, request)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "security[BasicAuth]"
        assert ex.path == ["security", "BasicAuth"]
        assert ex.message == "'['BasicAuth']' are required security scheme(s)"
        assert (
            ex.validation_message == "'['BasicAuth']' are required security scheme(s)."
        )


def test_unhandled_error(mock_event: Dict) -> None:
    request = EventParser(mock_event).event_to_request()

    random_ex = TypeError("Unhandled")

    try:
        ErrorHandler.raise_schema_validation_error(random_ex, request)
    except Exception as ex:
        assert type(ex) == UnhandledValidationError
