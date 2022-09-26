import json
import os
import shutil
from copy import copy
from datetime import datetime
from pathlib import PurePath
from typing import List, Tuple
from uuid import UUID

import pytest
from datadoc_model import Enums
from datadoc_model.Enums import DatasetState
from datadoc_model.Model import DataDocDataSet, DataDocVariable, MetadataDocument

from datadoc.backend.DataDocMetadata import PLACEHOLDER_USERNAME, DataDocMetadata

from .utils import (
    TEST_EXISTING_METADATA_FILE_NAME,
    TEST_EXISTING_METADATA_FILEPATH,
    TEST_EXISTING_METADATA_WITH_VALID_ID_FILEPATH,
    TEST_PARQUET_FILEPATH,
    TEST_RESOURCES_DIRECTORY,
)

dummy_timestamp = datetime(2022, 1, 1)


@pytest.fixture()
def mock_timestamp(mocker):
    mocker.patch(
        "datadoc.backend.DataDocMetadata.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture
def metadata(mock_timestamp):
    yield DataDocMetadata(TEST_PARQUET_FILEPATH)


def make_paths() -> List[Tuple[str, DatasetState]]:
    split_path = list(PurePath(TEST_PARQUET_FILEPATH).parts)
    initial_data = [
        ("kildedata", DatasetState.SOURCE_DATA),
        ("inndata", DatasetState.INPUT_DATA),
        ("roskildedata/klargjorte-data", DatasetState.PROCESSED_DATA),
        ("klargjorte_data", DatasetState.PROCESSED_DATA),
        ("klargjorte-data", DatasetState.PROCESSED_DATA),
        ("statistikk", DatasetState.STATISTIC),
        ("", None),
    ]
    test_data = []

    # Construct paths with each of the potential options in them
    for to_insert, state in initial_data:
        new_path = copy(split_path)
        new_path.insert(-2, to_insert)
        new_path = PurePath("").joinpath(*new_path)
        test_data.append((str(new_path), state))

    return test_data


@pytest.fixture
def remove_document_file() -> None:
    yield None  # Dummy value, No need to return anything in particular here
    os.remove(os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME))


@pytest.fixture
def existing_metadata_file() -> str:
    # Setup by copying the file into the relevant directory
    shutil.copy(TEST_EXISTING_METADATA_FILEPATH, TEST_RESOURCES_DIRECTORY)
    return os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME)


@pytest.fixture
def existing_metadata_with_valid_id_file() -> str:
    # Setup by copying the file into the relevant directory
    shutil.copy(
        TEST_EXISTING_METADATA_WITH_VALID_ID_FILEPATH,
        os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME),
    )
    return os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME)


@pytest.mark.parametrize(("path", "expected_result"), make_paths())
def test_get_dataset_state(
    path: str, expected_result: DatasetState, metadata: DataDocMetadata
):
    actual_state = metadata.get_dataset_state(path)
    assert actual_state == expected_result


def test_get_dataset_state_none(metadata):
    assert metadata.get_dataset_state(None) is None


def test_existing_metadata_file(existing_metadata_file, metadata, remove_document_file):
    assert metadata.meta.dataset.name.en == "successfully_read_existing_file"


def test_metadata_document_percent_complete(metadata):
    dataset = DataDocDataSet(dataset_state=Enums.DatasetState.OUTPUT_DATA)
    variable_1 = DataDocVariable(data_type=Enums.Datatype.BOOLEAN)
    variable_2 = DataDocVariable(data_type=Enums.Datatype.INTEGER)
    document = MetadataDocument(
        percentage_complete=0,
        document_version=1,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )
    metadata.meta = document

    assert metadata.percent_complete == 19


def test_get_dataset_version(metadata: DataDocMetadata):
    assert metadata.get_dataset_version(metadata.short_name) == "1"


def test_get_dataset_version_unknown(metadata: DataDocMetadata):
    assert metadata.get_dataset_version("person_data.parquet") is None


def test_write_metadata_document(metadata: DataDocMetadata, remove_document_file):
    metadata.write_metadata_document()
    assert os.path.exists(
        os.path.join(TEST_RESOURCES_DIRECTORY, TEST_EXISTING_METADATA_FILE_NAME)
    )
    assert metadata.meta.dataset.last_updated_by == PLACEHOLDER_USERNAME
    assert metadata.meta.dataset.created_date == dummy_timestamp
    assert metadata.meta.dataset.last_updated_date == dummy_timestamp


def test_write_metadata_document_existing_document(
    existing_metadata_file, metadata: DataDocMetadata, remove_document_file
):
    original_created_date: datetime = metadata.meta.dataset.created_date
    original_created_by = metadata.meta.dataset.created_by
    metadata.write_metadata_document()
    assert metadata.meta.dataset.created_by == original_created_by
    assert metadata.meta.dataset.created_date == original_created_date
    assert metadata.meta.dataset.last_updated_by == PLACEHOLDER_USERNAME
    assert metadata.meta.dataset.last_updated_date == dummy_timestamp


def test_metadata_id(metadata: DataDocMetadata):
    assert isinstance(metadata.meta.dataset.id, UUID)


def test_existing_metadata_none_id(
    existing_metadata_file, metadata: DataDocMetadata, remove_document_file
):
    pre_open_id = ""
    post_write_id = ""
    with open(existing_metadata_file) as f:
        pre_open_id = json.load(f)["dataset"]["id"]
    assert pre_open_id is None
    assert isinstance(metadata.meta.dataset.id, UUID)
    metadata.write_metadata_document()
    with open(existing_metadata_file) as f:
        post_write_id = json.load(f)["dataset"]["id"]
    assert post_write_id == str(metadata.meta.dataset.id)


def test_existing_metadata_valid_id(
    existing_metadata_with_valid_id_file,
    metadata: DataDocMetadata,
    remove_document_file,
):
    pre_open_id = ""
    post_write_id = ""
    with open(existing_metadata_with_valid_id_file) as f:
        pre_open_id = json.load(f)["dataset"]["id"]
    assert pre_open_id is not None
    assert isinstance(metadata.meta.dataset.id, UUID)
    assert str(metadata.meta.dataset.id) == pre_open_id
    metadata.write_metadata_document()
    with open(existing_metadata_with_valid_id_file) as f:
        post_write_id = json.load(f)["dataset"]["id"]
    assert post_write_id == pre_open_id
