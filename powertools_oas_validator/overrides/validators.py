from typing import Any, Optional

from openapi_core import Spec
from openapi_core.datatypes import RequestParameters
from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.decorators import ValidationErrorWrapper
from openapi_core.validation.request.validators import BaseRequestValidator, Dict


class CustomBaseRequestValidator(BaseRequestValidator):
    class CustomValidationErrorWrapper(ValidationErrorWrapper):
        ...

    @CustomValidationErrorWrapper(OpenAPIError)
    def _get_body(self, body: Optional[str], mimetype: str, operation: Spec) -> Any:
        return super()._get_body.__wrapped__(  # type: ignore
            self, body=body, mimetype=mimetype, operation=operation
        )

    @CustomValidationErrorWrapper(OpenAPIError)
    def _get_parameter(
        self, parameters: RequestParameters, param: Spec
    ) -> Optional[Dict[str, str]]:
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
