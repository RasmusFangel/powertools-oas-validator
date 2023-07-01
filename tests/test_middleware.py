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
def dummy_handler_valid(event: Dict, context: LambdaContext) -> None:
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

    dummy_handler_valid(mock_event, context)


def test_validate_oas_on_validation_error(mock_event: Dict) -> None:
    context = MagicMock()
    mock_event["body"] = json.dumps({"param_invalid": "invalid_param"})
    with pytest.raises(SchemaValidationError):
        dummy_handler_valid(mock_event, context)


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
