import random

from datadoc import state
from datadoc.backend.DatasetReader import (
    KNOWN_BOOLEAN_TYPES,
    KNOWN_DATETIME_TYPES,
    KNOWN_FLOAT_TYPES,
    KNOWN_INTEGER_TYPES,
    KNOWN_STRING_TYPES,
    DatasetReader,
)
from datadoc_model.Enums import Datatype, SupportedLanguages
from datadoc_model.Model import DataDocVariable, LanguageStrings
from pytest import raises

from .utils import TEST_PARQUET_FILEPATH, TEST_SAS7BDAT_FILEPATH


def test_use_abstract_class_directly():
    with raises(TypeError):
        DatasetReader().get_fields()


def test_get_fields_parquet():
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

    reader = DatasetReader.for_file(TEST_PARQUET_FILEPATH)
    fields = reader.get_fields()

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
            short_name="tall", name=LanguageStrings(nb="Tall"), data_type=Datatype.FLOAT
        ),
        DataDocVariable(
            short_name="dato",
            name=LanguageStrings(nb="Dato"),
            data_type=Datatype.DATETIME,
        ),
    ]

    reader = DatasetReader.for_file(TEST_SAS7BDAT_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


def test_get_fields_unknown_file_type():
    with raises(NotImplementedError):
        DatasetReader.for_file("my_dataset.csv").get_fields()


def test_get_fields_no_extension_provided():
    with raises(FileNotFoundError):
        DatasetReader.for_file("my_dataset").get_fields()


def test_transform_datatype_unknown_type():
    expected = None
    input_data = "definitely not a known data type"
    actual = DatasetReader.transform_data_type(input_data)
    assert actual == expected


def test_transform_datatype():
    for expected, input_options in [
        (Datatype.INTEGER, KNOWN_INTEGER_TYPES),
        (Datatype.FLOAT, KNOWN_FLOAT_TYPES),
        (Datatype.STRING, KNOWN_STRING_TYPES),
        (Datatype.DATETIME, KNOWN_DATETIME_TYPES),
        (Datatype.BOOLEAN, KNOWN_BOOLEAN_TYPES),
    ]:
        input_data = random.choice(input_options)
        actual = DatasetReader.transform_data_type(input_data)
        assert actual == expected
