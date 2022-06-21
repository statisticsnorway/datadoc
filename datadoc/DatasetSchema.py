import pathlib
import pyarrow.parquet as pq
from typing import Optional
import pandas as pd


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
                field["name"] = str(data_field.name)
                field["datatype"] = self.transform_datatype(str(data_field.type))
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

                # Read the "column names" to get the variable name
                field["name"] = row.columns.values.tolist()[i]

                # Access the python type for the value and transform it to a DataDoc Datatype
                field["datatype"] = self.transform_datatype(type(v).__name__.lower())
                fields.append(field)

        elif self.dataset_file_type == "csv":
            raise NotImplementedError
        elif self.dataset_file_type == "json":
            raise NotImplementedError
        elif self.dataset_file_type == "xml":
            raise NotImplementedError
        return fields

    @staticmethod
    def transform_datatype(data_type) -> Optional[str]:
        v_data_type = data_type.lower()
        if v_data_type in (
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
        ):
            return "INTEGER"
        elif v_data_type in (
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
        ):
            return "FLOAT"
        elif v_data_type in (
            "string",
            "str",
            "char",
            "varchar",
            "varchar2",
            "text",
            "txt",
            "bytes",
        ):
            return "STRING"
        elif v_data_type in (
            "timestamp",
            "timestamp[us]",
            "timestamp[ns]",
            "datetime64",
            " datetime64[ns]",
            " datetime64[us]",
            "date",
            "datetime",
            "time",
        ):
            return "DATETIME"
        elif v_data_type in ("bool", "bool_", "boolean"):
            return "BOOLEAN"
        else:
            return None  # Unknown datatype?
