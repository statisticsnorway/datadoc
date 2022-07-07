from datadoc import Enums
from datadoc.Model import (
    DataDocDataSet,
    DataDocVariable,
    MetadataDocument,
    calculate_percentage,
)


def test_metadata_document_percent_complete():
    dataset = DataDocDataSet(dataset_state=Enums.DatasetState.OUTPUT_DATA)
    variable_1 = DataDocVariable(datatype=Enums.Datatype.BOOLEAN)
    variable_2 = DataDocVariable(datatype=Enums.Datatype.INTEGER)
    document = MetadataDocument(
        percentage_complete=0,
        document_version=1,
        dataset=dataset,
        variables=[variable_1, variable_2],
    )

    assert document.percent_complete == 14
