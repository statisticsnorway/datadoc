"""Verify that we are in sync with the Model."""

from datadoc_model.model import Dataset, Variable

from datadoc.frontend.fields.display_dataset import DISPLAY_DATASET, DatasetIdentifiers
from datadoc.frontend.fields.display_variables import (
    DISPLAY_VARIABLES,
    VariableIdentifiers,
)


def test_dataset_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert sorted([i.value for i in DatasetIdentifiers]) == sorted(
        Dataset().model_dump().keys(),
    )
    assert sorted(DatasetIdentifiers) == sorted(DISPLAY_DATASET.keys())


def test_variables_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    assert sorted([i.value for i in VariableIdentifiers]) == sorted(
        Variable().model_dump().keys(),
    )
    assert sorted(VariableIdentifiers) == sorted(DISPLAY_VARIABLES.keys())
