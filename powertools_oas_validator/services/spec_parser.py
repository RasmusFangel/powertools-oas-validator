from openapi_core import Spec

from powertools_oas_validator.types import OpenAPIVersion


class SpecParser:
    @staticmethod
    def get_openapi_version(spec: Spec) -> OpenAPIVersion:
        openapi_version = spec.accessor.lookup["openapi"]  # type: ignore

        openapi_version = openapi_version.split(".")

        return OpenAPIVersion(
            openapi_version[0], openapi_version[1], openapi_version[2]
        )
