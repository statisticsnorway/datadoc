from datadoc_model import Enums
from datadoc.frontend.DisplayDataset import DISPLAY_DATASET, DatasetIdentifiers
from datadoc.frontend.DisplayVariables import DISPLAY_VARIABLES, VariableIdentifiers
from datadoc_model.Model import (
    DataDocDataSet,
    DataDocVariable,
)


def test_dataset_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in DatasetIdentifiers] == list(DataDocDataSet().dict().keys())
    assert [i for i in DatasetIdentifiers] == list(DISPLAY_DATASET.keys())


def test_variables_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in VariableIdentifiers] == list(
        DataDocVariable().dict().keys()
    )
    assert [i for i in VariableIdentifiers] == list(DISPLAY_VARIABLES.keys())
