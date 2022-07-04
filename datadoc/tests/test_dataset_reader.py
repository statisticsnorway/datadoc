import json
import random

from datadoc.Model import DataDocVariable, Datatype
from ..DatasetReader import (
    KNOWN_BOOLEAN_TYPES,
    KNOWN_DATETIME_TYPES,
    KNOWN_FLOAT_TYPES,
    KNOWN_INTEGER_TYPES,
    KNOWN_STRING_TYPES,
    DatasetReader,
)
from .utils import TEST_PARQUET_FILEPATH, TEST_SAS7BDAT_FILEPATH
from pytest import raises


def test_use_abstract_class_directly():
    with raises(TypeError):
        DatasetReader().get_fields()


def test_get_fields_parquet():
    expected_fields = [
        DataDocVariable(short_name="pers_id", datatype=Datatype.STRING),
        DataDocVariable(short_name="tidspunkt", datatype=Datatype.DATETIME),
        DataDocVariable(short_name="sivilstand", datatype=Datatype.STRING),
        DataDocVariable(short_name="alm_inntekt", datatype=Datatype.INTEGER),
        DataDocVariable(short_name="sykepenger", datatype=Datatype.INTEGER),
        DataDocVariable(short_name="ber_bruttoformue", datatype=Datatype.INTEGER),
        DataDocVariable(short_name="fullf_utdanning", datatype=Datatype.STRING),
        DataDocVariable(short_name="hoveddiagnose", datatype=Datatype.STRING),
    ]

    reader = DatasetReader.for_file(TEST_PARQUET_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


def test_get_fields_sas7bdat():
    expected_fields = [
        DataDocVariable(short_name="tekst", name="Tekst", datatype=Datatype.STRING),
        DataDocVariable(short_name="tall", name="Tall", datatype=Datatype.FLOAT),
        DataDocVariable(short_name="dato", name="Dato", datatype=Datatype.DATETIME),
    ]

    reader = DatasetReader.for_file(TEST_SAS7BDAT_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


def test_get_fields_unknown_file_type():
    with raises(NotImplementedError):
        DatasetReader.for_file("my_dataset.csv").get_fields()


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
