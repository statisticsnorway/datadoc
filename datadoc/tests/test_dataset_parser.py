"""Tests for the DatasetParser class."""

import pytest
from datadoc_model.Enums import Datatype, SupportedLanguages
from datadoc_model.Model import DataDocVariable, LanguageStrings

from datadoc import state
from datadoc.backend.dataset_parser import (
    KNOWN_BOOLEAN_TYPES,
    KNOWN_DATETIME_TYPES,
    KNOWN_FLOAT_TYPES,
    KNOWN_INTEGER_TYPES,
    KNOWN_STRING_TYPES,
    DatasetParser,
    DatasetParserParquet,
)

from .utils import (
    TEST_PARQUET_FILEPATH,
    TEST_PARQUET_GZIP_FILEPATH,
    TEST_SAS7BDAT_FILEPATH,
)


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
        DataDocVariable(short_name="pers_id", data_type=Datatype.STRING),
        DataDocVariable(short_name="tidspunkt", data_type=Datatype.DATETIME),
        DataDocVariable(short_name="sivilstand", data_type=Datatype.STRING),
        DataDocVariable(short_name="alm_inntekt", data_type=Datatype.INTEGER),
        DataDocVariable(short_name="sykepenger", data_type=Datatype.INTEGER),
        DataDocVariable(short_name="ber_bruttoformue", data_type=Datatype.INTEGER),
        DataDocVariable(short_name="fullf_utdanning", data_type=Datatype.STRING),
        DataDocVariable(short_name="hoveddiagnose", data_type=Datatype.STRING),
    ]
    fields = local_parser.get_fields()

    assert fields == expected_fields


def test_get_fields_sas7bdat():
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    expected_fields = [
        DataDocVariable(
            short_name="tekst",
            name=LanguageStrings(nb="Tekst"),
            data_type=Datatype.STRING,
        ),
        DataDocVariable(
            short_name="tall",
            name=LanguageStrings(nb="Tall"),
            data_type=Datatype.FLOAT,
        ),
        DataDocVariable(
            short_name="dato",
            name=LanguageStrings(nb="Dato"),
            data_type=Datatype.DATETIME,
        ),
    ]

    reader = DatasetParser.for_file(TEST_SAS7BDAT_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


def test_get_fields_unknown_file_type():
    with pytest.raises(NotImplementedError):
        DatasetParser.for_file("my_dataset.csv").get_fields()


def test_get_fields_no_extension_provided():
    with pytest.raises(NotImplementedError):
        DatasetParser.for_file("my_dataset").get_fields()


def test_transform_datatype_unknown_type():
    expected = None
    input_data = "definitely not a known data type"
    actual = DatasetParser.transform_data_type(input_data)
    assert actual == expected


@pytest.mark.parametrize(
    ("expected", "concrete_type"),
    [
        *[(Datatype.INTEGER, i) for i in KNOWN_INTEGER_TYPES],
        *[(Datatype.FLOAT, i) for i in KNOWN_FLOAT_TYPES],
        *[(Datatype.STRING, i) for i in KNOWN_STRING_TYPES],
        *[(Datatype.DATETIME, i) for i in KNOWN_DATETIME_TYPES],
        *[(Datatype.BOOLEAN, i) for i in KNOWN_BOOLEAN_TYPES],
    ],
)
def test_transform_datatype(expected: Datatype, concrete_type: str):
    actual = DatasetParser.transform_data_type(concrete_type)
    assert actual == expected
