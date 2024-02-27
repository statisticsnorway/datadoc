"""Functionality for displaying new nvariables metadata."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING

import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc import state
from datadoc.frontend.callbacks.utils import get_language_strings_enum
from datadoc.frontend.fields.display_base import DisplayNewVariablesMetadata
from datadoc.frontend.fields.display_base import DisplayNewVariablesMetadataDropdown
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


class VariableIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst."""

    SHORT_NAME = "short_name"
    NAME = "name"
    DATA_TYPE = "data_type"
    VARIABLE_ROLE = "variable_role"
    DEFINITION_URI = "definition_uri"
    DIRECT_PERSON_IDENTIFYING = "direct_person_identifying"
    DATA_SOURCE = "data_source"
    POPULATION_DESCRIPTION = "population_description"
    COMMENT = "comment"
    TEMPORALITY_TYPE = "temporality_type"
    MEASUREMENT_UNIT = "measurement_unit"
    FORMAT = "format"
    CLASSIFICATION_URI = "classification_uri"
    SENTINEL_VALUE_URI = "sentinel_value_uri"
    INVALID_VALUE_DESCRIPTION = "invalid_value_description"
    IDENTIFIER = "id"
    CONTAINS_DATA_FROM = "contains_data_from"
    CONTAINS_DATA_UNTIL = "contains_data_until"


DISPLAY_VARIABLES: dict[VariableIdentifiers, DisplayNewVariablesMetadata] = {
    VariableIdentifiers.SHORT_NAME: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.NAME: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
        multiple_language_support=True,
        presentation="text",
        component=ssb.Input,
    ),
    VariableIdentifiers.DATA_TYPE: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        presentation="dropdown",
        component=ssb.Dropdown,
    ),
    VariableIdentifiers.VARIABLE_ROLE: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        presentation="dropdown",
        component=ssb.Dropdown,
    ),
    VariableIdentifiers.DEFINITION_URI: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        url=True,
        obligatory=True,
        presentation="url",
        component=ssb.Input,
    ),
    VariableIdentifiers.DIRECT_PERSON_IDENTIFYING: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="DPI",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
        presentation="dropdown",
        component=ssb.Dropdown,
    ),
    VariableIdentifiers.DATA_SOURCE: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.COMMENT: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
        multiple_language_support=True,
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Måleenhet. Eksempel: NOK eller USD for valuta, KG eller TONN for vekt. Se også forslag til SSBs måletyper/måleenheter.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.FORMAT: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering. Dette kan benyttes som en ytterligere presisering av datatypen (dataType) i de tilfellene hvor dette er relevant. ",
    ),
    VariableIdentifiers.CLASSIFICATION_URI: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS",
        url=True,
    ),
    VariableIdentifiers.SENTINEL_VALUE_URI: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.SENTINEL_VALUE_URI.value,
        display_name="Spesialverdienes URI",
        description="En lenke (URI) til en oversikt over 'spesialverdier' som inngår i variabelen.",
        url=True,
        presentation="url",
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="En beskrivelse av ugyldige verdier som inngår i variabelen dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.IDENTIFIER: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="Unik ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        obligatory=False,
        editable=False,
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelforekomsten i datasettet inneholder data fra og med denne dato.",
        presentation="date",
        component=ssb.Input,
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: DisplayNewVariablesMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelforekomsten i datasettet inneholder data til og med denne dato.",
        presentation="date",
        component=ssb.Input,
    ),
}


for v in DISPLAY_VARIABLES.values():
    if v.multiple_language_support:
        v.value_getter = get_multi_language_metadata

MULTIPLE_LANGUAGE_VARIABLES_METADATA = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.multiple_language_support
]

OBLIGATORY_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if m.obligatory and m.editable
]

OPTIONAL_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if not m.obligatory and m.editable
]

NON_EDITABLE_DATASET_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if not m.editable
]


# The order of this list MUST match the order of display components, as defined in DatasetTab.py
DISPLAYED_VARIABLES_METADATA: list[DisplayNewVariablesMetadata] = (
    OBLIGATORY_VARIABLES_METADATA + OPTIONAL_VARIABLES_METADATA
)

DISPLAYED_DROPDOWN_VARIABLES_METADATA: list[DisplayNewVariablesMetadataDropdown] = [
    m
    for m in DISPLAYED_VARIABLES_METADATA
    if isinstance(m, DisplayNewVariablesMetadataDropdown)
]

OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS: list[str] = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.obligatory and m.editable
]
