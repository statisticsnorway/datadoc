"""Verify that we are in sync with the Model."""

from datadoc_model.Model import DataDocDataSet, DataDocVariable

from datadoc.frontend.fields.display_dataset import DISPLAY_DATASET, DatasetIdentifiers
from datadoc.frontend.fields.display_variables import (
    DISPLAY_VARIABLES,
    VariableIdentifiers,
)


def test_dataset_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in DatasetIdentifiers] == list(DataDocDataSet().dict().keys())
    assert list(DatasetIdentifiers) == list(DISPLAY_DATASET.keys())


def test_variables_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in VariableIdentifiers] == list(
        DataDocVariable().dict().keys(),
    )
    assert list(VariableIdentifiers) == list(DISPLAY_VARIABLES.keys())
