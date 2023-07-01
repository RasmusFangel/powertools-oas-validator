from typing import Dict
from unittest.mock import MagicMock, patch

import pytest

from powertools_oas_validator.exceptions import (
    FileNotExistsError,
    NotSupportedFileTypeError,
)
from powertools_oas_validator.services.spec_loader import SpecLoader
from powertools_oas_validator.types import LoadedSpec


@pytest.mark.parametrize("file_path", ["test.yaml", "test.json"])
@patch("powertools_oas_validator.services.spec_loader.read_from_filename")
@patch("powertools_oas_validator.services.spec_loader.os")
def test_spec_loader_on_success(
    os_mock: MagicMock, read_mock: MagicMock, file_path: str
):
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock(return_value=True)

    spec_dict: Dict = {}
    spec_url = "test"

    read_mock.return_value = (spec_dict, spec_url)

    loaded_spec = SpecLoader().read_from_file_name(file_path)

    assert type(loaded_spec) == LoadedSpec
    assert loaded_spec.spec_dict == spec_dict
    assert loaded_spec.spec_url == spec_url

    os_mock.path.isfile.assert_called_once_with(file_path)


@pytest.mark.parametrize(
    "file_path, file_exists, ex",
    [(".yaml", False, FileNotExistsError), (".txt", True, NotSupportedFileTypeError)],
)
@patch("powertools_oas_validator.services.spec_loader.os")
def test_spec_loader_on_file_error(
    os_mock: MagicMock, file_path: str, file_exists: bool, ex: Exception
):
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock(return_value=file_exists)

    with pytest.raises(ex):  # type: ignore
        SpecLoader().read_from_file_name(file_path)

    os_mock.path.isfile.assert_called_once_with(file_path)
