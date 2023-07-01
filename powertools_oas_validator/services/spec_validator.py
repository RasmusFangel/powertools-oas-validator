import re
from typing import Dict

from aws_lambda_powertools.utilities.validation import SchemaValidationError
from chocs import HttpRequest, Route
from openapi_spec_validator import validate_spec as oas_validator
from opyapi.errors import ValidationError

from powertools_oas_validator.services.request_validator import RequestValidatorABC
from powertools_oas_validator.services.spec_loader import SpecLoaderProtocol


class SpecValidator:
    def __init__(
        self,
        file_path: str,
        event: Dict,
        spec_loader: SpecLoaderProtocol,
        request_validator: RequestValidatorABC,
    ) -> None:
        self.file_path = file_path
        self.event = event
        self.spec_loader = spec_loader
        self.request_validator = request_validator

    def validate_spec(self) -> None:
        loaded_spec = self.spec_loader.read_from_file_name(self.file_path)

        # Raises OpenAPIValidationError on error
        oas_validator(spec=loaded_spec.spec_dict, spec_url=loaded_spec.spec_url)

    def validate_request_against_spec(self) -> None:
        request = self._event_to_request(self.event)

        validator_cache_key = f"{request.method} {request.path}".lower()
        if validator_cache_key not in self.request_validator._validators:
            self.request_validator._validators[
                validator_cache_key
            ] = self.request_validator.get_validators_for_uri(
                request.path,
                request.method,
                str(request.headers.get("content-type", "application/json")),
            )

        validators = self.request_validator._validators[validator_cache_key]
        if not validators:
            return
        for validator in validators:
            # Raises Validation Error
            # https://github.com/kodemore/chocs-openapi/blob/main/chocs_middleware/openapi/error.py
            try:
                validator(request)
            except ValidationError as ex:
                raise self.validator_error_to_schema_validaton_error(ex, request)

    def _event_to_request(self, event: Dict) -> HttpRequest:
        req = HttpRequest(
            path=self.request_validator.get_path(event),
            method=self.request_validator.get_method(event),
            headers=self.request_validator.get_headers(event),
            body=self.request_validator.get_body(event),
            query_string=self.request_validator.get_query_string(event),
        )

        req._cookies = self.request_validator.get_cookies(event)
        req.route = Route(req.path)

        return req

    def validator_error_to_schema_validaton_error(
        self, ex: ValidationError, request: HttpRequest
    ) -> SchemaValidationError:
        violating_param = re.search("`(.+?)`", ex.context["reason"])
        violating_param = violating_param.group(1)  # type: ignore

        name = f"paths.{request.path.lstrip('/')}.{request.method.value.lower()}"

        code_to_oas_path = {
            "invalid_request_body": "requestBody",
            "invalid_request_query": "parameters",
            "invalid_request_headers": "parameters",
            "invalid_request_uri": "parameters",
        }

        try:
            name = name + f".{code_to_oas_path[ex.code]}"
        except KeyError:
            ...  # No support for invalid_request_cookies

        name = name + f".[{violating_param}]"
        path = name.replace("[", "").replace("]", "").split(".")

        return SchemaValidationError(
            name=name,
            path=path,
            validation_message=ex.context["reason"],
            definition=ex.message,
        )
