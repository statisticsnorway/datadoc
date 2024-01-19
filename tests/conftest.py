"""Shared fixtures and configuration."""

import shutil
import traceback
from collections.abc import Generator
from datetime import datetime
from datetime import timezone
from pathlib import Path
from unittest import mock

import pytest
from datadoc_model import model
from pytest_mock import MockerFixture

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.storage_adapter import StorageAdapter
from datadoc.enums import SupportedLanguages

from .utils import TEST_BUCKET_PARQUET_FILEPATH
from .utils import TEST_EXISTING_METADATA_DIRECTORY
from .utils import TEST_EXISTING_METADATA_FILE_NAME
from .utils import TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY
from .utils import TEST_PARQUET_FILEPATH
from .utils import TEST_RESOURCES_METADATA_DOCUMENT


@pytest.fixture()
def dummy_timestamp() -> datetime:
    return datetime(2022, 1, 1, tzinfo=timezone.utc)


@pytest.fixture()
def _mock_timestamp(mocker: MockerFixture, dummy_timestamp: datetime) -> None:
    mocker.patch(
        "datadoc.backend.datadoc_metadata.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture()
def metadata(_mock_timestamp: None) -> DataDocMetadata:
    return DataDocMetadata(str(TEST_PARQUET_FILEPATH))


@pytest.fixture()
def remove_document_file() -> Generator[None, None, None]:
    # Yield so we only run teardown
    yield None
    try:
        TEST_RESOURCES_METADATA_DOCUMENT.unlink()
    except FileNotFoundError as e:
        print("File not deleted on teardown, exception caught:")  # noqa: T201
        traceback.print_exception(type(e), e)


@pytest.fixture()
def existing_metadata_path() -> Path:
    return TEST_EXISTING_METADATA_DIRECTORY


@pytest.fixture()
def existing_metadata_file(existing_metadata_path: Path) -> str:
    # Setup by copying the file into the relevant directory
    shutil.copy(
        existing_metadata_path / TEST_EXISTING_METADATA_FILE_NAME,
        TEST_RESOURCES_METADATA_DOCUMENT,
    )
    return str(TEST_RESOURCES_METADATA_DOCUMENT)


@pytest.fixture()
@pytest.mark.parametrize(
    "existing_metadata_file",
    [TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY],
)
def existing_metadata_with_valid_id_file(existing_metadata_file: Path) -> Path:
    return existing_metadata_file


@pytest.fixture()
def _clear_state() -> None:
    """Global fixture, referred to in pytest.ini."""
    state.metadata = None  # type: ignore [assignment]
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL


@pytest.fixture()
def mock_gcsfs_open(mocker: MockerFixture) -> mock.Mock:
    return mocker.patch("gcsfs.GCSFileSystem.open")


@pytest.fixture()
def mock_gcsfs_exists(mocker: MockerFixture) -> mock.Mock:
    mock = mocker.patch("gcsfs.GCSFileSystem.exists")
    mock.return_value = True
    return mock


@pytest.fixture()
def mock_pathlib_write_text(mocker: MockerFixture) -> mock.Mock:
    return mocker.patch("pathlib.Path.write_text")


@pytest.fixture()
def local_parquet_file(
    mock_pathlib_write_text: mock.Mock,  # noqa: ARG001
) -> StorageAdapter:
    return StorageAdapter.for_path(str(TEST_PARQUET_FILEPATH))


@pytest.fixture()
def bucket_object_parquet_file(
    mock_gcsfs_open: mock.Mock,  # noqa: ARG001
    mock_gcsfs_exists: mock.Mock,  # noqa: ARG001
) -> StorageAdapter:
    return StorageAdapter.for_path(TEST_BUCKET_PARQUET_FILEPATH)


ENGLISH_NAME = "English Name"
BOKMÅL_NAME = "Bokmål Name"
NYNORSK_NAME = "Nynorsk Name"


@pytest.fixture()
def english_name() -> str:
    return "English Name"


@pytest.fixture()
def bokmål_name() -> str:
    return "Bokmål navn"


@pytest.fixture()
def nynorsk_name() -> str:
    return "Nynorsk namn"


@pytest.fixture()
def language_object(english_name: str, bokmål_name: str) -> model.LanguageStringType:
    return model.LanguageStringType(en=english_name, nb=bokmål_name)
