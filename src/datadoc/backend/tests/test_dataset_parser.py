"""Tests for the DatasetParser class."""

import io
import pathlib

import pandas as pd
import pytest
from datadoc_model.model import LanguageStringType
from datadoc_model.model import LanguageStringTypeItem
from datadoc_model.model import Variable

from datadoc.backend.src.dataset_parser import KNOWN_BOOLEAN_TYPES
from datadoc.backend.src.dataset_parser import KNOWN_DATETIME_TYPES
from datadoc.backend.src.dataset_parser import KNOWN_FLOAT_TYPES
from datadoc.backend.src.dataset_parser import KNOWN_INTEGER_TYPES
from datadoc.backend.src.dataset_parser import KNOWN_STRING_TYPES
from datadoc.backend.src.dataset_parser import DatasetParser
from datadoc.backend.src.dataset_parser import DatasetParserParquet
from datadoc.backend.src.utility.enums import DataType
from datadoc.backend.tests.constants import TEST_PARQUET_FILEPATH
from datadoc.backend.tests.constants import TEST_PARQUET_GZIP_FILEPATH
from datadoc.backend.tests.constants import TEST_SAS7BDAT_FILEPATH


def test_use_abstract_class_directly():
    with pytest.raises(TypeError):
        DatasetParser().get_fields()


@pytest.mark.parametrize(
    "local_parser",
    [
        DatasetParser.for_file(TEST_PARQUET_FILEPATH),
        DatasetParser.for_file(TEST_PARQUET_GZIP_FILEPATH),
    ],
)
def test_get_fields_parquet(local_parser: DatasetParserParquet):
    expected_fields = [
        Variable(short_name="pers_id", data_type=DataType.STRING),
        Variable(short_name="tidspunkt", data_type=DataType.DATETIME),
        Variable(short_name="sivilstand", data_type=DataType.STRING),
        Variable(short_name="alm_inntekt", data_type=DataType.INTEGER),
        Variable(short_name="sykepenger", data_type=DataType.INTEGER),
        Variable(short_name="ber_bruttoformue", data_type=DataType.INTEGER),
        Variable(short_name="fullf_utdanning", data_type=DataType.STRING),
        Variable(short_name="hoveddiagnose", data_type=DataType.STRING),
    ]
    fields = local_parser.get_fields()

    assert fields == expected_fields


def test_get_fields_sas7bdat():
    expected_fields = [
        Variable(
            short_name="tekst",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Tekst")],
            ),
            data_type=DataType.STRING,
        ),
        Variable(
            short_name="tall",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Tall")],
            ),
            data_type=DataType.FLOAT,
        ),
        Variable(
            short_name="dato",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Dato")],
            ),
            data_type=DataType.DATETIME,
        ),
    ]

    reader = DatasetParser.for_file(TEST_SAS7BDAT_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


@pytest.mark.parametrize("file", ["my_dataset.csv", "my_dataset.xlsx", "my_dataset"])
def test_dataset_parser_unsupported_files(file: pathlib.Path):
    with pytest.raises(NotImplementedError):
        DatasetParser.for_file(pathlib.Path(file))


def test_transform_datatype_unknown_type():
    assert DatasetParser.transform_data_type("definitely not a known data type") is None


@pytest.mark.parametrize(
    ("expected", "concrete_type"),
    [
        *[(DataType.INTEGER, i) for i in KNOWN_INTEGER_TYPES],
        *[(DataType.FLOAT, i) for i in KNOWN_FLOAT_TYPES],
        *[(DataType.STRING, i) for i in KNOWN_STRING_TYPES],
        *[(DataType.DATETIME, i) for i in KNOWN_DATETIME_TYPES],
        *[(DataType.BOOLEAN, i) for i in KNOWN_BOOLEAN_TYPES],
    ],
)
def test_transform_datatype(expected: DataType, concrete_type: str):
    actual = DatasetParser.transform_data_type(concrete_type)
    assert actual == expected


@pytest.fixture()
def parquet_with_index_column(tmp_path):
    """Create a parquet file with a column called __index_level_0__."""
    test_data = pd.read_csv(
        io.StringIO(
            """a	b
1	4
2	5
3	6
""",
        ),
        sep="\t",
    )

    output_path = tmp_path / "test_with_index.parquet"
    test_data.query("b % 2 == 0").to_parquet(output_path, engine="pyarrow")
    return output_path


def test_parquet_with_index_column(parquet_with_index_column: pathlib.Path):
    fields = DatasetParser.for_file(parquet_with_index_column).get_fields()
    assert not any(f.short_name == "__index_level_0__" for f in fields)
