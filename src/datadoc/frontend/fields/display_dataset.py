"""Functionality for displaying dataset metadata."""

from __future__ import annotations

import functools
import logging
from enum import Enum
from typing import TYPE_CHECKING

from dash import dcc

from datadoc import enums
from datadoc import state
from datadoc.frontend.callbacks.utils import get_language_strings_enum
from datadoc.frontend.fields.display_base import INPUT_KWARGS
from datadoc.frontend.fields.display_base import DisplayDatasetMetadata
from datadoc.frontend.fields.display_base import DisplayDatasetMetadataDropdown
from datadoc.frontend.fields.display_base import get_comma_separated_string
from datadoc.frontend.fields.display_base import get_metadata_and_stringify
from datadoc.frontend.fields.display_base import get_multi_language_metadata

if TYPE_CHECKING:
    from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)


def get_enum_options_for_language(
    enum: Enum,
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    return [
        {
            "label": i.get_value_for_language(language),
            "value": i.name,
        }
        for i in get_language_strings_enum(enum)  # type: ignore [attr-defined]
    ]


def get_statistical_subject_options(
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Collect the statistical subject options for the given language."""
    return [
        {
            "label": f"{primary.get_title(language)} - {secondary.get_title(language)}",
            "value": secondary.subject_code,
        }
        for primary in state.statistic_subject_mapping.primary_subjects
        for secondary in primary.secondary_subjects
    ]


def get_unit_type_options(
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Collect the unit type options for the given language."""
    return [
        {
            "label": unit_type.get_title(language),
            "value": unit_type.code,
        }
        for unit_type in state.unit_types.classifications
    ]


def get_owner_options(
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Collect the owner options for the given language."""
    return [
        {
            "label": f"{option.code} - {option.get_title(language)}",
            "value": option.code,
        }
        for option in state.organisational_units.classifications
    ]


class DatasetIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/l/c/aoSfEWJU."""

    SHORT_NAME = "short_name"
    ASSESSMENT = "assessment"
    DATASET_STATUS = "dataset_status"
    DATASET_STATE = "dataset_state"
    NAME = "name"
    DESCRIPTION = "description"
    DATA_SOURCE = "data_source"
    REGISTER_URI = "register_uri"
    POPULATION_DESCRIPTION = "population_description"
    VERSION = "version"
    VERSION_DESCRIPTION = "version_description"
    UNIT_TYPE = "unit_type"
    TEMPORALITY_TYPE = "temporality_type"
    SUBJECT_FIELD = "subject_field"
    KEYWORD = "keyword"
    SPATIAL_COVERAGE_DESCRIPTION = "spatial_coverage_description"
    ID = "id"
    OWNER = "owner"
    FILE_PATH = "file_path"
    METADATA_CREATED_DATE = "metadata_created_date"
    METADATA_CREATED_BY = "metadata_created_by"
    METADATA_LAST_UPDATED_DATE = "metadata_last_updated_date"
    METADATA_LAST_UPDATED_BY = "metadata_last_updated_by"
    CONTAINS_DATA_FROM = "contains_data_from"
    CONTAINS_DATA_UNTIL = "contains_data_until"


DISPLAY_DATASET: dict[DatasetIdentifiers, DisplayDatasetMetadata] = {
    DatasetIdentifiers.SHORT_NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Navn på (fysisk) datafil, datatabell eller datasett",
        component=dcc.Input,
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ASSESSMENT: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurdering (sensitivitetsklassifisering) for datasettet.",
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.Assessment,
        ),
    ),
    DatasetIdentifiers.DATASET_STATUS: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Status",
        description="Livssyklus for datasettet",
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.DataSetStatus,
        ),
        obligatory=True,
    ),
    DatasetIdentifiers.DATASET_STATE: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.DataSetState,
        ),
    ),
    DatasetIdentifiers.NAME: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Navn",
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
    DatasetIdentifiers.REGISTER_URI: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.REGISTER_URI.value,
        display_name="Register URI",
        description="Lenke (URI) til register i registeroversikt (oversikt over alle registre meldt Datatilsynet (oppdatering foretas av sikkerhetsrådgiver))",
        multiple_language_support=True,
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjon",
        description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
        obligatory=True,
        multiple_language_support=True,
    ),
    DatasetIdentifiers.VERSION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Versjon",
        extra_kwargs=dict(type="number", min=1, **INPUT_KWARGS),
        obligatory=True,
    ),
    DatasetIdentifiers.VERSION_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.VERSION_DESCRIPTION.value,
        display_name="Versjonsbeskrivelse",
        description="Årsak/grunnlag for denne versjonen av datasettet i form av beskrivende tekst.",
        multiple_language_support=True,
        obligatory=True,
    ),
    DatasetIdentifiers.UNIT_TYPE: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Primær enhetstype for datafil, datatabell eller datasett. Se  Vi jobber med en avklaring av behov for flere enhetstyper her.",
        multiple_language_support=False,
        options_getter=get_unit_type_options,
        obligatory=True,
    ),
    DatasetIdentifiers.TEMPORALITY_TYPE: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.TemporalityTypeType,
        ),
        obligatory=True,
    ),
    DatasetIdentifiers.DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
        multiple_language_support=True,
        obligatory=True,
    ),
    DatasetIdentifiers.SUBJECT_FIELD: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Primær statistikkområdet som datasettet inngår i",
        obligatory=True,
        # TODO @mmwinther: Remove multiple_language_support once the model is updated.
        # https://github.com/statisticsnorway/ssb-datadoc-model/issues/41
        multiple_language_support=True,
        options_getter=get_statistical_subject_options,
    ),
    DatasetIdentifiers.KEYWORD: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.KEYWORD.value,
        display_name="Nøkkelord",
        description="En kommaseparert liste med søkbare nøkkelord som kan bidra til utvikling av effektive filtrerings- og søketjeneste.",
        value_getter=get_comma_separated_string,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografisk dekningsområde",
        description="Beskrivelse av datasettets geografiske dekningsområde. Målet er på sikt at dette skal hentes fra Klass, men fritekst vil også kunne brukes.",
        multiple_language_support=True,
    ),
    DatasetIdentifiers.ID: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.ID.value,
        display_name="ID",
        description="Unik SSB-identifikator for datasettet (løpenummer)",
        obligatory=True,
        editable=False,
        value_getter=get_metadata_and_stringify,
    ),
    DatasetIdentifiers.OWNER: DisplayDatasetMetadataDropdown(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Maskingenerert seksjonstilhørighet til den som oppretter metadata om datasettet, men kan korrigeres manuelt",
        obligatory=True,
        editable=True,
        multiple_language_support=False,
        options_getter=get_owner_options,
    ),
    DatasetIdentifiers.FILE_PATH: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.FILE_PATH.value,
        display_name="Filsti",
        description="Filstien inneholder datasettets navn og stien til hvor det er lagret.",
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
    DatasetIdentifiers.CONTAINS_DATA_FROM: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
    ),
    DatasetIdentifiers.CONTAINS_DATA_UNTIL: DisplayDatasetMetadata(
        identifier=DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
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
DISPLAYED_DATASET_METADATA: list[DisplayDatasetMetadata] = (
    OBLIGATORY_EDITABLE_DATASET_METADATA
    + OPTIONAL_DATASET_METADATA
    + NON_EDITABLE_DATASET_METADATA
)

DISPLAYED_DROPDOWN_DATASET_METADATA: list[DisplayDatasetMetadataDropdown] = [
    m
    for m in DISPLAYED_DATASET_METADATA
    if isinstance(m, DisplayDatasetMetadataDropdown)
]

OBLIGATORY_DATASET_METADATA_IDENTIFIERS: list[str] = [
    m.identifier for m in DISPLAY_DATASET.values() if m.obligatory and m.editable
]
