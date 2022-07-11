from enum import Enum
from datadoc.DisplayVariables import DisplayMetadata
from datadoc.Enums import Assessment, DatasetState, DatasetStatus, TemporalityType


class DatasetIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/l/c/aoSfEWJU"""

    SHORT_NAME = "short_name"
    ASSESSMENT = "assessment"
    DATASET_STATUS = "dataset_status"
    DATASET_STATE = "dataset_state"
    NAME = "name"
    DATA_SOURCE = "data_source"
    POPULATION_DESCRIPTION = "population_description"
    VERSION = "version"
    UNIT_TYPE = "unit_type"
    TEMPORALITY_TYPE = "temporality_type"
    DESCRIPTION = "description"
    SUBJECT_FIELD = "subject_field"
    SPATIAL_COVERAGE_DESCRIPTION = "spatial_coverage_description"
    ID = "id"
    OWNER = "owner"
    DATA_SOURCE_PATH = "data_source_path"
    METADATA_CREATED_DATE = "created_date"
    METADATA_CREATED_BY = "created_by"
    METADATA_LAST_UPDATED_DATE = "last_updated_date"
    METADATA_LAST_UPDATED_BY = "last_updated_by"


DISPLAY_DATASET = {
    DatasetIdentifiers.SHORT_NAME: DisplayMetadata(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Navn på (fysisk) datafil, datatabell eller datasett",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ASSESSMENT: DisplayMetadata(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurdering (sensitivitetsklassifisering) for datasettet.",
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in Assessment]},
    ),
    DatasetIdentifiers.DATASET_STATUS: DisplayMetadata(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Livssyklus",
        description="Livssyklus for datasettet",
        presentation="dropdown",
        options={
            "options": [{"label": i.name, "value": i.name} for i in DatasetStatus]
        },
    ),
    DatasetIdentifiers.DATASET_STATE: DisplayMetadata(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
        obligatory=True,
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in DatasetState]},
    ),
    DatasetIdentifiers.NAME: DisplayMetadata(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Datasettnavn",
        description="Datasettnavn",
        obligatory=True,
    ),
    DatasetIdentifiers.DATA_SOURCE: DisplayMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes enten for datasettet eller variabelforekomst.",
        obligatory=True,
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: DisplayMetadata(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonsbeskrivelsen",
        description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
        obligatory=True,
    ),
    DatasetIdentifiers.VERSION: DisplayMetadata(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Versjon",
        presentation="number",
        obligatory=True,
    ),
    DatasetIdentifiers.UNIT_TYPE: DisplayMetadata(
        identifier=DatasetIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Primær enhetstype for datafil, datatabell eller datasett. Se  Vi jobber med en avklaring av behov for flere enhetstyper her.",
    ),
    DatasetIdentifiers.TEMPORALITY_TYPE: DisplayMetadata(
        identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        presentation="dropdown",
        options={
            "options": [{"label": i.name, "value": i.name} for i in TemporalityType]
        },
    ),
    DatasetIdentifiers.DESCRIPTION: DisplayMetadata(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
    ),
    DatasetIdentifiers.SUBJECT_FIELD: DisplayMetadata(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Primær statistikkområdet som datasettet inngår i",
        obligatory=True,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: DisplayMetadata(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografiskedekningsområde",
        description="Beskrivelse av datasettets geografiske dekningsområde. Målet er på sikt at dette skal hentes fra Klass, men fritekst vil også kunne brukes.",
    ),
    DatasetIdentifiers.ID: DisplayMetadata(
        identifier=DatasetIdentifiers.ID.value,
        display_name="Unik ID",
        description="Unik SSB-identifikator for datasettet (løpenummer)",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.OWNER: DisplayMetadata(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Maskingenerert seksjonstilhørighet til den som oppretter metadata om datasettet, men kan korrigeres manuelt",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.DATA_SOURCE_PATH: DisplayMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE_PATH.value,
        display_name="Datasettsti",
        description="Fysisk fil-sti (plassering) av datasett",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_DATE: DisplayMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_DATE.value,
        display_name="Dato opprettet",
        description="Opprettet dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_BY: DisplayMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_BY.value,
        display_name="Opprettet av",
        description="Opprettet av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_DATE: DisplayMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_DATE.value,
        display_name="Dato oppdatert",
        description="Sist oppdatert dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_BY: DisplayMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_BY.value,
        display_name="Oppdatert av",
        description="Siste endring utført av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
}

OBLIGATORY_DATASET_METADATA = [
    m.identifier for m in DISPLAY_DATASET.values() if m.obligatory
]
