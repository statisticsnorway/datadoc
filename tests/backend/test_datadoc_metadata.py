"""Tests for the DataDocMetadata class."""

from __future__ import annotations

import json
import pathlib
import shutil
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID

import pytest
from cloudpathlib.local import LocalGSClient
from cloudpathlib.local import LocalGSPath
from datadoc_model.model import DatadocMetadata
from datadoc_model.model import Dataset
from datadoc_model.model import Variable

from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.backend.user_info import PLACEHOLDER_EMAIL_ADDRESS
from datadoc.backend.user_info import TestUserInfo
from datadoc.enums import Assessment
from datadoc.enums import DataSetState
from datadoc.enums import DataSetStatus
from datadoc.enums import DataType
from datadoc.enums import VariableRole
from tests.utils import TEST_BUCKET_PARQUET_FILEPATH
from tests.utils import TEST_EXISTING_METADATA_DIRECTORY
from tests.utils import TEST_EXISTING_METADATA_FILE_NAME
from tests.utils import TEST_PARQUET_FILEPATH
from tests.utils import TEST_PROCESSED_DATA_POPULATION_DIRECTORY
from tests.utils import TEST_RESOURCES_DIRECTORY

if TYPE_CHECKING:
    import os
    from collections.abc import Generator
    from datetime import datetime


DATADOC_METADATA_MODULE = "datadoc.backend.datadoc_metadata"


@pytest.fixture()
def generate_periodic_file(
    existing_data_path: Path,
    insert_string: str,
) -> Generator[Path, None, None]:
    file_name = existing_data_path.name
    insert_pos = file_name.find("_v1")
    new_file_name = file_name[:insert_pos] + insert_string + file_name[insert_pos:]
    new_path = TEST_RESOURCES_DIRECTORY / new_file_name
    shutil.copy(existing_data_path, new_path)
    yield new_path
    if new_path.exists():
        new_path.unlink()


@pytest.mark.usefixtures("existing_metadata_file")
def test_existing_metadata_file(
    metadata: DataDocMetadata,
):
    assert metadata.dataset.name.en == "successfully_read_existing_file"  # type: ignore [union-attr]


def test_metadata_document_percent_complete(metadata: DataDocMetadata):
    dataset = Dataset(dataset_state=DataSetState.OUTPUT_DATA)
    variable_1 = Variable(data_type=DataType.BOOLEAN)
    variable_2 = Variable(data_type=DataType.INTEGER)
    document = DatadocMetadata(
        percentage_complete=0,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )
    metadata.dataset = document.dataset  # type: ignore [assignment]
    metadata.variables = document.variables  # type: ignore [assignment]

    assert metadata.percent_complete == 17  # noqa: PLR2004


def test_write_metadata_document(
    dummy_timestamp: datetime,
    metadata: DataDocMetadata,
    tmp_path: pathlib.Path,
):
    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME
    assert Path.exists(written_document)
    assert metadata.dataset.metadata_created_date == dummy_timestamp
    assert metadata.dataset.metadata_created_by == PLACEHOLDER_EMAIL_ADDRESS
    assert metadata.dataset.metadata_last_updated_date == dummy_timestamp
    assert metadata.dataset.metadata_last_updated_by == PLACEHOLDER_EMAIL_ADDRESS

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
    assert datadoc_metadata["metadata_created_by"] == PLACEHOLDER_EMAIL_ADDRESS
    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            metadata_last_updated_date=datadoc_metadata["metadata_last_updated_date"],
        ).metadata_last_updated_date
        == dummy_timestamp
    )
    assert datadoc_metadata["metadata_last_updated_by"] == PLACEHOLDER_EMAIL_ADDRESS


@pytest.mark.usefixtures("existing_metadata_file")
@patch(
    "datadoc.backend.user_info.get_user_info_for_current_platform",
    return_value=TestUserInfo(),
)
def test_write_metadata_document_existing_document(
    _mock_user_info: MagicMock,  # noqa: PT019 it's a patch, not a fixture
    dummy_timestamp: datetime,
    metadata: DataDocMetadata,
):
    original_created_date = metadata.dataset.metadata_created_date
    original_created_by = metadata.dataset.metadata_created_by
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_by == original_created_by
    assert metadata.dataset.metadata_created_date == original_created_date
    assert metadata.dataset.metadata_last_updated_by == PLACEHOLDER_EMAIL_ADDRESS
    assert metadata.dataset.metadata_last_updated_date == dummy_timestamp


