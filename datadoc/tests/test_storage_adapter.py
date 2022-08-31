import pytest

from datadoc.tests.utils import TEST_BUCKET_PARQUET_FILEPATH, TEST_PARQUET_FILEPATH

from ..backend.StorageAdapter import GCSObject, LocalFile, StorageAdapter


@pytest.fixture
def local_parquet_file():
    return StorageAdapter.for_path(TEST_PARQUET_FILEPATH)


@pytest.fixture
def bucket_object_parquet_file():
    return StorageAdapter.for_path(TEST_BUCKET_PARQUET_FILEPATH)


def test_local_file():
    assert isinstance(StorageAdapter.for_path("local/file/path"), LocalFile)


def test_bucket_object():
    assert isinstance(StorageAdapter.for_path("gs://object/in/bucket"), GCSObject)


def test_open_local_file(local_parquet_file: StorageAdapter):
    with local_parquet_file.open() as file_handle:
        assert file_handle.readable()


def test_open_bucket_object(bucket_object_parquet_file: StorageAdapter):
    with bucket_object_parquet_file.open() as file_handle:
        assert file_handle.readable()
