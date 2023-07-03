from collections.abc import Callable
from typing import Any, Dict, Optional

from openapi_core import Spec
from openapi_core.datatypes import RequestParameters
from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.decorators import OpenAPIErrorType, ValidationErrorWrapper
from openapi_core.validation.request.validators import BaseRequestValidator


class CustomBaseRequestValidator(BaseRequestValidator):
    class CustomValidationErrorWrapper(ValidationErrorWrapper):
        def _raise_error(
            self,
            exc: OpenAPIError,
            cls: OpenAPIErrorType,
            f: Callable[..., Any],
            *args: Any,
            **kwds: Any
        ) -> None:
            raise exc from None

    @CustomValidationErrorWrapper(OpenAPIError)
    def _get_body(self, body: Optional[str], mimetype: str, operation: Spec) -> Any:
        super()._get_body.__wrapped__(  # type: ignore
            self, body=body, mimetype=mimetype, operation=operation
        )

    @CustomValidationErrorWrapper(OpenAPIError)
    def _get_parameter(self, parameters: RequestParameters, param: Spec) -> Any:
        return super()._get_parameter.__wrapped__(  # type: ignore
            self, parameters=parameters, param=param
        )

    @CustomValidationErrorWrapper(OpenAPIError)
    def _get_security(
        self, parameters: RequestParameters, operation: Spec
    ) -> Optional[Dict[str, str]]:
        return super()._get_security.__wrapped__(  # type: ignore
            self, parameters=parameters, operation=operation
        )
