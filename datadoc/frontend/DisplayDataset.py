from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type
from dash import dcc
from dash.development.base_component import Component
from datadoc.Enums import (
    Assessment,
    DatasetState,
    DatasetStatus,
    TemporalityType,
    UnitType,
)


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


INPUT_KWARGS = {
    "debounce": True,
    "style": {"width": "100%"},
    "className": "ssb-input",
}
DROPDOWN_KWARGS = {
    "style": {"width": "100%"},
    "className": "ssb-dropdown",
}


@dataclass
class DisplayDatasetMetadata:
    identifier: str
    display_name: str
    description: str
    extra_kwargs: Dict[str, Any]
    component: Type[Component] = dcc.Input
    options: Optional[Dict[str, List[Dict[str, str]]]] = None
    obligatory: bool = False
    presentation: Optional[str] = "input"
    editable: bool = True


DISPLAY_DATASET = {
    DatasetIdentifiers.SHORT_NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Navn på (fysisk) datafil, datatabell eller datasett",
        component=dcc.Input,
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ASSESSMENT: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurdering (sensitivitetsklassifisering) for datasettet.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
        options={"options": [{"label": i.name, "value": i.name} for i in Assessment]},
    ),
    DatasetIdentifiers.DATASET_STATUS: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Livssyklus",
        description="Livssyklus for datasettet",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
        options={
            "options": [{"label": i.name, "value": i.name} for i in DatasetStatus]
        },
    ),
    DatasetIdentifiers.DATASET_STATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
        obligatory=True,
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
        options={"options": [{"label": i.name, "value": i.name} for i in DatasetState]},
    ),
    DatasetIdentifiers.NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Datasettnavn",
        description="Datasettnavn",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.DATA_SOURCE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes enten for datasettet eller variabelforekomst.",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonsbeskrivelsen",
        description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.VERSION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Versjon",
        presentation="number",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.UNIT_TYPE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Primær enhetstype for datafil, datatabell eller datasett. Se  Vi jobber med en avklaring av behov for flere enhetstyper her.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
        options={"options": [{"label": i.name, "value": i.name} for i in UnitType]},
    ),
    DatasetIdentifiers.TEMPORALITY_TYPE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        component=dcc.Dropdown,
        extra_kwargs=DROPDOWN_KWARGS,
        options={
            "options": [{"label": i.name, "value": i.name} for i in TemporalityType]
        },
    ),
    DatasetIdentifiers.DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
        extra_kwargs=INPUT_KWARGS,
    ),
    DatasetIdentifiers.SUBJECT_FIELD: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Primær statistikkområdet som datasettet inngår i",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografiskedekningsområde",
        description="Beskrivelse av datasettets geografiske dekningsområde. Målet er på sikt at dette skal hentes fra Klass, men fritekst vil også kunne brukes.",
        extra_kwargs=INPUT_KWARGS,
    ),
    DatasetIdentifiers.ID: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.ID.value,
        display_name="Unik ID",
        description="Unik SSB-identifikator for datasettet (løpenummer)",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.OWNER: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Maskingenerert seksjonstilhørighet til den som oppretter metadata om datasettet, men kan korrigeres manuelt",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.DATA_SOURCE_PATH: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DATA_SOURCE_PATH.value,
        display_name="Datasettsti",
        description="Fysisk fil-sti (plassering) av datasett",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_DATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_DATE.value,
        display_name="Dato opprettet",
        description="Opprettet dato for metadata om datasettet",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_BY: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_CREATED_BY.value,
        display_name="Opprettet av",
        description="Opprettet av person. Kun til bruk i SSB.",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_DATE: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_DATE.value,
        display_name="Dato oppdatert",
        description="Sist oppdatert dato for metadata om datasettet",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_BY: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_BY.value,
        display_name="Oppdatert av",
        description="Siste endring utført av person. Kun til bruk i SSB.",
        extra_kwargs=INPUT_KWARGS,
        obligatory=True,
        editable=False,
    ),
}

OBLIGATORY_DATASET_METADATA = [
    m.identifier for m in DISPLAY_DATASET.values() if m.obligatory
]
