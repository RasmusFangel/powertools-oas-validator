import re
from typing import List, Union

from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.types import Request


class ErrorHandler:
    @staticmethod
    def to_schema_validation_error(
        ex: Union[ParameterValidationError, InvalidSchemaValue], request: Request
    ) -> SchemaValidationError:
        if issubclass(type(ex), ParameterValidationError):
            return ErrorHandler._handle_parameter_error(ex, request)  # type: ignore
        elif type(ex) == InvalidSchemaValue:
            return ErrorHandler._handle_body_error(ex, request)
        else:
            raise ValueError(
                f"'{type(ex)}' is not mapped to a function. Consider adding it."
            )

    @staticmethod
    def _handle_parameter_error(
        ex: ParameterValidationError, request: Request
    ) -> SchemaValidationError:
        name = ErrorHandler._get_name(request, "parameters", ex.name)  # type: ignore

        validation_message = f"'{ex.name}' is a required {ex.location} parameter."

        return SchemaValidationError(
            message=None,
            validation_message=validation_message,
            name=name,
            path=ErrorHandler._get_path(name),
            value=None,
            definition=None,
            rule=None,
            rule_definition=None,
        )

    @staticmethod
    def _handle_body_error(
        ex: InvalidSchemaValue, request: Request
    ) -> SchemaValidationError:
        violating_req_params = []

        for error in ex.schema_errors:
            if "required" in error.message:  # type: ignore
                try:
                    violating_req_params.append(
                        re.search("'(.+?)'", error.message).group(1)  # type: ignore
                    )
                except IndexError:
                    ...
            else:
                raise ValueError(
                    (
                        "Unmapped error type. Consider adding case for"
                        + f"'{ex.message}'"  # type: ignore
                    )
                )

        try:
            name = ErrorHandler._get_name(
                request, "requestBody", violating_req_params[0]
            )
            path = ErrorHandler._get_path(name)

        except KeyError:
            name = ErrorHandler._get_name(request, "request_body", "")
            path = ErrorHandler._get_path("")

        validation_message = ""

        if violating_req_params:
            try:
                validation_message = f"{violating_req_params} are required propertie(s)"
            except KeyError:
                ...

        return SchemaValidationError(
            message=None,
            validation_message=validation_message,
            name=name,
            path=path,
            value=None,
            definition=None,
            rule=None,
            rule_definition=None,
        )

    @staticmethod
    def _get_name(request: Request, path: str, violating_param: str) -> str:
        return (
            request.path.replace("/", ".").lstrip(".") + f".{path}[{violating_param}]"
        )

    @staticmethod
    def _get_path(name: str) -> List[str]:
        return name.replace("[", ".").replace("]", "").split(".")


error_to_func = {
    ParameterValidationError: ErrorHandler._handle_parameter_error,
    InvalidSchemaValue: ErrorHandler._handle_body_error,
}