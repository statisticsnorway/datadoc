from copy import copy
import os
from pathlib import PurePath
import shutil
import pytest
from datadoc_model import Enums

from datadoc_model.Enums import DatasetState
from datadoc import DataDocMetadata
from datadoc_model.Model import DataDocDataSet, DataDocVariable, MetadataDocument
from .utils import (
    TEST_EXISTING_METADATA_FILE_NAME,
    TEST_EXISTING_METADATA_FILEPATH,
    TEST_PARQUET_FILEPATH,
    TEST_RESOURCES_DIRECTORY,
)


@pytest.fixture
def make_paths():
    split_path = list(PurePath(TEST_PARQUET_FILEPATH).parts)
    initial_data = [
        ("kildedata", DatasetState.SOURCE_DATA),
        ("inndata", DatasetState.INPUT_DATA),
        ("klargjorte_data", DatasetState.PROCESSED_DATA),
        ("", None),
    ]
    test_data = []

    # Construct paths with each of the potential options in them
    for to_insert, state in initial_data:
        new_path = copy(split_path)
        new_path.insert(-2, to_insert)
        new_path = PurePath("").joinpath(*new_path)
        test_data.append((new_path, state))

    return test_data


def test_get_dataset_state(make_paths):
    metadata = DataDocMetadata.DataDocMetadata(TEST_PARQUET_FILEPATH)
    for path, expected_result in make_paths:
        actual_state = metadata.get_dataset_state(path)
        assert actual_state == expected_result


def test_get_dataset_state_no_parameter_supplied():
    metadata = DataDocMetadata.DataDocMetadata(TEST_PARQUET_FILEPATH)
    assert metadata.get_dataset_state() is None


@pytest.fixture
def existing_metadata_file():
    # Setup by copying the file into the relevant directory
    shutil.copy(TEST_EXISTING_METADATA_FILEPATH, TEST_RESOURCES_DIRECTORY)
    yield True  # Dummy value, No need to return anything in particular here
    # Cleanup by deleting the file once we're done
    os.remove(os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME))


def test_existing_metadata_file(existing_metadata_file):
    metadata = DataDocMetadata.DataDocMetadata(TEST_PARQUET_FILEPATH)
    assert metadata.meta.dataset.name.en == "successfully_read_existing_file"


def test_metadata_document_percent_complete():
    dataset = DataDocDataSet(dataset_state=Enums.DatasetState.OUTPUT_DATA)
    variable_1 = DataDocVariable(data_type=Enums.Datatype.BOOLEAN)
    variable_2 = DataDocVariable(data_type=Enums.Datatype.INTEGER)
    document = MetadataDocument(
        percentage_complete=0,
        document_version=1,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )
    metadata = DataDocMetadata.DataDocMetadata(TEST_PARQUET_FILEPATH)
    metadata.meta = document

    assert metadata.percent_complete == 11
