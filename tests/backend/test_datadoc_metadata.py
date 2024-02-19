"""Tests for the DataDocMetadata class."""

from __future__ import annotations

import json
import pathlib
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from cloudpathlib.local import LocalGSClient
from cloudpathlib.local import LocalGSPath
from datadoc_model.model import DatadocJsonSchema
from datadoc_model.model import Dataset
from datadoc_model.model import Variable

from datadoc.backend.datadoc_metadata import PLACEHOLDER_USERNAME
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.enums import Assessment
from datadoc.enums import DatasetState
from datadoc.enums import DatasetStatus
from datadoc.enums import DataType
from datadoc.enums import VariableRole
from tests.utils import TEST_BUCKET_PARQUET_FILEPATH
from tests.utils import TEST_EXISTING_METADATA_DIRECTORY
from tests.utils import TEST_EXISTING_METADATA_FILE_NAME
from tests.utils import TEST_INPUT_DATA_POPULATION_DIRECTORY
from tests.utils import TEST_OUTPUT_DATA_POPULATION_DIRECTORY
from tests.utils import TEST_PARQUET_FILEPATH
from tests.utils import TEST_PROCESSED_DATA_POPULATION_DIRECTORY
from tests.utils import TEST_RESOURCES_DIRECTORY
from tests.utils import TEST_RESOURCES_METADATA_DOCUMENT
from tests.utils import TEST_STATISTICS_POPULATION_DIRECTORY

if TYPE_CHECKING:
    import os
    from datetime import datetime


DATADOC_METADATA_MODULE = "datadoc.backend.datadoc_metadata"


@pytest.mark.usefixtures("existing_metadata_file")
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


@pytest.mark.usefixtures("existing_metadata_file")
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


def test_save_file_path_metadata_field(
    existing_metadata_file: str,
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    with Path.open(Path(existing_metadata_file)) as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset)


def test_save_file_path_dataset_and_no_metadata(
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    with Path.open(Path(TEST_RESOURCES_METADATA_DOCUMENT)) as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset)


@pytest.mark.parametrize(
    ("insert_string", "expected_from", "expected_until"),
    [
        ("_p2021", "2021-01-01", "2021-12-31"),
        ("_p2022_p2023", "2022-01-01", "2023-12-31"),
    ],
)
def test_period_metadata_fields_saved(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    generate_periodic_file,
    expected_from,
    expected_until,
):
    metadata = DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        str(generate_periodic_file),
    )
    assert metadata.meta.dataset.contains_data_from == expected_from
    assert metadata.meta.dataset.contains_data_until == expected_until


@pytest.mark.parametrize(
    ("dataset_path", "expected_type"),
    [
        (TEST_BUCKET_PARQUET_FILEPATH, LocalGSPath),
        (str(TEST_PARQUET_FILEPATH), pathlib.Path),
    ],
)
def test_open_file(
    dataset_path: str,
    expected_type: type[os.PathLike],
    mocker,
):
    mocker.patch(f"{DATADOC_METADATA_MODULE}.AuthClient", autospec=True)
    mocker.patch(f"{DATADOC_METADATA_MODULE}.GSClient", LocalGSClient)
    mocker.patch(
        f"{DATADOC_METADATA_MODULE}.GSPath",
        LocalGSPath,
    )
    file = DataDocMetadata._open_path(  # noqa: SLF001 for testing purposes
        dataset_path,
    )
    assert isinstance(file, expected_type)


@pytest.mark.parametrize(
    ("dataset_path", "metadata_document_path", "expected_type"),
    [
        (
            str(
                TEST_PROCESSED_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            ),
            str(
                TEST_PROCESSED_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json",
            ),
            DatasetStatus.DRAFT.value,
        ),
        (
            str(
                TEST_RESOURCES_DIRECTORY / "person_data_v1.parquet",
            ),
            None,
            DatasetStatus.DRAFT.value,
        ),
        (
            "",
            None,
            None,
        ),
    ],
)
def test_dataset_status_default_value(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    dataset_path: str,
    metadata_document_path: str | None,
    expected_type: DatasetStatus | None,
):
    datadoc_metadata = DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        dataset_path,
        metadata_document_path,
    )

    assert expected_type == datadoc_metadata.meta.dataset.dataset_status


@pytest.mark.parametrize(
    ("dataset_path", "metadata_document_path", "expected_type"),
    [
        (
            str(
                TEST_INPUT_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            ),
            str(
                TEST_INPUT_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json",
            ),
            Assessment.SENSITIVE.value,
        ),
        (
            str(TEST_INPUT_DATA_POPULATION_DIRECTORY / "person_data_v1.parquet"),
            None,
            Assessment.PROTECTED.value,
        ),
        (
            str(
                TEST_PROCESSED_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            ),
            str(
                TEST_PROCESSED_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json",
            ),
            Assessment.PROTECTED.value,
        ),
        (
            str(TEST_PROCESSED_DATA_POPULATION_DIRECTORY / "person_data_v1.parquet"),
            None,
            Assessment.PROTECTED.value,
        ),
        (
            str(
                TEST_STATISTICS_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            ),
            str(
                TEST_STATISTICS_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json",
            ),
            Assessment.SENSITIVE.value,
        ),
        (
            str(TEST_STATISTICS_POPULATION_DIRECTORY / "person_data_v1.parquet"),
            None,
            Assessment.PROTECTED.value,
        ),
        (
            str(
                TEST_OUTPUT_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            ),
            str(
                TEST_OUTPUT_DATA_POPULATION_DIRECTORY
                / "person_testdata_p2021-12-31_p2021-12-31_v1__DOC.json",
            ),
            Assessment.SENSITIVE.value,
        ),
        (
            str(TEST_OUTPUT_DATA_POPULATION_DIRECTORY / "person_data_v1.parquet"),
            None,
            Assessment.OPEN.value,
        ),
        (
            str(TEST_RESOURCES_DIRECTORY / "person_data_v1.parquet"),
            None,
            None,
        ),
        (
            "",
            None,
            None,
        ),
    ],
)
def test_dataset_assessment_default_value(
    dataset_path: str,
    metadata_document_path: str | None,
    expected_type: Assessment | None,
):
    datadoc_metadata = DataDocMetadata(
        statistic_subject_mapping=StatisticSubjectMapping(source_url=""),
        dataset_path=dataset_path,
        metadata_document_path=metadata_document_path,
    )
    assert expected_type == datadoc_metadata.meta.dataset.assessment


@pytest.mark.parametrize(
    ("path_parts_to_insert", "expected_subject_code"),
    [
        (["aa_kortnvan_01", "klargjorte_data"], "aa01"),
        (["ab_kortnvan", "utdata"], "ab00"),
        (["aa_kortnvan_01", "no_dataset_state"], None),
        (["unknown_short_name", "klargjorte_data"], None),
    ],
)
def test_extract_subject_field_value_from_statistic_structure_xml(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    copy_dataset_to_path: Path,
    expected_subject_code: str,
):
    subject_mapping_fake_statistical_structure.wait_for_primary_subject()
    metadata = DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        str(copy_dataset_to_path),
    )
    # TODO @mmwinther: Remove multiple_language_support once the model is updated.
    # https://github.com/statisticsnorway/ssb-datadoc-model/issues/41
    assert metadata.meta.dataset.subject_field.en == expected_subject_code
