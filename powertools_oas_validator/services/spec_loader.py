import os
from typing import Protocol

from openapi_spec_validator.readers import read_from_filename

from powertools_oas_validator.exceptions import (
    FileNotExistsError,
    NotSupportedFileTypeError,
)
from powertools_oas_validator.types import LoadedSpec


class SpecLoaderProtocol(Protocol):
    def read_from_file_name(self, file_path: str) -> LoadedSpec:
        raise NotImplementedError  # pragma: nocover


class SpecLoader:
    validated_cache: bool = False

    def read_from_file_name(self, file_path: str) -> LoadedSpec:
        self.validate_file(file_path)

        spec_dict, spec_url = read_from_filename(file_path)

        return LoadedSpec(spec_dict=spec_dict, spec_url=spec_url)

    def validate_file(self, file_path: str) -> None:
        if self.validated_cache:
            return

        if not os.path.isfile(file_path):
            raise FileNotExistsError(f"File does not exist on path: {file_path}")

        extension = file_path.split(".")[-1]

        if extension not in ["yaml", "json"]:
            raise NotSupportedFileTypeError(
                f"'.{extension} not supported. Only '.json' and '.yaml'"
            )

        self.validated_cache = True
