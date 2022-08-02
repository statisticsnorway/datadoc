import pathlib
from abc import ABC, abstractmethod
import pyarrow.parquet as pq
from typing import List, Optional, TypeVar
import pandas as pd
from datadoc import state

from datadoc.Enums import Datatype
from datadoc.Model import DataDocVariable, LanguageStrings

TDatasetReader = TypeVar("TDatasetReader", bound="DatasetReader")

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


class DatasetReader(ABC):
    def __init__(self, dataset):
        self.dataset = dataset

    @staticmethod
    def for_file(dataset: str) -> TDatasetReader:
        """Factory method to return the correct subclass based on the given dataset file"""
        file_type = str(pathlib.Path(dataset)).lower().split(".")[1]
        if file_type == "parquet":
            return DatasetReaderParquet(dataset)
        if file_type == "sas7bdat":
            return DatasetReaderSas7bdat(dataset)
        else:
            # In the future we can potentially support csv, xml or json files
            raise NotImplementedError

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

    @abstractmethod
    def get_fields(self) -> List[DataDocVariable]:
        """Abstract method, must be implemented by subclasses"""
        pass


class DatasetReaderParquet(DatasetReader):
    def __init__(self, dataset):
        super().__init__(dataset)

    def get_fields(self) -> List[DataDocVariable]:
        fields = []
        data_table = pq.read_table(self.dataset)
        for data_field in data_table.schema:
            fields.append(
                DataDocVariable(
                    short_name=data_field.name,
                    data_type=self.transform_data_type(str(data_field.type)),
                )
            )
        return fields


class DatasetReaderSas7bdat(DatasetReader):
    def __init__(self, dataset):
        super().__init__(dataset)

    def get_fields(self) -> List[DataDocVariable]:
        fields = []
        # Use an iterator to avoid reading in the entire dataset
        sas_reader = pd.read_sas(self.dataset, iterator=True)

        # Get the first row from the iterator
        row = next(sas_reader)

        # Get all the values from the row and loop through them
        for i, v in enumerate(row.values.tolist()[0]):
            fields.append(
                DataDocVariable(
                    short_name=sas_reader.columns[i].name,
                    # Assume labels are defined in the default language (NORSK_BOKMÅL)
                    # If this is not correct, the user may fix it via the UI
                    name={state.current_metadata_language: sas_reader.columns[i].label},
                    # Access the python type for the value and transform it to a DataDoc Data type
                    data_type=self.transform_data_type(type(v).__name__.lower()),
                )
            )

        return fields
