import datetime
from dataclasses import dataclass

import pytest

from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo


@dataclass
class DatasetPathTestCase:
    """Structure to define attributes needed for a test case."""

    path: str
    expected_contains_data_from: datetime.date
    expected_contains_data_until: datetime.date


TEST_CASES = [
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10-01_p2022-12-31_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10_p2022-12_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="flygende_objekter_p2019_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2019, 12, 31),
    ),
    DatasetPathTestCase(
        path="framskrevne-befolkningsendringer_p2019_p2050_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2050, 12, 31),
    ),
    DatasetPathTestCase(
        path="ufo_observasjoner_p2019_p2020_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2020, 12, 31),
    ),
]


@pytest.fixture(
    ids=[tc.path for tc in TEST_CASES],
    params=TEST_CASES,
)
def test_data(request: pytest.FixtureRequest) -> DatasetPathTestCase:
    return request.param


@pytest.fixture()
def dataset_path(test_data: DatasetPathTestCase) -> DaplaDatasetPathInfo:
    return DaplaDatasetPathInfo(test_data.path)


@pytest.fixture()
def expected_contains_data_from(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_from


@pytest.fixture()
def expected_contains_data_until(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_until


def test_extract_period_info_date_from(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_from: datetime.date,
):
    assert dataset_path.contains_data_from == expected_contains_data_from


def test_extract_period_info_date_until(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_until: datetime.date,
):
    assert dataset_path.contains_data_until == expected_contains_data_until
