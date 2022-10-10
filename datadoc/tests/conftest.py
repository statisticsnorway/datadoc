import shutil
from datetime import datetime

import pytest
from datadoc_model.Enums import SupportedLanguages

from datadoc import state

from ..backend.DataDocMetadata import DataDocMetadata
from ..backend.StorageAdapter import StorageAdapter
from .utils import (
    TEST_BUCKET_PARQUET_FILEPATH,
    TEST_EXISTING_METADATA_DIRECTORY,
    TEST_EXISTING_METADATA_FILE_NAME,
    TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY,
    TEST_PARQUET_FILEPATH,
    TEST_RESOURCES_DIRECTORY,
    TEST_RESOURCES_METADATA_DOCUMENT,
)


@pytest.fixture
def dummy_timestamp():
    return datetime(2022, 1, 1)


@pytest.fixture
def mock_timestamp(mocker, dummy_timestamp):
    mocker.patch(
        "datadoc.backend.DataDocMetadata.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture
def metadata(mock_timestamp):
    yield DataDocMetadata(str(TEST_PARQUET_FILEPATH))


@pytest.fixture
def remove_document_file() -> None:
    yield None  # Dummy value, No need to return anything in particular here
    full_path = TEST_RESOURCES_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
    full_path.unlink()


@pytest.fixture
def existing_metadata_path():
    return TEST_EXISTING_METADATA_DIRECTORY


@pytest.fixture
def existing_metadata_file(existing_metadata_path) -> str:
    # Setup by copying the file into the relevant directory
    shutil.copy(
        existing_metadata_path / TEST_EXISTING_METADATA_FILE_NAME,
        TEST_RESOURCES_METADATA_DOCUMENT,
    )
    return str(TEST_RESOURCES_METADATA_DOCUMENT)


@pytest.fixture
@pytest.mark.parametrize(
    "existing_metadata_path", [TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY]
)
def existing_metadata_with_valid_id_file(existing_metadata_file) -> str:
    return existing_metadata_file


@pytest.fixture
def clear_state():
    state.metadata = None
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL


@pytest.fixture
def mock_gcsfs_open(mocker):
    mock = mocker.patch("gcsfs.GCSFileSystem.open")
    return mock


@pytest.fixture
def mock_gcsfs_exists(mocker):
    mock = mocker.patch("gcsfs.GCSFileSystem.exists")
    mock.return_value = True
    return mock


@pytest.fixture
def mock_pathlib_write_text(mocker):
    mock = mocker.patch("pathlib.Path.write_text")
    return mock


@pytest.fixture
def local_parquet_file(mock_pathlib_write_text):
    return StorageAdapter.for_path(str(TEST_PARQUET_FILEPATH))


@pytest.fixture
def bucket_object_parquet_file(mock_gcsfs_open, mock_gcsfs_exists):
    return StorageAdapter.for_path(TEST_BUCKET_PARQUET_FILEPATH)
