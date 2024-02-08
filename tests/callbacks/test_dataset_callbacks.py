import random
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from datadoc_model import model

from datadoc import enums
from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.enums import DatasetState
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc.frontend.callbacks.dataset import change_language_dataset_metadata
from datadoc.frontend.callbacks.dataset import open_dataset_handling
from datadoc.frontend.callbacks.dataset import process_special_cases
from datadoc.frontend.callbacks.dataset import update_dataset_metadata_language
from datadoc.frontend.callbacks.utils import get_language_strings_enum
from datadoc.frontend.fields.display_dataset import MULTIPLE_LANGUAGE_DATASET_METADATA
from tests.utils import TEST_PARQUET_FILEPATH

DATASET_CALLBACKS_MODULE = "datadoc.frontend.callbacks.dataset"


@pytest.fixture()
def n_clicks_1():
    return 1


@pytest.fixture()
def file_path():
    return "valid/path/to/file.json"


def test_accept_dataset_metadata_input_new_data():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    output = accept_dataset_metadata_input(DatasetState.INPUT_DATA, "dataset_state")
    assert output[0] is False
    assert output[1] == ""
    assert state.metadata.meta.dataset.dataset_state == "INPUT_DATA"


def test_accept_dataset_metadata_input_incorrect_data_type():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    output = accept_dataset_metadata_input(3.1415, "dataset_state")
    assert output[0] is True
    assert "validation error for Dataset" in output[1]


def test_update_dataset_metadata_language_strings(
    bokmål_name: str,
    english_name: str,
    language_object: model.LanguageStringType,
):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    state.metadata.meta.dataset.name = language_object
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
    state.metadata.meta.dataset.dataset_state = DatasetState.PROCESSED_DATA
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = update_dataset_metadata_language()
    assert DatasetState.PROCESSED_DATA.language_strings.nb not in output
    assert DatasetState.PROCESSED_DATA.name in output
    state.current_metadata_language = SupportedLanguages.ENGLISH
    output = update_dataset_metadata_language()
    assert DatasetState.PROCESSED_DATA.language_strings.nb not in output
    assert DatasetState.PROCESSED_DATA.name in output


def test_change_language_dataset_metadata():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    value = change_language_dataset_metadata(SupportedLanguages.NORSK_NYNORSK)
    test = get_language_strings_enum(
        random.choice(  # noqa: S311 not for cryptographic purposes
            [
                enums.Assessment,
                enums.DatasetState,
                enums.DatasetStatus,
                enums.TemporalityTypeType,
            ],
        ),
    )
    assert isinstance(value, tuple)

    for options in value[0:-1]:
        assert all(list(d.keys()) == ["label", "value"] for d in options)

        member_names = set(test._member_names_)  # noqa: SLF001
        values = [i for d in options for i in d.values()]

        if member_names.intersection(values):
            assert {d["label"] for d in options} == {
                e.get_value_for_language(
                    SupportedLanguages.NORSK_NYNORSK,
                )
                for e in test
            }
            assert {d["value"] for d in options} == {e.name for e in test}


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_normal(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH

    opened, show_error, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )

    assert opened
    assert not show_error
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

    opened, show_error, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )
    assert not opened
    assert show_error
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

    opened, show_error, error_msg, language = open_dataset_handling(
        n_clicks_1,
        file_path,
    )
    assert not opened
    assert show_error
    assert error_msg.startswith("ValueError")
    assert language == "en"


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_no_click(
    open_file_mock: Mock,  # noqa: ARG001
    file_path: str,
):
    state.current_metadata_language = SupportedLanguages.ENGLISH
    opened, show_error, error_msg, language = open_dataset_handling(0, file_path)

    assert not opened
    assert not show_error
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
