"""Test methods in utils.py."""

import os
import pathlib

import pytest
from cloudpathlib.local import LocalGSClient
from cloudpathlib.local import LocalGSPath

from datadoc.backend.tests.utils import TEST_BUCKET_PARQUET_FILEPATH
from datadoc.backend.tests.utils import TEST_PARQUET_FILEPATH
from datadoc.backend.utils import calculate_percentage
from datadoc.backend.utils import normalize_path

BACKEND_UTILS_MODULE = "datadoc.backend.utils"


@pytest.mark.parametrize(
    ("dataset_path", "expected_type"),
    [
        (TEST_BUCKET_PARQUET_FILEPATH, LocalGSPath),
        (str(TEST_PARQUET_FILEPATH), pathlib.Path),
    ],
)
def test_normalize_path(  # noqa: ANN201, D103
    dataset_path: str,
    expected_type: type[os.PathLike],
    mocker,  # noqa: ANN001
):
    mocker.patch(f"{BACKEND_UTILS_MODULE}.AuthClient", autospec=True)
    mocker.patch(f"{BACKEND_UTILS_MODULE}.GSClient", LocalGSClient)
    mocker.patch(
        f"{BACKEND_UTILS_MODULE}.GSPath",
        LocalGSPath,
    )
    file = normalize_path(  # for testing purposes
        dataset_path,
    )
    assert isinstance(file, expected_type)  # noqa: S101


def test_calculate_percentage():  # noqa: ANN201, D103
    assert calculate_percentage(1, 3) == 33  # noqa: PLR2004, S101
