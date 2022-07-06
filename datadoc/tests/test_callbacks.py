from copy import deepcopy
from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.Model import VariableRole
from datadoc.tests.utils import TEST_PARQUET_FILEPATH
from datadoc.Callbacks import accept_variable_metadata_input
import datadoc.globals as globals


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
    output = accept_variable_metadata_input(DATA_ORIGINAL, DATA_ORIGINAL)
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_new_data():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    output = accept_variable_metadata_input(DATA_VALID, DATA_ORIGINAL)

    assert (
        globals.metadata.variables_metadata["pers_id"].variable_role
        == VariableRole.IDENTIFIER
    )
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_metadata_input_incorrect_data_type():
    globals.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    previous_metadata = deepcopy(globals.metadata.variables_metadata)
    output = accept_variable_metadata_input(DATA_INVALID, DATA_ORIGINAL)

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for DataDocVariable" in output[2]
    assert globals.metadata.variables_metadata == previous_metadata
