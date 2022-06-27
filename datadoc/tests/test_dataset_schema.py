from .. import DatasetSchema
from .utils import TEST_PARQUET_FILEPATH, TEST_SAS7BDAT_FILEPATH


def test_get_fields_parquet():
    expected_fields = [
        {"shortName": "pers_id", "dataType": "STRING"},
        {"shortName": "tidspunkt", "dataType": "DATETIME"},
        {"shortName": "sivilstand", "dataType": "STRING"},
        {"shortName": "alm_inntekt", "dataType": "INTEGER"},
        {"shortName": "sykepenger", "dataType": "INTEGER"},
        {"shortName": "ber_bruttoformue", "dataType": "INTEGER"},
        {"shortName": "fullf_utdanning", "dataType": "STRING"},
        {"shortName": "hoveddiagnose", "dataType": "STRING"},
    ]

    schema = DatasetSchema(TEST_PARQUET_FILEPATH)
    fields = schema.get_fields()

    assert fields == expected_fields


def test_get_fields_sas7bdat():
    expected_fields = [
        {"shortName": "tekst", "name": "Tekst", "dataType": "STRING"},
        {"shortName": "tall", "name": "Tall", "dataType": "FLOAT"},
        {"shortName": "dato", "name": "Dato", "dataType": "DATETIME"},
    ]

    schema = DatasetSchema(TEST_SAS7BDAT_FILEPATH)
    fields = schema.get_fields()

    assert fields == expected_fields
