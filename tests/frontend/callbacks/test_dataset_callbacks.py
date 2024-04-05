from __future__ import annotations

import datetime
import random
from typing import TYPE_CHECKING
from typing import cast
from unittest.mock import Mock
from unittest.mock import patch
from uuid import UUID

import pytest
from datadoc_model import model

from datadoc import enums
from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.enums import DataSetState
from datadoc.enums import LanguageStringsEnum
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc.frontend.callbacks.dataset import change_language_dataset_metadata
from datadoc.frontend.callbacks.dataset import open_dataset_handling
from datadoc.frontend.callbacks.dataset import process_special_cases
from datadoc.frontend.callbacks.dataset import update_dataset_metadata_language
from datadoc.frontend.fields.display_dataset import MULTIPLE_LANGUAGE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from tests.utils import TEST_PARQUET_FILEPATH

if TYPE_CHECKING:
    from datadoc.backend.code_list import CodeList
    from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
    from datadoc.frontend.callbacks.utils import MetadataInputTypes

DATASET_CALLBACKS_MODULE = "datadoc.frontend.callbacks.dataset"


@pytest.fixture()
def n_clicks_1():
    return 1


@pytest.fixture()
def file_path():
    return "valid/path/to/file.json"


@pytest.fixture()
def file_path_without_dates():
    return "valid/path/to/person_data_v1.parquet"


