import random
from copy import deepcopy

from datadoc_model.Enums import DatasetState, Datatype, SupportedLanguages
from datadoc_model.Model import DataDocDataSet, DataDocVariable, LanguageStrings

import datadoc.state as state
from datadoc.backend.DataDocMetadata import DataDocMetadata
from datadoc.frontend.callbacks.dataset import (
    accept_dataset_metadata_input,
    change_language_dataset_metadata,
    update_dataset_metadata_language,
    update_global_language_state,
)
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.variables import (
    accept_variable_metadata_input,
    update_variable_table_dropdown_options_for_language,
    update_variable_table_language,
)
from datadoc.frontend.fields.DisplayDataset import DISPLAYED_DROPDOWN_DATASET_ENUMS
from datadoc.frontend.fields.DisplayVariables import VariableIdentifiers
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

ENGLISH_NAME = "English Name"
BOKMÅL_NAME = "Bokmål Name"
NYNORSK_NAME = "Nynorsk Name"

LANGUAGE_OBJECT = LanguageStrings(en=ENGLISH_NAME, nb=BOKMÅL_NAME)


def test_accept_variable_metadata_input_no_change_in_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = accept_variable_metadata_input(DATA_ORIGINAL, DATA_ORIGINAL)
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_new_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = accept_variable_metadata_input(DATA_VALID, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].variable_role == "IDENTIFIER"
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_incorrect_data_type():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    previous_metadata = deepcopy(state.metadata.meta.variables)
    output = accept_variable_metadata_input(DATA_INVALID, DATA_ORIGINAL)

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for DataDocVariable" in output[2]
    assert state.metadata.meta.variables == previous_metadata


def test_accept_dataset_metadata_input_new_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = accept_dataset_metadata_input(DatasetState.INPUT_DATA, "dataset_state")
    assert output[0] is False
    assert output[1] == ""
    assert state.metadata.meta.dataset.dataset_state == "INPUT_DATA"


def test_accept_dataset_metadata_input_incorrect_data_type():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = accept_dataset_metadata_input(3.1415, "dataset_state")
    assert output[0] is True
    assert "validation error for DataDocDataSet" in output[1]


def test_update_dataset_metadata_language_strings():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
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
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
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
        dataset_metadata, BOKMÅL_NAME, "name"
    )
    assert language_strings == LanguageStrings(nb=BOKMÅL_NAME)


def test_find_existing_language_string_pre_existing_strings():
    dataset_metadata = DataDocDataSet()
    dataset_metadata.name = LANGUAGE_OBJECT
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    language_strings = find_existing_language_string(
        dataset_metadata, NYNORSK_NAME, "name"
    )
    assert language_strings == LanguageStrings(
        nb=BOKMÅL_NAME, en=ENGLISH_NAME, nn=NYNORSK_NAME
    )


def test_update_variable_table_language():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    test_variable = random.choice([v.short_name for v in state.metadata.meta.variables])
    state.metadata.variables_lookup[test_variable].name = LANGUAGE_OBJECT
    output = update_variable_table_language(
        [v.dict() for v in state.metadata.meta.variables],
        SupportedLanguages.NORSK_BOKMÅL,
    )
    name = [
        d[VariableIdentifiers.NAME.value]
        for d in output[0]
        if d[VariableIdentifiers.SHORT_NAME.value] == test_variable
    ][0]
    assert name == BOKMÅL_NAME


def test_nonetype_value_for_language_string():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    state.metadata.variables_lookup["pers_id"].name = LANGUAGE_OBJECT
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    accept_variable_metadata_input(DATA_NONETYPE, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].name == LANGUAGE_OBJECT


def test_update_variable_table_dropdown_options_for_language():
    options = update_variable_table_dropdown_options_for_language(
        SupportedLanguages.NORSK_BOKMÅL
    )
    assert all(k in DataDocVariable.__fields__.keys() for k in options.keys())
    assert all(list(v.keys()) == ["options"] for v in options.values())
    assert all(
        list(d.keys()) == ["label", "value"]
        for v in options.values()
        for d in list(v.values())[0]
    )
    assert [d["label"] for d in options["data_type"]["options"]] == [
        i.get_value_for_language(SupportedLanguages.NORSK_BOKMÅL) for i in Datatype
    ]


def test_update_global_language_state():
    language: SupportedLanguages = random.choice(list(SupportedLanguages))
    update_global_language_state(language)
    assert state.current_metadata_language == language


def test_change_language_dataset_metadata():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    value = change_language_dataset_metadata(SupportedLanguages.NORSK_NYNORSK)
    test = random.choice(DISPLAYED_DROPDOWN_DATASET_ENUMS)
    assert isinstance(value, tuple)

    for options in value[0:-1]:
        assert all(list(d.keys()) == ["label", "value"] for d in options)

        member_names = set(test._member_names_)
        values = [i for d in options for i in d.values()]

        if member_names.intersection(values):
            assert {d["label"] for d in options} == {
                e.get_value_for_language(SupportedLanguages.NORSK_NYNORSK) for e in test
            }
            assert {d["value"] for d in options} == {e.name for e in test}
