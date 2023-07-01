from collections.abc import Callable
from typing import Dict

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext

from powertools_oas_validator.services.request_validator import RequestValidator
from powertools_oas_validator.services.spec_loader import SpecLoader
from powertools_oas_validator.services.spec_validator import SpecValidator
from powertools_oas_validator.types import ValidationConfig


@lambda_handler_decorator
def validate_request(
    handler: Callable,
    event: Dict,
    context: LambdaContext,
    oas_path: str,
    validate_spec=True,
    validate_body=True,
    validate_headers=True,
    validate_query=True,
    validate_path=True,
    validate_cookies=True,
) -> Callable:
    config = ValidationConfig(
        validate_body=validate_body,
        validate_headers=validate_headers,
        validate_query=validate_query,
        validate_path=validate_path,
        validate_cookies=validate_cookies,
    )

    # Validate File Path
    spec_loader = SpecLoader()
    spec_loader.validate_file(oas_path)

    # Setup Request Validator
    request_validator = RequestValidator(oas_path, config)

    # Setup SpecValidator
    spec_validator = SpecValidator(oas_path, event, spec_loader, request_validator)

    # If Spec Should be validated against OpenAPI Schema standard
    if validate_spec:
        spec_validator.validate_spec()

    # Validate Spec Against Request
    spec_validator.validate_request_against_spec()

    return handler(event, context)
