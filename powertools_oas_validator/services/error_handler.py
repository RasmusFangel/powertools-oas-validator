import re
from typing import List

from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.exceptions import UnhandledValidationError
from powertools_oas_validator.types import ParamError, Request


class ErrorHandler:
    @staticmethod
    def raise_schema_validation_error(
        ex: Exception,
        request: Request,
    ) -> None:
        ex_type = type(ex)

        if issubclass(ex_type, ParameterValidationError):
            error = ErrorHandler._handle_parameter_error(ex, request)  # type: ignore
        elif ex_type == InvalidSchemaValue:
            error = ErrorHandler._handle_body_error(ex, request)  # type: ignore
        elif ex_type == SecurityNotFound:
            error = ErrorHandler._handle_security_error(ex, request)  # type: ignore
        else:
            raise UnhandledValidationError(
                f"'{ex_type}' is unhandled. Please open an issue on:"
                + "https://github.com/RasmusFangel/powertools-oas-validator/issues"
                + " and it will be resolved ASAP!"
            )
        raise error

    @staticmethod
    def _handle_security_error(
        ex: SecurityNotFound, request: Request
    ) -> SchemaValidationError:
        violating_schemes = ex.schemes[0]
        name = ErrorHandler._get_name(request, "security", violating_schemes[0])

        validation_message = f"'{ex.schemes}' are required security scheme(s)."

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
    def _handle_parameter_error(
        ex: ParameterValidationError, request: Request
    ) -> SchemaValidationError:
        name = ErrorHandler._get_name(request, "parameters", ex.name)

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
            err_msg = str(error.message)  # type: ignore

            violating_param = ErrorHandler._get_violating_param(err_msg)
            if "required" in err_msg:
                param = violating_param
            else:
                kv_swap = {v: k for k, v in ex.value.items()}  # type: ignore
                param = kv_swap[violating_param]

            violating_req_params.append(
                (
                    ParamError(
                        param=param,
                        validation_message=err_msg,
                        value=violating_param,
                    )
                )
            )
        try:
            name = ErrorHandler._get_name(
                request, "requestBody", violating_req_params[0].param
            )
            path = ErrorHandler._get_path(name)

        except KeyError:
            name = ErrorHandler._get_name(request, "request_body", "")
            path = ErrorHandler._get_path("")

        validation_message = ""

        if violating_req_params:
            try:
                validation_message = violating_req_params[0].validation_message
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

    @staticmethod
    def _get_violating_param(p: str) -> str:
        try:
            return re.search("'(.+?)'", p).group(1)  # type: ignore
        except IndexError:
            return ""


error_to_func = {
    ParameterValidationError: ErrorHandler._handle_parameter_error,
    InvalidSchemaValue: ErrorHandler._handle_body_error,
}
