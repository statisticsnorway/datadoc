"""Shared fixtures and configuration."""

import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import pytest
from datadoc_model.Enums import SupportedLanguages
from pytest_mock import MockerFixture

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.storage_adapter import StorageAdapter

from .utils import (
    TEST_BUCKET_PARQUET_FILEPATH,
    TEST_EXISTING_METADATA_DIRECTORY,
    TEST_EXISTING_METADATA_FILE_NAME,
    TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY,
    TEST_PARQUET_FILEPATH,
    TEST_RESOURCES_DIRECTORY,
    TEST_RESOURCES_METADATA_DOCUMENT,
)


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
def remove_document_file() -> None:
    yield None  # Dummy value, No need to return anything in particular here
    full_path = TEST_RESOURCES_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
    try:
        full_path.unlink()
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
    state.metadata = None
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL


@pytest.fixture()
def mock_gcsfs_open(mocker: MockerFixture):
    return mocker.patch("gcsfs.GCSFileSystem.open")


@pytest.fixture()
def mock_gcsfs_exists(mocker: MockerFixture):
    mock = mocker.patch("gcsfs.GCSFileSystem.exists")
    mock.return_value = True
    return mock


@pytest.fixture()
def mock_pathlib_write_text(mocker: MockerFixture):
    return mocker.patch("pathlib.Path.write_text")


@pytest.fixture()
def local_parquet_file(mock_pathlib_write_text: mock.patch):  # noqa: ARG001
    return StorageAdapter.for_path(str(TEST_PARQUET_FILEPATH))


@pytest.fixture()
def bucket_object_parquet_file(
    mock_gcsfs_open: mock.patch,  # noqa: ARG001
    mock_gcsfs_exists: mock.patch,  # noqa: ARG001
):
    return StorageAdapter.for_path(TEST_BUCKET_PARQUET_FILEPATH)
