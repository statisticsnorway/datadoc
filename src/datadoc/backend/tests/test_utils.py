import datetime
import os
import pathlib

import pytest
from cloudpathlib.local import LocalGSClient
from cloudpathlib.local import LocalGSPath

from datadoc.backend.src.utility.utils import calculate_percentage
from datadoc.backend.src.utility.utils import incorrect_date_order
from datadoc.backend.src.utility.utils import normalize_path
from datadoc.backend.tests.utility.constants import DATADOC_METADATA_MODULE_UTILS
from datadoc.backend.tests.utility.constants import TEST_BUCKET_PARQUET_FILEPATH
from datadoc.backend.tests.utility.constants import TEST_PARQUET_FILEPATH


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


@pytest.mark.parametrize(
    ("date_from", "date_until", "expected"),
    [
        (datetime.date(2024, 1, 1), datetime.date(1960, 1, 1), True),
        (datetime.date(1980, 1, 1), datetime.date(2000, 6, 5), False),
        (None, None, False),
        (datetime.date(2024, 1, 1), None, False),
        (None, datetime.date(2024, 1, 1), True),
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 1), False),
    ],
)
def test_incorrect_date_order(date_from, date_until, expected):
    result = incorrect_date_order(date_from, date_until)
    assert result == expected
