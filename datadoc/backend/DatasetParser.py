import pathlib
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar

import pandas as pd
import pyarrow.parquet as pq
from datadoc_model.Enums import Datatype
from datadoc_model.LanguageStrings import LanguageStrings
from datadoc_model.Model import DataDocVariable

from datadoc import state
from datadoc.backend.StorageAdapter import StorageAdapter

TDatasetParser = TypeVar("TDatasetParser", bound="DatasetParser")

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


class DatasetParser(ABC):
    def __init__(self, dataset: str):
        self.dataset: StorageAdapter = StorageAdapter.for_path(dataset)

    @staticmethod
    def for_file(dataset: str) -> TDatasetParser:
        """Factory method to return the correct subclass based on the given dataset file"""
        supported_file_types = {
            "parquet": DatasetParserParquet,
            "sas7bdat": DatasetParserSas7Bdat,
        }
        file_type = "Unknown"
        try:
            file_type = str(pathlib.Path(dataset)).lower().split(".")[-1]
            # Extract the appropriate reader class from the SUPPORTED_FILE_TYPES dict and return an instance of it
            reader = supported_file_types[file_type](dataset)
        except IndexError as e:
            # Thrown when just one element is returned from split, meaning there is no file extension supplied
            raise FileNotFoundError(
                f"Could not recognise file type for provided {dataset = }. Supported file types are: {', '.join(supported_file_types.keys())}"
            ) from e
        except KeyError as e:
            # In this case the file type is not supported, so we throw a helpful exception
            raise NotImplementedError(
                f"{file_type = } is not supported. Please open one of the following supported files types: {', '.join(supported_file_types.keys())} or contact the maintainers to request support."
            ) from e
        else:
            return reader

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
            # Unknown data type. There's no need to throw an exception here,
            # the user can still define the data type manually in the GUI
            return None

    @abstractmethod
    def get_fields(self) -> List[DataDocVariable]:
        """Abstract method, must be implemented by subclasses"""


class DatasetParserParquet(DatasetParser):
    def __init__(self, dataset: str):
        super().__init__(dataset)

    def get_fields(self) -> List[DataDocVariable]:
        fields = []
        with self.dataset.open(mode="rb") as f:
            data_table = pq.read_table(f)
            for data_field in data_table.schema:
                fields.append(
                    DataDocVariable(
                        short_name=data_field.name,
                        data_type=self.transform_data_type(str(data_field.type)),
                    )
                )
        return fields


class DatasetParserSas7Bdat(DatasetParser):
    def __init__(self, dataset: str):
        super().__init__(dataset)

    def get_fields(self) -> List[DataDocVariable]:
        fields = []
        with self.dataset.open(mode="rb") as f:
            # Use an iterator to avoid reading in the entire dataset
            sas_reader = pd.read_sas(f, format="sas7bdat", iterator=True)

            # Get the first row from the iterator
            row = next(sas_reader)

        # Get all the values from the row and loop through them
        for i, v in enumerate(row.values.tolist()[0]):
            fields.append(
                DataDocVariable(
                    short_name=sas_reader.columns[i].name,
                    # Assume labels are defined in the default language (NORSK_BOKMÅL)
                    # If this is not correct, the user may fix it via the UI
                    name=LanguageStrings(
                        **{state.current_metadata_language: sas_reader.columns[i].label}
                    ),
                    # Access the python type for the value and transform it to a DataDoc Data type
                    data_type=self.transform_data_type(type(v).__name__.lower()),
                )
            )

        return fields
