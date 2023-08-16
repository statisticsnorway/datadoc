"""Tests for the DataDocMetadata class."""
from __future__ import annotations

import json
from copy import copy
from pathlib import Path, PurePath
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from datadoc_model import Enums
from datadoc_model.Enums import DatasetState
from datadoc_model.Model import DataDocDataSet, DataDocVariable, MetadataDocument

from datadoc.backend.datadoc_metadata import PLACEHOLDER_USERNAME, DataDocMetadata

from .utils import (
    TEST_EXISTING_METADATA_DIRECTORY,
    TEST_EXISTING_METADATA_FILE_NAME,
    TEST_PARQUET_FILEPATH,
    TEST_RESOURCES_DIRECTORY,
)

if TYPE_CHECKING:
    from datetime import datetime


def make_paths() -> list[tuple[str, DatasetState]]:
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
        new_path = PurePath().joinpath(*new_path)
        test_data.append((str(new_path), state))

    return test_data


@pytest.mark.parametrize(("path", "expected_result"), make_paths())
def test_get_dataset_state(
    path: str,
    expected_result: DatasetState,
    metadata: DataDocMetadata,
):
    actual_state = metadata.get_dataset_state(path)
    assert actual_state == expected_result


def test_get_dataset_state_none(metadata: DataDocMetadata):
    assert metadata.get_dataset_state(None) is None


@pytest.mark.usefixtures("existing_metadata_file", "remove_document_file")
def test_existing_metadata_file(
    metadata: DataDocMetadata,
):
    assert metadata.meta.dataset.name.en == "successfully_read_existing_file"


def test_metadata_document_percent_complete(metadata: DataDocMetadata):
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

    assert metadata.percent_complete == 17  # noqa: PLR2004


def test_get_dataset_version(metadata: DataDocMetadata):
    assert metadata.get_dataset_version(metadata.short_name) == "1"


def test_get_dataset_version_unknown(metadata: DataDocMetadata):
    assert metadata.get_dataset_version("person_data.parquet") is None


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

    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        DataDocDataSet(
            metadata_created_date=written_metadata["dataset"]["metadata_created_date"],
        ).metadata_created_date
        == dummy_timestamp
    )
    assert written_metadata["dataset"]["metadata_created_by"] == PLACEHOLDER_USERNAME
    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        DataDocDataSet(
            metadata_last_updated_date=written_metadata["dataset"][
                "metadata_last_updated_date"
            ],
        ).metadata_last_updated_date
        == dummy_timestamp
    )
    assert (
        written_metadata["dataset"]["metadata_last_updated_by"] == PLACEHOLDER_USERNAME
    )


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
    pre_open_id = ""
    post_write_id = ""
    with Path.open(existing_metadata_file) as f:
        pre_open_id = json.load(f)["dataset"]["id"]
    assert pre_open_id is None
    assert isinstance(metadata.meta.dataset.id, UUID)
    metadata.write_metadata_document()
    with Path.open(existing_metadata_file) as f:
        post_write_id = json.load(f)["dataset"]["id"]
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
    with Path.open(existing_metadata_file) as f:
        pre_open_id = json.load(f)["dataset"]["id"]
    assert pre_open_id is not None
    assert isinstance(metadata.meta.dataset.id, UUID)
    assert str(metadata.meta.dataset.id) == pre_open_id
    metadata.write_metadata_document()
    with Path.open(existing_metadata_file) as f:
        post_write_id = json.load(f)["dataset"]["id"]
    assert post_write_id == pre_open_id


def test_variable_role_default_value(metadata: DataDocMetadata):
    assert all(
        v.variable_role == Enums.VariableRole.MEASURE.value
        for v in metadata.meta.variables
    )


def test_direct_person_identifying_default_value(metadata: DataDocMetadata):
    assert all(not v.direct_person_identifying for v in metadata.meta.variables)
