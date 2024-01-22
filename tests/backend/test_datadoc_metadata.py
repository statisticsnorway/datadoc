"""Tests for the DataDocMetadata class."""
from __future__ import annotations

import json
import pathlib
from copy import copy
from pathlib import Path
from pathlib import PurePath
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from datadoc_model.model import DatadocJsonSchema
from datadoc_model.model import Dataset
from datadoc_model.model import Variable

from datadoc.backend.datadoc_metadata import PLACEHOLDER_USERNAME
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.enums import DatasetState
from datadoc.enums import DataType
from datadoc.enums import VariableRole
from tests.utils import TEST_EXISTING_METADATA_DIRECTORY, TEST_RESOURCES_METADATA_DOCUMENT
from tests.utils import TEST_EXISTING_METADATA_FILE_NAME
from tests.utils import TEST_PARQUET_FILEPATH
from tests.utils import TEST_RESOURCES_DIRECTORY

if TYPE_CHECKING:
    from datetime import datetime


def make_paths() -> list[tuple[str, DatasetState | None]]:
    split_path = list(PurePath(TEST_PARQUET_FILEPATH).parts)
    initial_data = [
        ("kildedata", DatasetState.SOURCE_DATA),
        ("inndata", DatasetState.INPUT_DATA),
        ("roskildedata/klargjorte-data", DatasetState.PROCESSED_DATA),
        ("klargjorte_data", DatasetState.PROCESSED_DATA),
        ("klargjorte-data", DatasetState.PROCESSED_DATA),
        ("statistikk", DatasetState.STATISTICS),
        ("", None),
    ]
    test_data = []

    # Construct paths with each of the potential options in them
    for to_insert, state in initial_data:
        new_path = copy(split_path)
        new_path.insert(-2, to_insert)
        joined_path = PurePath().joinpath(*new_path)
        test_data.append((str(joined_path), state))

    return test_data


@pytest.mark.parametrize(("path", "expected_result"), make_paths())
def test_get_dataset_state(
    path: str,
    expected_result: DatasetState,
    metadata: DataDocMetadata,
):
    actual_state = metadata.get_dataset_state(pathlib.Path(path))
    assert actual_state == expected_result


@pytest.mark.usefixtures("existing_metadata_file", "remove_document_file")
def test_existing_metadata_file(
    metadata: DataDocMetadata,
):
    assert metadata.meta.dataset.name.en == "successfully_read_existing_file"


def test_metadata_document_percent_complete(metadata: DataDocMetadata):
    dataset = Dataset(dataset_state=DatasetState.OUTPUT_DATA)
    variable_1 = Variable(data_type=DataType.BOOLEAN)
    variable_2 = Variable(data_type=DataType.INTEGER)
    document = DatadocJsonSchema(
        percentage_complete=0,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )
    metadata.meta = document

    assert metadata.percent_complete == 17  # noqa: PLR2004


@pytest.mark.parametrize(
    ("short_name", "expected"),
    [
        ("person_data_v1", "1"),
        ("person_data_v2", "2"),
        ("person_data", None),
        ("person_testdata_p2021-12-31_p2021-12-31_v20", "20"),
    ],
)
def test_get_dataset_version(
    short_name: str,
    expected: str | None,
):
    assert DataDocMetadata.get_dataset_version(short_name) == expected


@pytest.mark.usefixtures("remove_document_file")
def test_write_metadata_document(
    dummy_timestamp: datetime,
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    written_document = TEST_RESOURCES_DIRECTORY / TEST_EXISTING_METADATA_FILE_NAME
    assert Path.exists(written_document)
    assert metadata.meta.dataset.metadata_created_date == dummy_timestamp
    assert metadata.meta.dataset.metadata_created_by == PLACEHOLDER_USERNAME
    assert metadata.meta.dataset.metadata_last_updated_date == dummy_timestamp
    assert metadata.meta.dataset.metadata_last_updated_by == PLACEHOLDER_USERNAME

    with Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["dataset"]

    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            metadata_created_date=datadoc_metadata["metadata_created_date"],
        ).metadata_created_date
        == dummy_timestamp
    )
    assert datadoc_metadata["metadata_created_by"] == PLACEHOLDER_USERNAME
    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            metadata_last_updated_date=datadoc_metadata["metadata_last_updated_date"],
        ).metadata_last_updated_date
        == dummy_timestamp
    )
    assert datadoc_metadata["metadata_last_updated_by"] == PLACEHOLDER_USERNAME


@pytest.mark.usefixtures("existing_metadata_file", "remove_document_file")
def test_write_metadata_document_existing_document(
    dummy_timestamp: datetime,
    metadata: DataDocMetadata,
):
    original_created_date: datetime = metadata.meta.dataset.metadata_created_date
    original_created_by = metadata.meta.dataset.metadata_created_by
    metadata.write_metadata_document()
    assert metadata.meta.dataset.metadata_created_by == original_created_by
    assert metadata.meta.dataset.metadata_created_date == original_created_date
    assert metadata.meta.dataset.metadata_last_updated_by == PLACEHOLDER_USERNAME
    assert metadata.meta.dataset.metadata_last_updated_date == dummy_timestamp


def test_metadata_id(metadata: DataDocMetadata):
    assert isinstance(metadata.meta.dataset.id, UUID)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "invalid_id_field"],
)
@pytest.mark.usefixtures("remove_document_file")
def test_existing_metadata_none_id(
    existing_metadata_file: str,
    metadata: DataDocMetadata,
):
    with Path.open(Path(existing_metadata_file)) as f:
        pre_open_id: None = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is None
    assert isinstance(metadata.meta.dataset.id, UUID)
    metadata.write_metadata_document()
    with Path.open(Path(existing_metadata_file)) as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == str(metadata.meta.dataset.id)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "valid_id_field"],
)
@pytest.mark.usefixtures("remove_document_file")
def test_existing_metadata_valid_id(
    existing_metadata_file: str,
    metadata: DataDocMetadata,
):
    pre_open_id = ""
    post_write_id = ""
    with Path.open(Path(existing_metadata_file)) as f:
        pre_open_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is not None
    assert isinstance(metadata.meta.dataset.id, UUID)
    assert str(metadata.meta.dataset.id) == pre_open_id
    metadata.write_metadata_document()
    with Path.open(Path(existing_metadata_file)) as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == pre_open_id


def test_variable_role_default_value(metadata: DataDocMetadata):
    assert all(
        v.variable_role == VariableRole.MEASURE.value for v in metadata.meta.variables
    )


def test_direct_person_identifying_default_value(metadata: DataDocMetadata):
    assert all(not v.direct_person_identifying for v in metadata.meta.variables)


# Test with existing dataset and metadata document
def test_save_file_path_metadata_field(
    existing_metadata_file: str,
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    with Path.open(Path(existing_metadata_file)) as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset)


# Test with dataset and no metadata document
def test_save_file_path_dataset_and_no_metadata(
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    with Path.open(Path(TEST_RESOURCES_METADATA_DOCUMENT)) as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset)


# Test with metadata document and no dataset

