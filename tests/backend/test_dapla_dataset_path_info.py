import datetime

import pytest

from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dapla_dataset_path_info import SupportedDateFormats
from datadoc.backend.dapla_dataset_path_info import categorize_period_string


# utanningsnivaa_p2022-10-01_v1.parquet - status this date
# grensehandel_imputert_p2022-10_p2022-12_v1.parquet - for 3 months
# omsetning_p2020W15_v1.parquet - for one week
@pytest.fixture(
    params=[
        {
            "dataset_path": "grensehandel_imputert_p2022-B1_v1.parquet",
            "expected_contains_data_from": datetime.date(2022, 1, 1),
            "expected_contains_data_until": datetime.date(2022, 2, 28),
            "expected_date_format": SupportedDateFormats.SSB_YEAR_BIMESTER,
        },
        {
            "dataset_path": "grensehandel_imputert_p2022-B1_p2022-B2_v1.parquet",
            "expected_contains_data_from": datetime.date(2022, 1, 1),
            "expected_contains_data_until": datetime.date(2022, 4, 30),
            "expected_date_format": SupportedDateFormats.SSB_YEAR_BIMESTER,
        },
        {
            "dataset_path": "grensehandel_imputert_p2022-10-01_p2022-12-31_v1.parquet",
            "expected_contains_data_from": datetime.date(2022, 10, 1),
            "expected_contains_data_until": datetime.date(2022, 12, 31),
            "expected_date_format": SupportedDateFormats.ISO_YEAR_MONTH_DAY,
        },
        {
            "dataset_path": "grensehandel_imputert_p2022-10_p2022-12_v1.parquet",
            "expected_contains_data_from": datetime.date(2022, 10, 1),
            "expected_contains_data_until": datetime.date(2022, 12, 31),
            "expected_date_format": SupportedDateFormats.ISO_YEAR_MONTH,
        },
        {
            "dataset_path": "flygende_objekter_p2019_v1.parquet",
            "expected_contains_data_from": datetime.date(2019, 1, 1),
            "expected_contains_data_until": datetime.date(2019, 12, 31),
            "expected_date_format": SupportedDateFormats.ISO_YEAR,
        },
        {
            "dataset_path": "framskrevne-befolkningsendringer_p2019_p2050_v1.parquet",
            "expected_contains_data_from": datetime.date(2019, 1, 1),
            "expected_contains_data_until": datetime.date(2050, 12, 31),
            "expected_date_format": SupportedDateFormats.ISO_YEAR,
        },
        {
            "dataset_path": "ufo_observasjoner_p2019_p2020_v1.parquet",
            "expected_contains_data_from": datetime.date(2019, 1, 1),
            "expected_contains_data_until": datetime.date(2020, 12, 31),
            "expected_date_format": SupportedDateFormats.ISO_YEAR,
        },
    ],
)
def test_data(request) -> DaplaDatasetPathInfo:
    return request.param


@pytest.fixture()
def dataset_path(test_data: dict[str, object]) -> DaplaDatasetPathInfo:
    return DaplaDatasetPathInfo(test_data["dataset_path"])


@pytest.fixture()
def expected_contains_data_from(test_data: dict[str, object]) -> datetime.date:
    return test_data["expected_contains_data_from"]


@pytest.fixture()
def expected_contains_data_until(test_data: dict[str, object]) -> datetime.date:
    return test_data["expected_contains_data_until"]


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
    "period,expected",
    [
        ("2022", SupportedDateFormats.ISO_YEAR),
        ("2022-10", SupportedDateFormats.ISO_YEAR_MONTH),
        ("2022-10-10", SupportedDateFormats.ISO_YEAR_MONTH_DAY),
        ("2022-H1", SupportedDateFormats.SSB_YEAR_SEMESTER),
        ("DEFAULT_ON_FAIL", SupportedDateFormats.UNKNOWN)
    ],
)
def test_categorize_period_string(period: str, expected: SupportedDateFormats):
    assert expected == categorize_period_string(period)

