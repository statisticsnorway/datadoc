"""Functionality for displaying dataset metadata."""

from __future__ import annotations

import functools
import logging
from enum import Enum

from datadoc import enums
from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import DATASET_METADATA_MULTILANGUAGE_INPUT
from datadoc.frontend.fields.display_base import FieldTypes
from datadoc.frontend.fields.display_base import MetadataCheckboxField
from datadoc.frontend.fields.display_base import MetadataDropdownField
from datadoc.frontend.fields.display_base import MetadataInputField
from datadoc.frontend.fields.display_base import MetadataMultiLanguageField
from datadoc.frontend.fields.display_base import MetadataPeriodField
from datadoc.frontend.fields.display_base import get_comma_separated_string
from datadoc.frontend.fields.display_base import get_data_source_options
from datadoc.frontend.fields.display_base import get_enum_options

logger = logging.getLogger(__name__)


def get_statistical_subject_options() -> list[dict[str, str]]:
    """Generate the list of options for statistical subject."""
    dropdown_options = [
        {
            "title": f"{primary.get_title(SupportedLanguages.NORSK_BOKMÅL)} - {secondary.get_title(SupportedLanguages.NORSK_BOKMÅL)}",
            "id": secondary.subject_code,
        }
        for primary in state.statistic_subject_mapping.primary_subjects
        for secondary in primary.secondary_subjects
    ]
    dropdown_options.insert(0, {"title": "", "id": ""})
    return dropdown_options


def get_unit_type_options() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": unit_type.get_title(SupportedLanguages.NORSK_BOKMÅL),
            "id": unit_type.code,
        }
        for unit_type in state.unit_types.classifications
    ]
    dropdown_options.insert(0, {"title": "", "id": ""})
    return dropdown_options


def get_owner_options() -> list[dict[str, str]]:
    """Collect the owner options."""
    dropdown_options = [
        {
            "title": f"{option.code} - {option.get_title(SupportedLanguages.NORSK_BOKMÅL)}",
            "id": option.code,
        }
        for option in state.organisational_units.classifications
    ]
    dropdown_options.insert(0, {"title": "", "id": ""})
    return dropdown_options


class DatasetIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/l/c/aoSfEWJU."""

    SHORT_NAME = "short_name"
    ASSESSMENT = "assessment"
    DATASET_STATUS = "dataset_status"
    DATASET_STATE = "dataset_state"
    NAME = "name"
    DESCRIPTION = "description"
    DATA_SOURCE = "data_source"
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
    USE_RESTRICTION = "use_restriction"
    USE_RESTRICTION_DATE = "use_restriction_date"
    CONTAINS_PERSONAL_DATA = "contains_personal_data"


DISPLAY_DATASET: dict[
    DatasetIdentifiers,
    FieldTypes,
] = {
    DatasetIdentifiers.SHORT_NAME: MetadataInputField(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Navn på (fysisk) datafil, datatabell eller datasett",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ASSESSMENT: MetadataDropdownField(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurdering (sensitivitetsklassifisering) for datasettet.",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            enums.Assessment,
        ),
    ),
    DatasetIdentifiers.DATASET_STATUS: MetadataDropdownField(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Status",
        description="Livssyklus for datasettet",
        options_getter=functools.partial(
            get_enum_options,
            enums.DataSetStatus,
        ),
        obligatory=True,
    ),
    DatasetIdentifiers.DATASET_STATE: MetadataDropdownField(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            enums.DataSetState,
        ),
    ),
    DatasetIdentifiers.NAME: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Navn",
        description="Datasettnavn",
        obligatory=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
        obligatory=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.DATA_SOURCE: MetadataDropdownField(
        identifier=DatasetIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes enten for datasettet eller variabelforekomst.",
        obligatory=True,
        options_getter=get_data_source_options,
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjon",
        description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
        obligatory=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.VERSION: MetadataInputField(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Versjon",
        obligatory=True,
        type="number",
    ),
    DatasetIdentifiers.VERSION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.VERSION_DESCRIPTION.value,
        display_name="Versjonsbeskrivelse",
        description="Årsak/grunnlag for denne versjonen av datasettet i form av beskrivende tekst.",
        obligatory=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.UNIT_TYPE: MetadataDropdownField(
        identifier=DatasetIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Primær enhetstype for datafil, datatabell eller datasett. Se  Vi jobber med en avklaring av behov for flere enhetstyper her.",
        options_getter=get_unit_type_options,
        obligatory=True,
    ),
    DatasetIdentifiers.TEMPORALITY_TYPE: MetadataDropdownField(
        identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        options_getter=functools.partial(
            get_enum_options,
            enums.TemporalityTypeType,
        ),
        obligatory=True,
    ),
    DatasetIdentifiers.SUBJECT_FIELD: MetadataDropdownField(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Primær statistikkområdet som datasettet inngår i",
        obligatory=True,
        options_getter=get_statistical_subject_options,
    ),
    DatasetIdentifiers.KEYWORD: MetadataInputField(
        identifier=DatasetIdentifiers.KEYWORD.value,
        display_name="Nøkkelord",
        description="En kommaseparert liste med søkbare nøkkelord som kan bidra til utvikling av effektive filtrerings- og søketjeneste.",
        value_getter=get_comma_separated_string,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografisk dekningsområde",
        description="Beskrivelse av datasettets geografiske dekningsområde. Målet er på sikt at dette skal hentes fra Klass, men fritekst vil også kunne brukes.",
        obligatory=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.ID: MetadataInputField(
        identifier=DatasetIdentifiers.ID.value,
        display_name="ID",
        description="Unik SSB-identifikator for datasettet (løpenummer)",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.OWNER: MetadataDropdownField(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Maskingenerert seksjonstilhørighet til den som oppretter metadata om datasettet, men kan korrigeres manuelt",
        obligatory=True,
        editable=True,
        options_getter=get_owner_options,
    ),
    DatasetIdentifiers.FILE_PATH: MetadataInputField(
        identifier=DatasetIdentifiers.FILE_PATH.value,
        display_name="Filsti",
        description="Filstien inneholder datasettets navn og stien til hvor det er lagret.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_DATE: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_CREATED_DATE.value,
        display_name="Dato opprettet",
        description="Opprettet dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_BY: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_CREATED_BY.value,
        display_name="Opprettet av",
        description="Opprettet av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_DATE: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_DATE.value,
        display_name="Dato oppdatert",
        description="Sist oppdatert dato for metadata om datasettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_BY: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_BY.value,
        display_name="Oppdatert av",
        description="Siste endring utført av person. Kun til bruk i SSB.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.CONTAINS_DATA_FROM: MetadataPeriodField(
        identifier=DatasetIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_DATE_INPUT,
    ),
    DatasetIdentifiers.CONTAINS_DATA_UNTIL: MetadataPeriodField(
        identifier=DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_DATE_INPUT,
    ),
    DatasetIdentifiers.USE_RESTRICTION: MetadataDropdownField(
        identifier=DatasetIdentifiers.USE_RESTRICTION.value,
        display_name="Bruksrestriksjon",
        options_getter=functools.partial(
            get_enum_options,
            enums.UseRestriction,
        ),
        description="",
    ),
    DatasetIdentifiers.USE_RESTRICTION_DATE: MetadataPeriodField(
        identifier=DatasetIdentifiers.USE_RESTRICTION_DATE.value,
        display_name="Bruksrestriksjonsdato",
        description="",
    ),
    DatasetIdentifiers.CONTAINS_PERSONAL_DATA: MetadataCheckboxField(
        identifier=DatasetIdentifiers.CONTAINS_PERSONAL_DATA.value,
        display_name="Inneholder personopplysninger",
        description="",
        obligatory=True,
    ),
}

MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS = [
    m.identifier
    for m in DISPLAY_DATASET.values()
    if isinstance(m, MetadataMultiLanguageField)
]

OBLIGATORY_EDITABLE_DATASET_METADATA = [
    m for m in DISPLAY_DATASET.values() if m.obligatory and m.editable
]

OPTIONAL_DATASET_METADATA = [
    m for m in DISPLAY_DATASET.values() if not m.obligatory and m.editable
]

NON_EDITABLE_DATASET_METADATA = [m for m in DISPLAY_DATASET.values() if not m.editable]


# The order of this list MUST match the order of display components, as defined in DatasetTab.py
DISPLAYED_DATASET_METADATA: list[FieldTypes] = (
    OBLIGATORY_EDITABLE_DATASET_METADATA
    + OPTIONAL_DATASET_METADATA
    + NON_EDITABLE_DATASET_METADATA
)

DROPDOWN_DATASET_METADATA: list[MetadataDropdownField] = [
    m for m in DISPLAYED_DATASET_METADATA if isinstance(m, MetadataDropdownField)
]
DROPDOWN_DATASET_METADATA_IDENTIFIERS: list[str] = [
    m.identifier for m in DROPDOWN_DATASET_METADATA
]

OBLIGATORY_DATASET_METADATA_IDENTIFIERS: list[str] = [
    m.identifier for m in DISPLAY_DATASET.values() if m.obligatory and m.editable
]

OBLIGATORY_DATASET_METADATA_IDENTIFIERS_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name)
    for m in DISPLAY_DATASET.values()
    if m.obligatory and m.editable
]
