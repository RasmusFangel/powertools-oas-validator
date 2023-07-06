import json
import os
from typing import Dict
from unittest.mock import MagicMock

import pytest
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError

from powertools_oas_validator.exceptions import (
    FileNotExistsError,
    NotSupportedFileTypeError,
)
from powertools_oas_validator.middleware import validate_request

app = APIGatewayRestResolver()


@app.get("/endpoint")
def dummy_func():
    ...


@validate_request(oas_path=os.getcwd() + "/tests/files/oas-valid.yaml")
def dummy_handler_valid_body(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/oas-valid-parameters.yaml")
def dummy_handler_valid_parameters(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/oas-valid-body-enum.yaml")
def dummy_handler_valid_enum(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/oas-valid-security.yaml")
def dummy_handler_valid_security(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/oas-invalid.yaml")
def dummy_handler_invalid(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/invalid-filetype.txt")
def dummy_handler_invalid_filetype(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


@validate_request(oas_path=os.getcwd() + "/tests/files/file-not-exist.yaml")
def dummy_handler_file_not_exist(event: Dict, context: LambdaContext) -> None:
    app.resolve(event, context)


def test_validate_oas_on_succes(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps({"param_1": "Param 1", "param_2": "Param 2"})

    dummy_handler_valid_body(mock_event, context)


def test_validate_oas_on_security_validation_error(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps({})

    try:
        dummy_handler_valid_security(mock_event, context)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "test-path.test-endpoint.security[BasicAuth]"
        assert ex.path == [
            "test-path",
            "test-endpoint",
            "security",
            "BasicAuth",
        ]
        assert (
            ex.validation_message
            == "'[['BasicAuth']]' are required security scheme(s)."
        )
    else:
        # If no exception is raised
        assert False


def test_validate_oas_on_requestBody_validation_error_enum(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps({"param_1": "invalid_param"})

    try:
        dummy_handler_valid_enum(mock_event, context)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "test-path.test-endpoint.requestBody[param_1]"
        assert ex.path == [
            "test-path",
            "test-endpoint",
            "requestBody",
            "param_1",
        ]
        assert ex.validation_message == "'invalid_param' is not one of ['value_1']"
    else:
        # If no exception is raised
        assert False


def test_validate_oas_requestBody_type_error(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps(
        {"param_1": "Param 1", "param_2": "Param 2", "param_3": "not an integer"}
    )

    try:
        dummy_handler_valid_body(mock_event, context)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "test-path.test-endpoint.requestBody[param_3]"
        assert ex.path == [
            "test-path",
            "test-endpoint",
            "requestBody",
            "param_3",
        ]
        assert ex.validation_message == "'not an integer' is not of type 'integer'"
    else:
        # If no exception is raised
        assert False


def test_validate_oas_on_requestBody_validation_error(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps({"param_invalid": "invalid_param"})

    try:
        dummy_handler_valid_body(mock_event, context)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "test-path.test-endpoint.requestBody[param_1]"
        assert ex.path == [
            "test-path",
            "test-endpoint",
            "requestBody",
            "param_1",
        ]
        assert ex.validation_message == "'param_1' is a required property"
    else:
        # If no exception is raised
        assert False


def test_validate_oas_on_parameters_validation_error(mock_event: Dict) -> None:
    context = MagicMock()

    try:
        dummy_handler_valid_parameters(mock_event, context)
    except Exception as ex:
        assert type(ex) == SchemaValidationError
        assert ex.name == "test-path.test-endpoint.parameters[query_param_1]"
        assert ex.path == [
            "test-path",
            "test-endpoint",
            "parameters",
            "query_param_1",
        ]
        assert ex.validation_message == "'query_param_1' is a required query parameter."
    else:
        # If no exception is raised
        assert False


def test_validate_oas_on_invalid_oas() -> None:
    event = {"path": "/endpoint", "httpMethod": "GET"}

    context = MagicMock()
    with pytest.raises(OpenAPIValidationError):
        dummy_handler_invalid(event, context)


def test_validate_oas_on_invalid_filetype() -> None:
    event = {"path": "/endpoint", "httpMethod": "GET"}

    context = MagicMock()
    with pytest.raises(NotSupportedFileTypeError):
        dummy_handler_invalid_filetype(event, context)


def test_validate_oas_on_file_not_exist() -> None:
    event = {"path": "/endpoint", "httpMethod": "GET"}

    context = MagicMock()
    with pytest.raises(FileNotExistsError):
        dummy_handler_file_not_exist(event, context)
