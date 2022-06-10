from copy import copy
from pathlib import PurePath
from .. import DataDocMetadata
from .utils import TEST_PARQUET_FILEPATH


def setup_module():
    split_path = list(PurePath(TEST_PARQUET_FILEPATH).parts)
    initial_data = [
        ("kildedata", "SOURCE_DATA"),
        ("inndata", "INPUT_DATA"),
        ("klargjorte_data", "PROCESSED_DATA"),
        ("", None),
    ]
    global test_data
    test_data = []

    # Construct paths with each of the potential options in them
    for to_insert, state in initial_data:
        new_path = copy(split_path)
        new_path.insert(-2, to_insert)
        new_path = PurePath("").joinpath(*new_path)
        test_data.append((new_path, state))


def test_get_dataset_state():
    metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    for path, expected_result in test_data:
        actual_state = metadata.get_dataset_state(path)
        assert actual_state == expected_result


def test_get_dataset_state_no_parameter_supplied():
    metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    assert metadata.get_dataset_state() is None
