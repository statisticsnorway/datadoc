import os

TEST_BUCKET_PARQUET_FILEPATH = "gs://ssb-staging-dapla-felles-data-delt/datadoc/klargjorte_data/person_data_v1.parquet"

TEST_RESOURCES_DIRECTORY = "datadoc/tests/resources/"

TEST_PARQUET_FILEPATH = os.path.join(TEST_RESOURCES_DIRECTORY, "person_data_v1.parquet")
TEST_SAS7BDAT_FILEPATH = os.path.join(TEST_RESOURCES_DIRECTORY, "sasdata.sas7bdat")

TEST_EXISTING_METADATA_FILE_NAME = "person_data_v1__DOC.json"
TEST_EXISTING_METADATA_FILEPATH = os.path.join(
    TEST_RESOURCES_DIRECTORY, "existing_metadata_file", TEST_EXISTING_METADATA_FILE_NAME
)

TEST_EXISTING_METADATA_FILE_WITH_VALID_ID_NAME = (
    "person_data_with_id_field_v1__DOC.json"
)
TEST_EXISTING_METADATA_WITH_VALID_ID_FILEPATH = os.path.join(
    TEST_RESOURCES_DIRECTORY,
    "existing_metadata_file",
    TEST_EXISTING_METADATA_FILE_WITH_VALID_ID_NAME,
)
