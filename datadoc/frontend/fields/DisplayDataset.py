import logging
from enum import Enum
from typing import Dict, List

from dash import dcc
from datadoc.frontend.fields.DisplayBase import (
    DROPDOWN_KWARGS,
    NUMBER_KWARGS,
    DisplayDatasetMetadata,
    get_multi_language_metadata,
)
from datadoc_model import Model

logger = logging.getLogger(__name__)


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


DISPLAY_DATASET: Dict[DatasetIdentifiers, DisplayDatasetMetadata] = {
    DatasetIdentifiers.SHORT_NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Navn på (fysisk) datafil, datatabell eller datasett",
        component=dcc.Input,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ASSESSMENT: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurdering (sensitivitetsklassifisering) for datasettet.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
    ),
    DatasetIdentifiers.DATASET_STATUS: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Livssyklus",
        description="Livssyklus for datasettet",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
    ),
    DatasetIdentifiers.DATASET_STATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
        obligatory=True,
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
    ),
    DatasetIdentifiers.NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Datasettnavn",
        description="Datasettnavn",
        obligatory=True,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.DATA_SOURCE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes enten for datasettet eller variabelforekomst.",
        obligatory=True,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonsbeskrivelsen",
        description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
        obligatory=True,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.VERSION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Versjon",
        extra_kwargs=NUMBER_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.UNIT_TYPE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Primær enhetstype for datafil, datatabell eller datasett. Se  Vi jobber med en avklaring av behov for flere enhetstyper her.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
    ),
    DatasetIdentifiers.TEMPORALITY_TYPE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
    ),
    DatasetIdentifiers.DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
        multiple_language_support=True,
    ),
    DatasetIdentifiers.SUBJECT_FIELD: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Primær statistikkområdet som datasettet inngår i",
        obligatory=True,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografiskedekningsområde",
        description="Beskrivelse av datasettets geografiske dekningsområde. Målet er på sikt at dette skal hentes fra Klass, men fritekst vil også kunne brukes.",
        multiple_language_support=True,
    ),
    DatasetIdentifiers.ID: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.ID.value,
        display_name="Unik ID",
        description="Unik SSB-identifikator for datasettet (løpenummer)",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.OWNER: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Maskingenerert seksjonstilhørighet til den som oppretter metadata om datasettet, men kan korrigeres manuelt",
        obligatory=True,
        editable=False,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.DATA_SOURCE_PATH: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE_PATH.value,
        display_name="Datasettsti",
        description="Fysisk fil-sti (plassering) av datasett",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_DATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_DATE.value,
        display_name="Dato opprettet",
        description="Opprettet dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_BY: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_BY.value,
        display_name="Opprettet av",
        description="Opprettet av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_DATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_DATE.value,
        display_name="Dato oppdatert",
        description="Sist oppdatert dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_BY: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_BY.value,
        display_name="Oppdatert av",
        description="Siste endring utført av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
}

for v in DISPLAY_DATASET.values():
    if v.multiple_language_support:
        v.value_getter = get_multi_language_metadata

MULTIPLE_LANGUAGE_DATASET_METADATA = [
    m.identifier for m in DISPLAY_DATASET.values() if m.multiple_language_support
]

OBLIGATORY_EDITABLE_DATASET_METADATA = [
    m for m in DISPLAY_DATASET.values() if m.obligatory and m.editable
]

OPTIONAL_DATASET_METADATA = [
    m for m in DISPLAY_DATASET.values() if not m.obligatory and m.editable
]

NON_EDITABLE_DATASET_METADATA = [m for m in DISPLAY_DATASET.values() if not m.editable]


# The order of this list MUST match the order of display components, as defined in DatasetTab.py
DISPLAYED_DATASET_METADATA: List[DisplayDatasetMetadata] = (
    OBLIGATORY_EDITABLE_DATASET_METADATA
    + OPTIONAL_DATASET_METADATA
    + NON_EDITABLE_DATASET_METADATA
)

DISPLAYED_DROPDOWN_DATASET_METADATA = [
    m for m in DISPLAYED_DATASET_METADATA if m.component == dcc.Dropdown
]

DISPLAYED_DROPDOWN_DATASET_ENUMS = [
    Model.DataDocDataSet.__fields__[m.identifier].type_
    for m in DISPLAYED_DROPDOWN_DATASET_METADATA
]
