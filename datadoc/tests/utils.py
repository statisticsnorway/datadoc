"""Utility values and functions for tests."""

from pathlib import Path

TEST_BUCKET_PARQUET_FILEPATH = "gs://ssb-staging-dapla-felles-data-delt/datadoc/klargjorte_data/person_data_v1.parquet"

TEST_RESOURCES_DIRECTORY = Path("datadoc/tests/resources/")

TEST_PARQUET_FILEPATH = TEST_RESOURCES_DIRECTORY / "person_data_v1.parquet"
TEST_SAS7BDAT_FILEPATH = TEST_RESOURCES_DIRECTORY / "sasdata.sas7bdat"
TEST_PARQUET_GZIP_FILEPATH = TEST_RESOURCES_DIRECTORY / "person_data_v1.parquet.gzip"

TEST_EXISTING_METADATA_DIRECTORY = TEST_RESOURCES_DIRECTORY / "existing_metadata_file"
TEST_EXISTING_METADATA_FILE_NAME = "person_data_v1__DOC.json"
TEST_EXISTING_METADATA_FILEPATH = (
    TEST_EXISTING_METADATA_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
)
TEST_RESOURCES_METADATA_DOCUMENT = (
    TEST_RESOURCES_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
)

TEST_EXISTING_METADATA_WITH_VALID_ID_DIRECTORY = (
    TEST_EXISTING_METADATA_DIRECTORY / "valid_id_field"
)

TEST_COMPATIBILITY_DIRECTORY = TEST_EXISTING_METADATA_DIRECTORY / "compatibility"