def test_metadata_id(metadata: DataDocMetadata):
    assert isinstance(metadata.dataset.id, UUID)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "invalid_id_field"],
)
def test_existing_metadata_none_id(
    existing_metadata_file: Path,
    metadata: DataDocMetadata,
):
    with existing_metadata_file.open() as f:
        pre_open_id: None = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is None
    assert isinstance(metadata.dataset.id, UUID)
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == str(metadata.dataset.id)


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "valid_id_field"],
)
def test_existing_metadata_valid_id(
    existing_metadata_file: Path,
    metadata: DataDocMetadata,
):
    pre_open_id = ""
    post_write_id = ""
    with existing_metadata_file.open() as f:
        pre_open_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert pre_open_id is not None
    assert isinstance(metadata.dataset.id, UUID)
    assert str(metadata.dataset.id) == pre_open_id
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        post_write_id = json.load(f)["datadoc"]["dataset"]["id"]
    assert post_write_id == pre_open_id


def test_variable_role_default_value(metadata: DataDocMetadata):
    assert all(
        v.variable_role == VariableRole.MEASURE.value for v in metadata.variables
    )


def test_direct_person_identifying_default_value(metadata: DataDocMetadata):
    assert all(not v.direct_person_identifying for v in metadata.variables)


def test_save_file_path_metadata_field(
    existing_metadata_file: Path,
    metadata: DataDocMetadata,
):
    metadata.write_metadata_document()
    with existing_metadata_file.open() as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset_path)


def test_save_file_path_dataset_and_no_metadata(
    metadata: DataDocMetadata,
    tmp_path: pathlib.Path,
):
    metadata.write_metadata_document()
    with (tmp_path / TEST_EXISTING_METADATA_FILE_NAME).open() as f:
        saved_file_path = json.load(f)["datadoc"]["dataset"]["file_path"]
    assert saved_file_path == str(metadata.dataset_path)


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
    assert metadata.dataset.contains_data_from == expected_from
    assert metadata.dataset.contains_data_until == expected_until


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
    ("dataset_path", "expected_type"),
    [
        (
            TEST_PROCESSED_DATA_POPULATION_DIRECTORY
            / "person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            DataSetStatus.INTERNAL.value,
        ),
        (
            TEST_PARQUET_FILEPATH,
            DataSetStatus.DRAFT.value,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_dataset_status_default_value(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    dataset_path: str,
    expected_type: DataSetStatus | None,
):
    datadoc_metadata = DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        str(dataset_path),
    )

    assert datadoc_metadata.dataset.dataset_status == expected_type


@pytest.mark.parametrize(
    ("path_parts_to_insert", "expected_type"),
    [
        (
            "kildedata",
            None,
        ),
        (
            "inndata",
            Assessment.PROTECTED.value,
        ),
        (
            "klargjorte_data",
            Assessment.PROTECTED.value,
        ),
        (
            "statistikk",
            Assessment.PROTECTED.value,
        ),
        (
            "utdata",
            Assessment.OPEN.value,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_dataset_assessment_default_value(
    expected_type: Assessment | None,
    copy_dataset_to_path: Path,
):
    datadoc_metadata = DataDocMetadata(
        statistic_subject_mapping=StatisticSubjectMapping(source_url=""),
        dataset_path=str(copy_dataset_to_path),
    )
    assert datadoc_metadata.dataset.assessment == expected_type


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
    subject_mapping_fake_statistical_structure.wait_for_external_result()
    metadata = DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        str(copy_dataset_to_path),
    )
    # TODO @mmwinther: Remove multiple_language_support once the model is updated.
    # https://github.com/statisticsnorway/ssb-datadoc-model/issues/41
    assert metadata.dataset.subject_field.en == expected_subject_code


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_EXISTING_METADATA_DIRECTORY / "pseudo"],
)
def test_existing_pseudo_metadata_file(
    existing_metadata_file: Path,
    metadata: DataDocMetadata,
):
    pre_open_metadata = json.loads(existing_metadata_file.read_text())
    metadata.write_metadata_document()
    post_open_metadata = json.loads(existing_metadata_file.read_text())

    assert len(metadata.meta.variables) == 8  # noqa: PLR2004
    assert (
        pre_open_metadata["pseudonymization"] == post_open_metadata["pseudonymization"]
    )
    assert post_open_metadata["datadoc"] is not None
