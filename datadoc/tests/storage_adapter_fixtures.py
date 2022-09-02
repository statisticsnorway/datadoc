import pytest

from datadoc.tests.utils import TEST_BUCKET_PARQUET_FILEPATH, TEST_PARQUET_FILEPATH

from ..backend.StorageAdapter import StorageAdapter


@pytest.fixture()
def mock_gcsfs_open(mocker):
    mock = mocker.patch("gcsfs.GCSFileSystem.open")
    return mock


@pytest.fixture()
def mock_gcsfs_exists(mocker):
    mock = mocker.patch("gcsfs.GCSFileSystem.exists")
    mock.return_value = True
    return mock


@pytest.fixture()
def mock_pathlib_write_text(mocker):
    mock = mocker.patch("pathlib.Path.write_text")
    return mock


@pytest.fixture
def local_parquet_file(mock_pathlib_write_text):
    return StorageAdapter.for_path(TEST_PARQUET_FILEPATH)


@pytest.fixture
def bucket_object_parquet_file(mock_gcsfs_open, mock_gcsfs_exists):
    return StorageAdapter.for_path(TEST_BUCKET_PARQUET_FILEPATH)
