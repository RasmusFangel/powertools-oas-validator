from collections.abc import Callable
from typing import Dict

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext

from powertools_oas_validator.services.event_parser import EventParser
from powertools_oas_validator.services.spec_loader import SpecLoader
from powertools_oas_validator.services.spec_validator import SpecValidator


@lambda_handler_decorator
def validate_request(
    handler: Callable,
    event: Dict,
    context: LambdaContext,
    oas_path: str,
) -> Callable:
    # Setup Spec Loader
    spec_loader = SpecLoader(oas_path)

    # Setup Event Parser
    event_parser = EventParser(event)

    # Setup SpecValidator
    spec_validator = SpecValidator(oas_path, event, spec_loader, event_parser)

    # Validate Spec Against Event
    spec_validator.validate_request_against_spec()

    return handler(event, context)
