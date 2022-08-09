from copy import deepcopy
import random

from datadoc_model.Enums import DatasetState, VariableRole
from datadoc_model.Model import LanguageStrings, DataDocDataSet, DataDocVariable
from datadoc.frontend.fields.DisplayVariables import VariableIdentifiers
from datadoc.tests.utils import TEST_PARQUET_FILEPATH
import datadoc.state as state
from datadoc.backend.DataDocMetadata import DataDocMetadata
from datadoc.frontend.callbacks import Callbacks
from datadoc.Enums import SupportedLanguages


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


def test_accept_variable_metadata_input_no_change_in_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_variable_metadata_input(DATA_ORIGINAL, DATA_ORIGINAL)
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_new_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_variable_metadata_input(DATA_VALID, DATA_ORIGINAL)

    assert (
        state.metadata.variables_lookup["pers_id"].variable_role
        == VariableRole.IDENTIFIER
    )
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_incorrect_data_type():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    previous_metadata = deepcopy(state.metadata.meta.variables)
    output = Callbacks.accept_variable_metadata_input(DATA_INVALID, DATA_ORIGINAL)

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for DataDocVariable" in output[2]
    assert state.metadata.meta.variables == previous_metadata


def test_accept_dataset_metadata_input_new_data():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_dataset_metadata_input(
        DatasetState.INPUT_DATA, "dataset_state"
    )
    assert output[0] is False
    assert output[1] == ""
    assert state.metadata.meta.dataset.dataset_state == DatasetState.INPUT_DATA


def test_accept_dataset_metadata_input_incorrect_data_type():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_dataset_metadata_input(3.1415, "dataset_state")
    assert output[0] is True
    assert "validation error for DataDocDataSet" in output[1]


def test_change_language():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    state.metadata.meta.dataset.name = LanguageStrings(en=ENGLISH_NAME, nb=BOKMÅL_NAME)
    output = Callbacks.update_dataset_metadata_language(SupportedLanguages.NORSK_BOKMÅL)
    assert ENGLISH_NAME not in output
    assert BOKMÅL_NAME in output
    output = Callbacks.update_dataset_metadata_language(SupportedLanguages.ENGLISH)
    assert ENGLISH_NAME in output
    assert BOKMÅL_NAME not in output


def test_find_existing_language_string_no_existing_strings():
    dataset_metadata = DataDocDataSet()
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    language_strings = Callbacks.find_existing_language_string(
        dataset_metadata, BOKMÅL_NAME, "name"
    )
    assert language_strings == LanguageStrings(nb=BOKMÅL_NAME)


def test_find_existing_language_string_pre_existing_strings():
    dataset_metadata = DataDocDataSet()
    dataset_metadata.name = LanguageStrings(en=ENGLISH_NAME, nb=BOKMÅL_NAME)
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    language_strings = Callbacks.find_existing_language_string(
        dataset_metadata, NYNORSK_NAME, "name"
    )
    assert language_strings == LanguageStrings(
        nb=BOKMÅL_NAME, en=ENGLISH_NAME, nn=NYNORSK_NAME
    )


def test_update_variable_table_language():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    test_variable = random.choice([v.short_name for v in state.metadata.meta.variables])
    state.metadata.variables_lookup[test_variable].name = LanguageStrings(
        en=ENGLISH_NAME, nb=BOKMÅL_NAME
    )
    output = Callbacks.update_variable_table_language(
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
    ENGLISH_NAME = "English Name"
    BOKMÅL_NAME = "Bokmål Name"
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    state.metadata.variables_lookup["pers_id"].name = LanguageStrings(
        en=ENGLISH_NAME, nb=BOKMÅL_NAME
    )
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    Callbacks.accept_variable_metadata_input(DATA_NONETYPE, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].name == LanguageStrings(
        en=ENGLISH_NAME, nb=BOKMÅL_NAME
    )
