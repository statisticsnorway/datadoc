from .. import DataDocMetadata
from .utils import TEST_PARQUET_FILEPATH


def test_get_dataset_state():
    metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    expected_state = "INPUT_DATA"
    actual_state = metadata.get_dataset_state(TEST_PARQUET_FILEPATH)

    assert actual_state == expected_state
