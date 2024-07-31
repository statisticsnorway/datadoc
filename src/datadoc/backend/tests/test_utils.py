import os
import pathlib

import pytest
from cloudpathlib.local import LocalGSClient
from cloudpathlib.local import LocalGSPath

from datadoc.backend.src.utils import calculate_percentage
from datadoc.backend.src.utils import normalize_path
from datadoc.backend.tests.constants import DATADOC_METADATA_MODULE_UTILS
from datadoc.backend.tests.constants import TEST_BUCKET_PARQUET_FILEPATH
from datadoc.backend.tests.constants import TEST_PARQUET_FILEPATH


@pytest.mark.parametrize(
    ("dataset_path", "expected_type"),
    [
        (TEST_BUCKET_PARQUET_FILEPATH, LocalGSPath),
        (str(TEST_PARQUET_FILEPATH), pathlib.Path),
    ],
)
def test_normalize_path(
    dataset_path: str,
    expected_type: type[os.PathLike],
    mocker,
):
    mocker.patch(f"{DATADOC_METADATA_MODULE_UTILS}.AuthClient", autospec=True)
    mocker.patch(f"{DATADOC_METADATA_MODULE_UTILS}.GSClient", LocalGSClient)
    mocker.patch(
        f"{DATADOC_METADATA_MODULE_UTILS}.GSPath",
        LocalGSPath,
    )
    file = normalize_path(  # for testing purposes
        dataset_path,
    )
    assert isinstance(file, expected_type)


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33  # noqa: PLR2004
