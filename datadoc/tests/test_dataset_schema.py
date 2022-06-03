from .. import DatasetSchema


def test_get_fields():
    expected_fields = [
        {"name": "pers_id", "datatype": "STRING"},
        {"name": "tidspunkt", "datatype": "DATETIME"},
        {"name": "sivilstand", "datatype": "STRING"},
        {"name": "alm_inntekt", "datatype": "INTEGER"},
        {"name": "sykepenger", "datatype": "INTEGER"},
        {"name": "ber_bruttoformue", "datatype": "INTEGER"},
        {"name": "fullf_utdanning", "datatype": "STRING"},
        {"name": "hoveddiagnose", "datatype": "STRING"},
    ]

    schema = DatasetSchema("datadoc/tests/resources/person_data_v1.parquet")
    fields = schema.get_fields()

    assert fields == expected_fields
