"""Abstractions for dataset file formats.

Handles reading in the data and transforming data types to generic metadata types.
"""

from __future__ import annotations

import pathlib  # noqa: TCH003 import is needed for docs build
import re
import typing as t
from abc import ABC
from abc import abstractmethod

import pandas as pd
import pyarrow.parquet as pq
from datadoc_model.model import LanguageStringType
from datadoc_model.model import Variable

from datadoc import state
from datadoc.backend.storage_adapter import StorageAdapter
from datadoc.enums import DataType

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


TYPE_CORRESPONDENCE: list[tuple[tuple[str, ...], DataType]] = [
    (KNOWN_INTEGER_TYPES, DataType.INTEGER),
    (KNOWN_FLOAT_TYPES, DataType.FLOAT),
    (KNOWN_STRING_TYPES, DataType.STRING),
    (KNOWN_DATETIME_TYPES, DataType.DATETIME),
    (KNOWN_BOOLEAN_TYPES, DataType.BOOLEAN),
]
TYPE_MAP: dict[str, DataType] = {}
for concrete_type, abstract_type in TYPE_CORRESPONDENCE:
    TYPE_MAP.update({c: abstract_type for c in concrete_type})

TDatasetParser = t.TypeVar("TDatasetParser", bound="DatasetParser")


class DatasetParser(ABC):
    """Abstract Base Class for all Dataset parsers.

    Implements:
    - A static factory method to get the correct implementation for each file extension.
    - A static method for data type conversion.

    Requires implementation by subclasses:
    - A method to extract variables (columns) from the dataset, so they may be documented.
    """

    def __init__(self, dataset: pathlib.Path) -> None:
        """Initialize for a given dataset."""
        self.dataset: StorageAdapter = StorageAdapter.for_path(dataset)

    @staticmethod
    def for_file(dataset: pathlib.Path) -> DatasetParser:
        """Return the correct subclass based on the given dataset file."""
        supported_file_types: dict[
            str,
            type[DatasetParser],
        ] = {
            ".parquet": DatasetParserParquet,
            ".sas7bdat": DatasetParserSas7Bdat,
            ".parquet.gzip": DatasetParserParquet,
        }
        file_type = "Unknown"
        try:
            file_type = dataset.suffix
            # Gzipped parquet files can be read with DatasetParserParquet
            match = re.search(r"(.parquet.gzip)", str(dataset).lower())
            file_type = ".parquet.gzip" if match else file_type
            # Extract the appropriate reader class from the SUPPORTED_FILE_TYPES dict and return an instance of it
            reader = supported_file_types[file_type](dataset)
        except IndexError as e:
            # Thrown when just one element is returned from split, meaning there is no file extension supplied
            msg = f"Could not recognise file type for provided {dataset = }. Supported file types are: {', '.join(supported_file_types.keys())}"
            raise FileNotFoundError(
                msg,
            ) from e
        except KeyError as e:
            # In this case the file type is not supported, so we throw a helpful exception
            msg = f"{file_type = } is not supported. Please open one of the following supported files types: {', '.join(supported_file_types.keys())} or contact the maintainers to request support."
            raise NotImplementedError(
                msg,
            ) from e
        else:
            return reader

    @staticmethod
    def transform_data_type(data_type: str) -> DataType | None:
        """Transform a concrete data type to an abstract data type.

        In statistical metadata, one is not interested in how the data is
        technically stored, but in the meaning of the data type. Because of
        this, we transform known data types to their abstract metadata
        representations.

        If we encounter a data type we don't know, we just ignore it and let
        the user handle it in the GUI.
        """
        return TYPE_MAP.get(data_type.lower(), None)

    @abstractmethod
    def get_fields(self) -> list[Variable]:
        """Abstract method, must be implemented by subclasses."""


class DatasetParserParquet(DatasetParser):
    """Concrete implementation for parsing parquet files."""

    def __init__(self, dataset: pathlib.Path) -> None:
        """Use the super init method."""
        super().__init__(dataset)

    def get_fields(self) -> list[Variable]:
        """Extract the fields from this dataset."""
        with self.dataset.open(mode="rb") as f:
            data_table = pq.read_table(f)
        return [
            Variable(
                short_name=data_field.name,
                data_type=self.transform_data_type(str(data_field.type)),
            )
            for data_field in data_table.schema
        ]


class DatasetParserSas7Bdat(DatasetParser):
    """Concrete implementation for parsing SAS7BDAT files."""

    def __init__(self, dataset: pathlib.Path) -> None:
        """Use the super init method."""
        super().__init__(dataset)

    def get_fields(self) -> list[Variable]:
        """Extract the fields from this dataset."""
        fields = []
        with self.dataset.open(mode="rb") as f:
            # Use an iterator to avoid reading in the entire dataset
            sas_reader = pd.read_sas(f, format="sas7bdat", iterator=True)  # type: ignore [call-overload]

            # Get the first row from the iterator
            try:
                row = next(sas_reader)
            except StopIteration as e:
                msg = f"Could not read data from {self.dataset}"
                raise RuntimeError(msg) from e

        # Get all the values from the row and loop through them
        for i, v in enumerate(row.to_numpy().tolist()[0]):
            fields.append(
                Variable(
                    short_name=sas_reader.columns[i].name,
                    # Assume labels are defined in the default language (NORSK_BOKMÅL)
                    # If this is not correct, the user may fix it via the UI
                    name=LanguageStringType(
                        **{
                            state.current_metadata_language: sas_reader.columns[
                                i
                            ].label,
                        },
                    ),
                    # Access the python type for the value and transform it to a DataDoc Data type
                    data_type=self.transform_data_type(type(v).__name__.lower()),
                ),
            )

        return fields
