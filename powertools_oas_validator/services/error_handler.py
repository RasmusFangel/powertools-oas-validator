from typing import Union

from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
    ParameterValidationError,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue

from powertools_oas_validator.exceptions import UnhandledValidationError
from powertools_oas_validator.types import Request


class ErrorHandler:
    @staticmethod
    def raise_schema_validation_error(
        ex: Exception,
        request: Request,
    ) -> None:
        ex_type = type(ex)

        if issubclass(ex_type, ParameterValidationError) or ex_type == CastError:
            error = ErrorHandler._handle_parameter_error(ex)  # type: ignore
        elif ex_type == InvalidSchemaValue or ex_type == MissingRequiredRequestBody:
            error = ErrorHandler._handle_body_error(ex, request)  # type: ignore
        elif ex_type == SecurityNotFound:
            error = ErrorHandler._handle_security_error(ex)  # type: ignore
        else:
            raise UnhandledValidationError(
                f"'{ex_type}' is unhandled. Please open an issue on:"
                + "https://github.com/RasmusFangel/powertools-oas-validator/issues"
                + " and it will be resolved ASAP!"
            )
        raise error

    @staticmethod
    def _handle_security_error(ex: SecurityNotFound) -> SchemaValidationError:
        violating_schemes = ex.schemes[0]
        name = f"security[{violating_schemes[0]}]"
        path = name.replace("]", "").split("[")
        validation_message = f"'{violating_schemes}' are required security scheme(s)"

        return SchemaValidationError(
            message=validation_message,
            validation_message=validation_message + ".",
            name=name,
            path=path,
            value=None,
            definition=None,
            rule=None,
            rule_definition=None,
        )

    @staticmethod
    def _handle_parameter_error(
        ex: Union[ParameterValidationError, CastError],
    ) -> SchemaValidationError:
        if type(ex) == CastError:
            validation_message = f"Parameter '{ex.value}' is not of type: '{ex.type}'"
            return SchemaValidationError(
                message=validation_message, validation_message=validation_message + "."
            )
        name = f"parameters[{ex.name}]"  # type: ignore

        validation_message = (
            f"'{ex.name}' is a required '{ex.location}' parameter"  # type: ignore
        )

        return SchemaValidationError(
            message=validation_message,
            validation_message=validation_message + ".",
            name=name,
            path=name.replace("[", "").replace("]", "").split("."),
            value=None,
            definition=None,
            rule=ex.location,  # type: ignore
            rule_definition=None,
        )

    @staticmethod
    def _handle_body_error(
        ex: Union[InvalidSchemaValue, MissingRequiredRequestBody], request: Request
    ) -> SchemaValidationError:
        if type(ex) == MissingRequiredRequestBody:
            return SchemaValidationError(
                message="Missing required 'requestBody'",
                validation_message="Missing required 'requestBody'.",
            )
        error = None
        try:
            error = ex.schema_errors[0]  # type: ignore
        except IndexError:
            raise ValueError("Error has no Schema Error! Can't process errors")

        try:
            prop = error.absolute_path[0]
        except IndexError:
            prop = ""

        name = f"requestBody.content.{request.mimetype}.schema.properties[{prop}]"
        path = name.replace("[", ".").replace("]", "").split(".")

        return SchemaValidationError(
            message=error.message,
            validation_message=error.message + ".",
            name=name,
            path=path,
            value=error.instance,
            definition=None,
            rule=error.validator_value,
            rule_definition=error.validator,
        )
