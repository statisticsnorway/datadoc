from copy import deepcopy

from datadoc.Enums import DatasetState, VariableRole
from datadoc.tests.utils import TEST_PARQUET_FILEPATH
import datadoc.globals as globals
from datadoc.DataDocMetadata import DataDocMetadata
from datadoc import Callbacks


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
DATA_INVALID = [
    {
        "short_name": "pers_id",
        "variable_role": 3.1415,
    },
]


def test_accept_variable_metadata_input_no_change_in_data():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_variable_metadata_input(DATA_ORIGINAL, DATA_ORIGINAL)
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_new_data():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_variable_metadata_input(DATA_VALID, DATA_ORIGINAL)

    assert (
        globals.metadata.variables_lookup["pers_id"].variable_role
        == VariableRole.IDENTIFIER
    )
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_incorrect_data_type():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    previous_metadata = deepcopy(globals.metadata.meta.variables)
    output = Callbacks.accept_variable_metadata_input(DATA_INVALID, DATA_ORIGINAL)

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for DataDocVariable" in output[2]
    assert globals.metadata.meta.variables == previous_metadata


def test_accept_dataset_metadata_input_new_data():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_dataset_metadata_input(
        DatasetState.INPUT_DATA, "dataset_state"
    )
    assert output[0] is False
    assert output[1] == ""
    assert globals.metadata.meta.dataset.dataset_state == DatasetState.INPUT_DATA


def test_accept_dataset_metadata_input_incorrect_data_type():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = Callbacks.accept_dataset_metadata_input(3.1415, "dataset_state")
    assert output[0] is True
    assert "validation error for DataDocDataSet" in output[1]
