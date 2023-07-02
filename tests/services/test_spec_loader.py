from unittest.mock import MagicMock, patch

import pytest

from powertools_oas_validator.exceptions import (
    FileNotExistsError,
    NotSupportedFileTypeError,
)
from powertools_oas_validator.services.spec_loader import SpecLoader


@patch("powertools_oas_validator.services.spec_loader.Spec")
@patch("powertools_oas_validator.services.spec_loader.os")
def test_read_from_file_name(os_mock: MagicMock, spec_mock: MagicMock) -> None:
    spec_mock.from_file_path = MagicMock()
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock(return_value=True)

    SpecLoader(".yaml").read_from_file_name()

    spec_mock.from_file_path.assert_called_once_with(".yaml")


@patch("powertools_oas_validator.services.spec_loader.os")
def test_validate_file_already_validated(os_mock: MagicMock) -> None:
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock()

    loader = SpecLoader("")
    loader.validated_cache = True

    loader.validate_file()

    os_mock.path.isfile.assert_not_called()


@patch("powertools_oas_validator.services.spec_loader.os")
def test_validate_file_not_exists(os_mock: MagicMock) -> None:
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock(return_value=False)

    with pytest.raises(FileNotExistsError):
        SpecLoader(".yaml").validate_file()


@patch("powertools_oas_validator.services.spec_loader.os")
def test_validate_file_not_supported(os_mock: MagicMock) -> None:
    os_mock.path = MagicMock()
    os_mock.path.isfile = MagicMock(return_value=True)

    with pytest.raises(NotSupportedFileTypeError):
        SpecLoader(".filenotsupported").validate_file()
