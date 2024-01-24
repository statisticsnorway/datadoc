import datetime

from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo


def test_exctract_period_info_date_from():
    file_name = "ufo_observasjoner_p2019_p2020_v1.parquet"
    dapla_dataset = DaplaDatasetPathInfo(file_name)
    assert dapla_dataset.contains_data_from() == datetime.date(2019, 1, 1)
