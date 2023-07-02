from openapi_core import V30RequestValidator, V31RequestValidator
from openapi_core.unmarshalling.request.unmarshallers import BaseRequestUnmarshaller
from openapi_core.unmarshalling.schemas import (
    oas30_write_schema_unmarshallers_factory,
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.unmarshallers import BaseUnmarshaller
from openapi_core.validation.request.validators import APICallRequestValidator

from powertools_oas_validator.overrides.validators import CustomBaseRequestValidator


class CustomBaseRequestUnmarshaller(
    BaseRequestUnmarshaller, CustomBaseRequestValidator, BaseUnmarshaller
):
    ...


class BaseAPICallRequestUnmarshaller(CustomBaseRequestUnmarshaller):
    pass


class APICallRequestUnmarshaller(
    APICallRequestValidator, BaseAPICallRequestUnmarshaller
):
    ...


#
class V30RequestUnmarshaller(V30RequestValidator, APICallRequestUnmarshaller):
    schema_unmarshallers_factory = oas30_write_schema_unmarshallers_factory


class V31RequestUnmarshaller(V31RequestValidator, APICallRequestUnmarshaller):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
