from unittest.mock import MagicMock

import pytest
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.exceptions import UnhandledValidationError
from powertools_oas_validator.services.error_handler import ErrorHandler
from powertools_oas_validator.types import Request

validation_error = MagicMock()
validation_error.message = "'test' required"

ex_result = [
    (ParameterValidationError(name="test", location="test"), SchemaValidationError),
    (
        InvalidSchemaValue(value="test", type="test", schema_errors=[validation_error]),
        SchemaValidationError,
    ),
    (SecurityNotFound(schemes=[["test"]]), SchemaValidationError),
    (Exception, UnhandledValidationError),
]


@pytest.mark.parametrize("ex, result", ex_result)
def test_to_schema_validation_error(
    ex: Exception, result: Exception, mock_request: Request
) -> None:
    with pytest.raises(result):  # type: ignore
        ErrorHandler.raise_schema_validation_error(ex, mock_request)  # type: ignore
