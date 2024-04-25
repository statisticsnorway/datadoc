from __future__ import annotations

import datetime
import random
from typing import TYPE_CHECKING
from unittest.mock import Mock
from unittest.mock import patch
from uuid import UUID

import dash
import pytest
from datadoc_model import model

from datadoc import enums
from datadoc import state
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc.frontend.callbacks.dataset import open_dataset_handling
from datadoc.frontend.callbacks.dataset import process_special_cases
from datadoc.frontend.fields.display_dataset import (
    MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
)
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers

if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata
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
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Dataset name",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.DESCRIPTION,
            "Dataset description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Dataset description",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.DATA_SOURCE,
            "Census",
            "Census",
        ),
        (
            DatasetIdentifiers.DESCRIPTION,
            "Population description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Population description",
                    ),
                ],
            ),
        ),
        (DatasetIdentifiers.VERSION, 1, "1"),
        (
            DatasetIdentifiers.VERSION_DESCRIPTION,
            "Version description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Version description",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.TEMPORALITY_TYPE,
            enums.TemporalityTypeType.ACCUMULATED,
            enums.TemporalityTypeType.ACCUMULATED.value,
        ),
        (
            DatasetIdentifiers.SUBJECT_FIELD,
            "al03",
            "al03",
        ),
        (
            DatasetIdentifiers.KEYWORD,
            "one,two,three",
            ["one", "two", "three"],
        ),
        (
            DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION,
            "Spatial coverage description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Spatial coverage description",
                    ),
                ],
            ),
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
    output = accept_dataset_metadata_input(provided_value, metadata_identifier, "nb")
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
        "",
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


@pytest.mark.parametrize(
    "path",
    [
        "valid/path/to/person_data_v1.parquet",
        "  path/with/extra/whitespace/person_data_v1.parquet  ",
    ],
)
@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_normal(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    path: str,
):
    opened, show_error, naming_standard, error_msg, counter = open_dataset_handling(
        n_clicks_1,
        path,
        0,
    )
    assert opened
    assert not show_error
    assert naming_standard
    assert error_msg == ""
    assert counter == 1


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_file_not_found(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    open_file_mock.side_effect = FileNotFoundError()

    opened, show_error, naming_standard, error_msg, counter = open_dataset_handling(
        n_clicks_1,
        file_path,
        0,
    )
    assert not opened
    assert show_error
    assert not naming_standard
    assert error_msg.startswith(f"Filen '{file_path}' finnes ikke.")
    assert counter == dash.no_update


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_general_exception(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    open_file_mock.side_effect = ValueError()

    opened, show_error, naming_standard, error_msg, counter = open_dataset_handling(
        n_clicks_1,
        file_path,
        0,
    )
    assert not opened
    assert show_error
    assert not naming_standard
    assert error_msg.startswith("ValueError")
    assert counter == dash.no_update


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_no_click(
    open_file_mock: Mock,  # noqa: ARG001
    file_path: str,
):
    opened, show_error, naming_standard, error_msg, counter = open_dataset_handling(
        0,
        file_path,
        0,
    )
    assert not opened
    assert not show_error
    assert not naming_standard
    assert error_msg == ""
    assert counter == 1


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_naming_standard(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    file_path_without_dates: str,
):
    opened, show_error, naming_standard, error_msg, counter = open_dataset_handling(
        n_clicks_1,
        file_path_without_dates,
        0,
    )
    assert opened is True
    assert not show_error
    assert naming_standard
    assert error_msg == ""
    assert counter == 1


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
    language = "en"
    value = "Test language string"
    identifier = random.choice(  # noqa: S311
        MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
    )
    expected = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="Existing language string",
            ),
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=value,
            ),
        ],
    )
    mock_find.return_value = expected

    assert process_special_cases(value, identifier, language) == expected


def test_process_special_cases_no_change():
    value = ["unchanged", "values"]
    identifier = "random"
    assert process_special_cases(value, identifier) == value
