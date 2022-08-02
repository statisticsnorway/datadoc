from datadoc_model import Enums
from datadoc.frontend.DisplayDataset import DISPLAY_DATASET, DatasetIdentifiers
from datadoc.frontend.DisplayVariables import DISPLAY_VARIABLES, VariableIdentifiers
from datadoc_model.Model import (
    DataDocDataSet,
    DataDocVariable,
    MetadataDocument,
)


def test_metadata_document_percent_complete():
    dataset = DataDocDataSet(dataset_state=Enums.DatasetState.OUTPUT_DATA)
    variable_1 = DataDocVariable(data_type=Enums.Datatype.BOOLEAN)
    variable_2 = DataDocVariable(data_type=Enums.Datatype.INTEGER)
    document = MetadataDocument(
        percentage_complete=0,
        document_version=1,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )

    assert document.percent_complete == 11


def test_dataset_metadata_definition_parity():
    """The metadata fields are currently defined in two places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in DatasetIdentifiers] == list(DataDocDataSet().dict().keys())
    assert [i for i in DatasetIdentifiers] == list(DISPLAY_DATASET.keys())


def test_variables_metadata_definition_parity():
    """The metadata fields are currently defined in two places for technical reasons. We want these to always be exactly identical."""
    assert [i.value for i in VariableIdentifiers] == list(
        DataDocVariable().dict().keys()
    )
    assert [i for i in VariableIdentifiers] == list(DISPLAY_VARIABLES.keys())
