import datetime
from dataclasses import dataclass

import pytest

from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dapla_dataset_path_info import SupportedDateFormats
from datadoc.backend.dapla_dataset_path_info import categorize_period_string


@dataclass
class DatasetPathTestCase:
    """Structure to define attributes needed for a test case."""

    path: str
    expected_contains_data_from: datetime.date
    expected_contains_data_until: datetime.date
    expected_date_format: SupportedDateFormats


TEST_CASES = [
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-B1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 2, 28),
        expected_date_format=SupportedDateFormats.SSB_YEAR_BIMESTER,
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-B1_p2022-B2_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 4, 30),
        expected_date_format=SupportedDateFormats.SSB_YEAR_BIMESTER,
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10-01_p2022-12-31_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
        expected_date_format=SupportedDateFormats.ISO_YEAR_MONTH_DAY,
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10_p2022-12_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
        expected_date_format=SupportedDateFormats.ISO_YEAR_MONTH,
    ),
    DatasetPathTestCase(
        path="flygende_objekter_p2019_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2019, 12, 31),
        expected_date_format=SupportedDateFormats.ISO_YEAR,
    ),
    DatasetPathTestCase(
        path="framskrevne-befolkningsendringer_p2019_p2050_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2050, 12, 31),
        expected_date_format=SupportedDateFormats.ISO_YEAR,
    ),
    DatasetPathTestCase(
        path="ufo_observasjoner_p2019_p2020_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2020, 12, 31),
        expected_date_format=SupportedDateFormats.ISO_YEAR,
    ),
]


@pytest.fixture(
    ids=[f"{tc.expected_date_format.name}-{tc.path}" for tc in TEST_CASES],
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


""" def test_extract_period_info_date_until(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_until: datetime.date,
):
    assert dataset_path.contains_data_until == expected_contains_data_until
 """


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        ("2022", SupportedDateFormats.ISO_YEAR),
        ("2022-10", SupportedDateFormats.ISO_YEAR_MONTH),
        ("2022-10-10", SupportedDateFormats.ISO_YEAR_MONTH_DAY),
        ("2022-H1", SupportedDateFormats.SSB_YEAR_SEMESTER),
        ("DEFAULT_ON_FAIL", SupportedDateFormats.UNKNOWN),
    ],
)
def test_categorize_period_string(period: str, expected: SupportedDateFormats):
    assert expected == categorize_period_string(period)
