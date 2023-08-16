"""Tests for the callbacks package."""
from __future__ import annotations

import random
from copy import deepcopy

import pytest
from datadoc_model.Enums import DatasetState, Datatype, SupportedLanguages
from datadoc_model.Model import DataDocDataSet, DataDocVariable, LanguageStrings

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.frontend.callbacks.dataset import (
    accept_dataset_metadata_input,
    change_language_dataset_metadata,
    update_dataset_metadata_language,
    update_global_language_state,
)
from datadoc.frontend.callbacks.utils import (
    MetadataInputTypes,
    find_existing_language_string,
)
from datadoc.frontend.callbacks.variables import (
    accept_variable_metadata_input,
    update_variable_table_dropdown_options_for_language,
    update_variable_table_language,
)
from datadoc.frontend.fields.display_dataset import DISPLAYED_DROPDOWN_DATASET_ENUMS
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.tests.utils import TEST_PARQUET_FILEPATH

DATA_ORIGINAL = [
    {
        "short_name": "pers_id",
        "variable_role": None,
    },
]
DATA_VALID = [
    {
        "short_name": "pers_id",
        "variable_role": "IDENTIFIER",
    },
]
DATA_NONETYPE = [
    {"short_name": "pers_id", "variable_role": "IDENTIFIER", "name": None},
]
DATA_INVALID = [
    {
        "short_name": "pers_id",
        "variable_role": 3.1415,
    },
]
DATA_CLEAR_URI = [
    {"short_name": "pers_id", "variable_role": None, "definition_uri": ""},
]

ENGLISH_NAME = "English Name"
BOKMÅL_NAME = "Bokmål Name"
NYNORSK_NAME = "Nynorsk Name"

LANGUAGE_OBJECT = LanguageStrings(en=ENGLISH_NAME, nb=BOKMÅL_NAME)


@pytest.fixture()
def active_cell() -> dict[str, MetadataInputTypes]:
    return {"row": 1, "column": 1, "column_id": "short_name", "row_id": None}


def test_accept_variable_metadata_input_no_change_in_data(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = metadata
    output = accept_variable_metadata_input(DATA_ORIGINAL, active_cell, DATA_ORIGINAL)
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_new_data(
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    output = accept_variable_metadata_input(DATA_VALID, active_cell, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].variable_role == "IDENTIFIER"
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_clear_string(
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    output = accept_variable_metadata_input(DATA_CLEAR_URI, active_cell, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].definition_uri is None
    assert output[0] == DATA_CLEAR_URI
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_incorrect_data_type(
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    previous_metadata = deepcopy(state.metadata.meta.variables)
    output = accept_variable_metadata_input(DATA_INVALID, active_cell, DATA_ORIGINAL)

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for DataDocVariable" in output[2]
    assert state.metadata.meta.variables == previous_metadata


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
    assert "validation error for DataDocDataSet" in output[1]


def test_update_dataset_metadata_language_strings():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    state.metadata.meta.dataset.name = LANGUAGE_OBJECT
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = update_dataset_metadata_language()
    assert ENGLISH_NAME not in output
    assert BOKMÅL_NAME in output
    state.current_metadata_language = SupportedLanguages.ENGLISH
    output = update_dataset_metadata_language()
    assert ENGLISH_NAME in output
    assert BOKMÅL_NAME not in output


def test_update_dataset_metadata_language_enums():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    state.metadata.meta.dataset.dataset_state = DatasetState.PROCESSED_DATA
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    output = update_dataset_metadata_language()
    assert DatasetState.PROCESSED_DATA.language_strings.en not in output
    assert DatasetState.PROCESSED_DATA.language_strings.nb not in output
    assert DatasetState.PROCESSED_DATA.name in output
    state.current_metadata_language = SupportedLanguages.ENGLISH
    output = update_dataset_metadata_language()
    assert DatasetState.PROCESSED_DATA.language_strings.en not in output
    assert DatasetState.PROCESSED_DATA.language_strings.nb not in output
    assert DatasetState.PROCESSED_DATA.name in output


def test_find_existing_language_string_no_existing_strings():
    dataset_metadata = DataDocDataSet()
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    language_strings = find_existing_language_string(
        dataset_metadata,
        BOKMÅL_NAME,
        "name",
    )
    assert language_strings == LanguageStrings(nb=BOKMÅL_NAME)


def test_find_existing_language_string_pre_existing_strings():
    dataset_metadata = DataDocDataSet()
    dataset_metadata.name = LANGUAGE_OBJECT
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    language_strings = find_existing_language_string(
        dataset_metadata,
        NYNORSK_NAME,
        "name",
    )
    assert language_strings == LanguageStrings(
        nb=BOKMÅL_NAME,
        en=ENGLISH_NAME,
        nn=NYNORSK_NAME,
    )


def test_update_variable_table_language():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    test_variable = random.choice(  # noqa: S311 not for cryptographic purposes
        [v.short_name for v in state.metadata.meta.variables],
    )
    state.metadata.variables_lookup[test_variable].name = LANGUAGE_OBJECT
    output = update_variable_table_language(
        SupportedLanguages.NORSK_BOKMÅL,
    )
    name = next(
        d[VariableIdentifiers.NAME.value]
        for d in output[0]
        if d[VariableIdentifiers.SHORT_NAME.value] == test_variable
    )
    assert name == BOKMÅL_NAME


def test_nonetype_value_for_language_string(active_cell: dict[str, MetadataInputTypes]):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    state.metadata.variables_lookup["pers_id"].name = LANGUAGE_OBJECT
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    accept_variable_metadata_input(DATA_NONETYPE, active_cell, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].name == LANGUAGE_OBJECT


def test_update_variable_table_dropdown_options_for_language():
    options = update_variable_table_dropdown_options_for_language(
        SupportedLanguages.NORSK_BOKMÅL,
    )
    assert all(k in DataDocVariable.__fields__ for k in options)
    assert all(list(v.keys()) == ["options"] for v in options.values())
    assert all(
        list(d.keys()) == ["label", "value"]
        for v in options.values()
        for d in next(iter(v.values()))
    )
    assert [d["label"] for d in options["data_type"]["options"]] == [
        i.get_value_for_language(SupportedLanguages.NORSK_BOKMÅL) for i in Datatype
    ]


def test_update_global_language_state():
    language: SupportedLanguages = (
        random.choice(  # noqa: S311 not for cryptographic purposes
            list(SupportedLanguages),
        )
    )
    update_global_language_state(language)
    assert state.current_metadata_language == language


def test_change_language_dataset_metadata():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    value = change_language_dataset_metadata(SupportedLanguages.NORSK_NYNORSK)
    test = random.choice(  # noqa: S311 not for cryptographic purposes
        DISPLAYED_DROPDOWN_DATASET_ENUMS,
    )
    assert isinstance(value, tuple)

    for options in value[0:-1]:
        assert all(list(d.keys()) == ["label", "value"] for d in options)

        member_names = set(test._member_names_)  # noqa: SLF001
        values = [i for d in options for i in d.values()]

        if member_names.intersection(values):
            assert {d["label"] for d in options} == {
                e.get_value_for_language(SupportedLanguages.NORSK_NYNORSK) for e in test
            }
            assert {d["value"] for d in options} == {e.name for e in test}
