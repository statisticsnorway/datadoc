import pathlib

import pytest

from datadoc.tests.storage_adapter_fixtures import *  # noqa pytest magic
from datadoc.tests.utils import TEST_BUCKET_PARQUET_FILEPATH, TEST_PARQUET_FILEPATH

from ..backend.StorageAdapter import GCSObject, LocalFile, StorageAdapter


@pytest.mark.parametrize(
    ("file", "expected_class"),
    [("local_parquet_file", LocalFile), ("bucket_object_parquet_file", GCSObject)],
)
def test_factory(file: StorageAdapter, expected_class, request):
    # Ugly pytest magic to get the actual fixture out
    file = request.getfixturevalue(file)
    assert isinstance(file, expected_class)


@pytest.mark.parametrize("file", ["local_parquet_file", "bucket_object_parquet_file"])
def test_open(file: StorageAdapter, request):
    # Ugly pytest magic to get the actual fixture out
    file = request.getfixturevalue(file)
    with file.open() as file_handle:
        assert file_handle.readable()


@pytest.mark.parametrize(
    ("file", "expected_parent"),
    [
        (
            "local_parquet_file",
            str(pathlib.Path(TEST_PARQUET_FILEPATH).parent.absolute()),
        ),
        (
            "bucket_object_parquet_file",
            "/".join(TEST_BUCKET_PARQUET_FILEPATH.split("/")[:-1]),
        ),
    ],
)
def test_parent(file: StorageAdapter, expected_parent: str, request):
    # Ugly pytest magic to get the actual fixture out
    file = request.getfixturevalue(file)
    assert file.parent() == expected_parent


@pytest.mark.parametrize(
    ("file", "expected"),
    [
        (
            "local_parquet_file",
            "/".join([TEST_PARQUET_FILEPATH, "extra"]),
        ),
        (
            "bucket_object_parquet_file",
            "/".join([TEST_BUCKET_PARQUET_FILEPATH, "extra"]),
        ),
    ],
)
def test_joinpath(file: StorageAdapter, expected: str, request):
    # Ugly pytest magic to get the actual fixture out
    file = request.getfixturevalue(file)
    file.joinpath("extra")
    assert file.location == expected


@pytest.mark.parametrize("file", ["local_parquet_file", "bucket_object_parquet_file"])
def test_exists(file: StorageAdapter, request):
    # Ugly pytest magic to get the actual fixture out
    file = request.getfixturevalue(file)
    assert file.exists()


def test_write_text_local_file(local_parquet_file: StorageAdapter, request):
    local_parquet_file.write_text("12345")
    mock = request.getfixturevalue("mock_pathlib_write_text")
    mock.assert_called_once_with("12345", encoding="utf-8")


# Currently no test for writing to GCS
# Attempts to mock are failing with TypeError: cannot set 'write' attribute of immutable type '_io.BufferedWriter'
