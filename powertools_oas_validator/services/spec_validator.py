import re
from typing import Dict

from aws_lambda_powertools.utilities.validation import SchemaValidationError
from openapi_core import validate_request
from openapi_core.validation.request.validators import APICallRequestValidator
from openapi_core.validation.schemas.exceptions import ValidateError

from powertools_oas_validator.exceptions import UnsupportedOpenAPIVersion
from powertools_oas_validator.overrides import (
    V30RequestUnmarshaller,
    V31RequestUnmarshaller,
)
from powertools_oas_validator.services.event_parser import EventParserProtocol
from powertools_oas_validator.services.spec_loader import SpecLoaderProtocol
from powertools_oas_validator.services.spec_parser import SpecParser
from powertools_oas_validator.types import Request

marshaller_map = {"3.1": V31RequestUnmarshaller, "3.0": V30RequestUnmarshaller}


class SpecValidator:
    def __init__(
        self,
        file_path: str,
        event: Dict,
        spec_loader: SpecLoaderProtocol,
        event_parser: EventParserProtocol,
    ) -> None:
        self.file_path = file_path
        self.event = event
        self.spec_loader = spec_loader
        self.event_parser = event_parser

    def validate_request_against_spec(self) -> None:
        self.spec = self.spec_loader.read_from_file_name()

        request = self.event_parser.event_to_request()

        try:
            validate_request(
                request,
                spec=self.spec,
                base_url=request.host_url,
                cls=self._get_class(),  # type: ignore
            )

        except ValidateError as ex:
            raise self.schema_validaton_error(ex, request)

    def schema_validaton_error(
        self, ex: ValidateError, request: Request
    ) -> SchemaValidationError:
        error_message = ""

        error_path = ""
        violating_params = ""
        for error in ex.schema_errors:  # type: ignore
            if "property" in error.message:
                error_path = ".requestBody"
            elif "parameter" in error.message:
                error_path = ".parameters"
            try:
                violating_params = (
                    violating_params
                    + re.search("'(.+?)'", error.message).group(1)  # type: ignore
                    + ", "
                )
            except Exception:
                violating_params = ""

            error_message = error_message + error.message + ". "

        name = request.path.replace("/", ".").lstrip(".") + error_path
        name = name + f"[{violating_params.rstrip(', ')}]"
        error_message = error_message.rstrip(" ")
        path = name.replace("[", ".").replace("]", "").split(".")

        return SchemaValidationError(
            message=error_message,
            validation_message=error_message,
            name=name,
            path=path,
            value="",
            definition="",
            rule="",
            rule_definition="",
        )

    def _get_class(self) -> type[APICallRequestValidator]:
        version = SpecParser.get_openapi_version(self.spec)

        try:
            return marshaller_map[f"{version.major}.{version.minor}"]
        except KeyError:
            raise UnsupportedOpenAPIVersion(
                f"Unsupported OpenAPI version: '{str(version)}'"
            )