@pytest.mark.parametrize(
    ("metadata_identifier", "provided_value", "expected_model_value"),
    [
        (DatasetIdentifiers.SHORT_NAME, "person_data_v1", "person_data_v1"),
        (
            DatasetIdentifiers.ASSESSMENT,
            enums.Assessment.PROTECTED,
            enums.Assessment.PROTECTED.value,
        ),
        (
            DatasetIdentifiers.DATASET_STATUS,
            enums.DataSetStatus.INTERNAL,
            enums.DataSetStatus.INTERNAL.value,
        ),
        (
            DatasetIdentifiers.DATASET_STATE,
            enums.DataSetState.INPUT_DATA,
            enums.DataSetState.INPUT_DATA.value,
        ),
        (
            DatasetIdentifiers.NAME,
            "Dataset name",
            enums.LanguageStringType(nb="Dataset name"),
        ),
        (
            DatasetIdentifiers.DESCRIPTION,
            "Dataset description",
            enums.LanguageStringType(nb="Dataset description"),
        ),
        (
            DatasetIdentifiers.DATA_SOURCE,
            "Census",
            enums.LanguageStringType(nb="Census"),
        ),
        (
            DatasetIdentifiers.REGISTER_URI,
            "https://www.example.com",
            enums.LanguageStringType(nb="https://www.example.com"),
        ),
        (
            DatasetIdentifiers.DESCRIPTION,
            "Population description",
            enums.LanguageStringType(nb="Population description"),
        ),
        (DatasetIdentifiers.VERSION, 1, "1"),
        (
            DatasetIdentifiers.VERSION_DESCRIPTION,
            "Version description",
            enums.LanguageStringType(nb="Version description"),
        ),
        (
            DatasetIdentifiers.TEMPORALITY_TYPE,
            enums.TemporalityTypeType.ACCUMULATED,
            enums.TemporalityTypeType.ACCUMULATED.value,
        ),
        (
            DatasetIdentifiers.SUBJECT_FIELD,
            "al03",
            enums.LanguageStringType(nb="al03"),
        ),
        (
            DatasetIdentifiers.KEYWORD,
            "one,two,three",
            ["one", "two", "three"],
        ),
        (
            DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION,
            "Spatial coverage description",
            enums.LanguageStringType(nb="Spatial coverage description"),
        ),
        (
            DatasetIdentifiers.ID,
            "2f72477a-f051-43ee-bf8b-0d8f47b5e0a7",
            UUID("2f72477a-f051-43ee-bf8b-0d8f47b5e0a7"),
        ),
        (
            DatasetIdentifiers.OWNER,
            "Seksjon for dataplattform",
            "Seksjon for dataplattform",
        ),
    ],
)
def test_accept_dataset_metadata_input_valid_data(
    metadata_identifier: DatasetIdentifiers,
    provided_value: MetadataInputTypes,
    expected_model_value: str,
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = accept_dataset_metadata_input(provided_value, metadata_identifier)
    assert output[0] is False
    assert output[1] == ""
    assert (
        getattr(state.metadata.dataset, metadata_identifier.value)
        == expected_model_value
    )


def test_accept_dataset_metadata_input_incorrect_data_type(metadata: DataDocMetadata):
    state.metadata = metadata
    output = accept_dataset_metadata_input(
        3.1415,
        DatasetIdentifiers.DATASET_STATE.value,
    )
    assert output[0] is True
    assert "validation error for Dataset" in output[1]


earlier = str(datetime.date(2020, 1, 1))
later = str(datetime.date(2024, 1, 1))


@pytest.mark.parametrize(
    ("start_date", "end_date", "expect_error"),
    [
        (None, None, False),
        (later, None, False),
        (None, earlier, False),
        (earlier, earlier, False),
        (earlier, later, False),
        (later, earlier, True),
        (None, "12th March 1953", True),
    ],
    ids=[
        "no-input",
        "start-date-only",
        "end-date-only",
        "identical-dates",
        "correct-order",
        "incorrect-order",
        "invalid-date-format",
    ],
)
def test_accept_dataset_metadata_input_date_validation(
    metadata: DataDocMetadata,
    start_date: str | None,
    end_date: str | None,
    expect_error: bool,  # noqa: FBT001
):
    state.metadata = metadata
    output = accept_dataset_metadata_date_input(
        DatasetIdentifiers.CONTAINS_DATA_UNTIL,
        start_date,
        end_date,
    )
    assert output[2] is expect_error
    if expect_error:
        assert "Validation error" in output[3]
    else:
        assert output[1] == ""
        assert output[3] == ""


def test_update_dataset_metadata_language_strings(
    metadata: DataDocMetadata,
    bokmål_name: str,
    english_name: str,
    language_object: model.LanguageStringType,
):
    state.metadata = metadata
    state.metadata.dataset.name = language_object
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = update_dataset_metadata_language()
    assert english_name not in output
    assert bokmål_name in output
    state.current_metadata_language = SupportedLanguages.ENGLISH
    output = update_dataset_metadata_language()
    assert english_name in output
    assert bokmål_name not in output


def test_update_dataset_metadata_language_enums():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    state.metadata.dataset.dataset_state = DataSetState.PROCESSED_DATA
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = update_dataset_metadata_language()
    assert DataSetState.PROCESSED_DATA.language_strings.nb not in output
    assert DataSetState.PROCESSED_DATA.name in output
    state.current_metadata_language = SupportedLanguages.ENGLISH
    output = update_dataset_metadata_language()
    assert DataSetState.PROCESSED_DATA.language_strings.nb not in output
    assert DataSetState.PROCESSED_DATA.name in output


@pytest.mark.parametrize(
    "enum_for_options",
    [
        enums.Assessment,
        enums.DataSetState,
        enums.DataSetStatus,
        enums.TemporalityTypeType,
    ],
)
@pytest.mark.parametrize("language", list(SupportedLanguages))
def test_change_language_dataset_metadata_options_enums(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    code_list_fake_structure: CodeList,
    metadata: DataDocMetadata,
    enum_for_options: LanguageStringsEnum,
    language: SupportedLanguages,
):
    state.metadata = metadata
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    state.unit_types = code_list_fake_structure
    state.organisational_units = code_list_fake_structure
    value = change_language_dataset_metadata(language)

    for options in cast(list[list[dict[str, str]]], value[0:-1]):
        assert all(list(d.keys()) == ["label", "value"] for d in options)

        member_names = {m.name for m in enum_for_options}  # type: ignore [attr-defined]
        values = [i for d in options for i in d.values()]
        test_without_empty_option = options[1:]
        if member_names.intersection(values):
            assert {d["label"] for d in test_without_empty_option} == {
                e.get_value_for_language(
                    language,
                )
                for e in enum_for_options  # type: ignore [attr-defined]
            }
            assert {d["value"] for d in test_without_empty_option} == {e.name for e in enum_for_options}  # type: ignore [attr-defined]


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_normal(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH

    opened, show_error, naming_standard, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )
    assert opened
    assert not show_error
    assert naming_standard
    assert error_msg == ""
    assert language == "en"


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_file_not_found(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH
    open_file_mock.side_effect = FileNotFoundError()

    opened, show_error, naming_standard, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )
    assert not opened
    assert show_error
    assert not naming_standard
    assert error_msg.startswith(f"Filen '{file_path}' finnes ikke.")
    assert language == "en"


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_general_exception(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH
    open_file_mock.side_effect = ValueError()

    opened, show_error, naming_standard, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )
    assert not opened
    assert show_error
    assert not naming_standard
    assert error_msg.startswith("ValueError")
    assert language == "en"


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_no_click(
    open_file_mock: Mock,  # noqa: ARG001
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH
    opened, show_error, naming_standard, error_msg, language = open_dataset_handling(
        0,
        file_path,
    )
    assert not opened
    assert not show_error
    assert not naming_standard
    assert error_msg == ""
    assert language == "en"


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_naming_standard(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    file_path_without_dates: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH
    opened, show_error, naming_standard, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path_without_dates,
    )
    assert opened is True
    assert not show_error
    assert naming_standard
    assert error_msg == ""
    assert language == "en"


def test_process_special_cases_keyword():
    value = "test,key,words"
    identifier = "keyword"
    expected = ["test", "key", "words"]
    assert process_special_cases(value, identifier) == expected


@patch(f"{DATASET_CALLBACKS_MODULE}.find_existing_language_string")
def test_process_special_cases_language_string(
    mock_find: Mock,
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    state.current_metadata_language = SupportedLanguages.ENGLISH
    value = "Test language string"
    identifier = random.choice(  # noqa: S311
        MULTIPLE_LANGUAGE_DATASET_METADATA,
    )
    expected = model.LanguageStringType(nb="Existing language string", en=value)
    mock_find.return_value = expected

    assert process_special_cases(value, identifier) == expected


def test_process_special_cases_no_change():
    value = ["unchanged", "values"]
    identifier = "random"
    assert process_special_cases(value, identifier) == value
