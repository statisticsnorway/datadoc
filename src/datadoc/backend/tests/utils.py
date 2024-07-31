"""Utility values and functions for tests."""

from pathlib import Path

TEST_BUCKET_PARQUET_FILEPATH = "gs://ssb-staging-dapla-felles-data-delt/datadoc/klargjorte_data/person_data_v1.parquet"

TEST_BUCKET_PARQUET_FILEPATH_WITH_SHORTNAME = "gs://ssb-staging-dapla-felles-data-delt/befolkning/klargjorte_data/person_data_v1.parquet"

TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH = "gs://ssb-my-team-data-produkt-prod/ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"

TEST_RESOURCES_DIRECTORY = Path("src/datadoc/backend/tests/resources")

TEST_DATASETS_DIRECTORY = TEST_RESOURCES_DIRECTORY / "datasets"

TEST_PARQUET_FILE_NAME = "person_data_v1.parquet"

TEST_PARQUET_FILEPATH = TEST_DATASETS_DIRECTORY / TEST_PARQUET_FILE_NAME
