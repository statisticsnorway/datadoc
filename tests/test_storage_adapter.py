"""Tests for the StorageAdapter class."""

import pathlib

import pytest

from datadoc.backend.storage_adapter import GCSObject
from datadoc.backend.storage_adapter import LocalFile
from datadoc.backend.storage_adapter import StorageAdapter
from tests.utils import TEST_BUCKET_PARQUET_FILEPATH
from tests.utils import TEST_PARQUET_FILEPATH


@pytest.mark.parametrize(
    ("file_name", "expected_class"),
    [("local_parquet_file", LocalFile), ("bucket_object_parquet_file", GCSObject)],
)
def test_factory(
    file_name: str,
    expected_class: type[StorageAdapter],
    request: pytest.FixtureRequest,
):
    # Ugly pytest magic to get the actual fixture out
    file: StorageAdapter = request.getfixturevalue(file_name)
    assert isinstance(file, expected_class)


@pytest.mark.parametrize(
    "file_name",
    ["local_parquet_file", "bucket_object_parquet_file"],
)
def test_open(file_name: str, request: pytest.FixtureRequest):
    # Ugly pytest magic to get the actual fixture out
    file: StorageAdapter = request.getfixturevalue(file_name)
    with file.open() as file_handle:
        assert file_handle.readable()


@pytest.mark.parametrize(
    ("file_name", "expected_parent"),
    [
        (
            "local_parquet_file",
            str(TEST_PARQUET_FILEPATH.parent.absolute()),
        ),
        (
            "bucket_object_parquet_file",
            "/".join(TEST_BUCKET_PARQUET_FILEPATH.split("/")[:-1]),
        ),
    ],
)
def test_parent(file_name: str, expected_parent: str, request: pytest.FixtureRequest):
    # Ugly pytest magic to get the actual fixture out
    file: StorageAdapter = request.getfixturevalue(file_name)
    assert file.parent() == expected_parent


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        (
            "local_parquet_file",
            f"{TEST_PARQUET_FILEPATH}/extra",
        ),
        (
            "bucket_object_parquet_file",
            f"{TEST_BUCKET_PARQUET_FILEPATH}/extra",
        ),
    ],
)
def test_joinpath(
    file_name: str,
    expected: str,
    request: pytest.FixtureRequest,
):
    # Ugly pytest magic to get the actual fixture out
    actual_file: StorageAdapter = request.getfixturevalue(file_name)
    actual_file.joinpath("extra")
    assert pathlib.Path(actual_file.location) == pathlib.Path(expected)


@pytest.mark.parametrize(
    "file_name",
    ["local_parquet_file", "bucket_object_parquet_file"],
)
def test_exists(file_name: str, request: pytest.FixtureRequest):
    # Ugly pytest magic to get the actual fixture out
    actual_file: StorageAdapter = request.getfixturevalue(file_name)
    assert actual_file.exists()


def test_write_text_local_file(
    local_parquet_file: StorageAdapter,
    request: pytest.FixtureRequest,
):
    local_parquet_file.write_text("12345")
    mock = request.getfixturevalue("mock_pathlib_write_text")
    mock.assert_called_once_with("12345", encoding="utf-8")