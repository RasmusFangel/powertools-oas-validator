import os
from typing import Protocol

from openapi_core import Spec

from powertools_oas_validator.exceptions import (
    FileNotExistsError,
    NotSupportedFileTypeError,
)


class SpecLoaderProtocol(Protocol):
    def read_from_file_name(self) -> Spec:
        raise NotImplementedError  # pragma: nocover


class SpecLoader:
    oas_path: str
    validated_cache: bool = False

    def __init__(self, oas_path: str) -> None:
        self.oas_path = oas_path

    def read_from_file_name(self) -> Spec:
        if not self.validated_cache:
            self.validate_file()

        return Spec.from_file_path(self.oas_path)

    def validate_file(self) -> None:
        if self.validated_cache:
            return

        if not os.path.isfile(self.oas_path):
            raise FileNotExistsError(f"File does not exist on path: '{self.oas_path}'")

        extension = self.oas_path.split(".")[-1]

        if extension not in ["yaml", "json"]:
            raise NotSupportedFileTypeError(
                f"'.{extension} not supported. Only '.json' and '.yaml'"
            )

        self.validated_cache = True
