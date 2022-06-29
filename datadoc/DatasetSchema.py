import pathlib
import pyarrow.parquet as pq
from typing import Optional
import pandas as pd

from datadoc.Model import Datatype

KNOWN_INTEGER_TYPES = (
    "int",
    "int_",
    "int8",
    "int16",
    "int32",
    "int64",
    "integer",
    "long",
    "uint",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
)

KNOWN_FLOAT_TYPES = (
    "double",
    "float",
    "float_",
    "float16",
    "float32",
    "float64",
    "decimal",
    "number",
    "numeric",
    "num",
)

KNOWN_STRING_TYPES = (
    "string",
    "str",
    "char",
    "varchar",
    "varchar2",
    "text",
    "txt",
    "bytes",
)

KNOWN_DATETIME_TYPES = (
    "timestamp",
    "timestamp[us]",
    "timestamp[ns]",
    "datetime64",
    " datetime64[ns]",
    " datetime64[us]",
    "date",
    "datetime",
    "time",
)

KNOWN_BOOLEAN_TYPES = ("bool", "bool_", "boolean")


class DatasetSchema:
    def __init__(self, dataset):
        self.dataset = dataset
        self.dataset_full_path = pathlib.Path(self.dataset)
        self.dataset_file_type = str(self.dataset_full_path.name).lower().split(".")[1]

    def get_fields(self):
        fields = []
        if self.dataset_file_type == "parquet":
            data_table = pq.read_table(self.dataset)
            for data_field in data_table.schema:
                field = {}
                field["shortName"] = str(data_field.name)
                field["dataType"] = self.transform_data_type(str(data_field.type))
                fields.append(field)

        # SAS Data files
        elif self.dataset_file_type == "sas7bdat":
            # Use an iterator to avoid reading in the entire dataset
            sas_reader = pd.read_sas(self.dataset, iterator=True)

            # Get the first row from the iterator
            row = next(sas_reader)

            # Get all the values from the row and loop through them
            for i, v in enumerate(row.values.tolist()[0]):
                field = {}
                field["shortName"] = sas_reader.columns[i].name
                field["name"] = sas_reader.columns[i].label
                # Access the python type for the value and transform it to a DataDoc Data type
                field["dataType"] = self.transform_data_type(type(v).__name__.lower())
                fields.append(field)

        elif self.dataset_file_type == "csv":
            raise NotImplementedError
        elif self.dataset_file_type == "json":
            raise NotImplementedError
        elif self.dataset_file_type == "xml":
            raise NotImplementedError
        return fields

    @staticmethod
    def transform_data_type(data_type: str) -> Optional[Datatype]:
        v_data_type = data_type.lower()
        if v_data_type in KNOWN_INTEGER_TYPES:
            return Datatype.INTEGER
        elif v_data_type in KNOWN_FLOAT_TYPES:
            return Datatype.FLOAT
        elif v_data_type in KNOWN_STRING_TYPES:
            return Datatype.STRING
        elif v_data_type in KNOWN_DATETIME_TYPES:
            return Datatype.DATETIME
        elif v_data_type in KNOWN_BOOLEAN_TYPES:
            return Datatype.BOOLEAN
        else:
            return None  # Unknown datatype?
