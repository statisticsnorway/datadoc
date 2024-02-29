"""Functionality for displaying new nvariables metadata."""

from __future__ import annotations

import functools
import logging
from enum import Enum
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc import enums
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
            "title": i.get_value_for_language(language),
            "id": i.name,
        }
        for i in get_language_strings_enum(enum)  # type: ignore [attr-defined]
    ]


class NewVariableIdentifiers(str, Enum):
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


DISPLAY_VARIABLES: dict[NewVariableIdentifiers, DisplayNewVariablesMetadata] = {
    NewVariableIdentifiers.SHORT_NAME: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    NewVariableIdentifiers.NAME: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
        multiple_language_support=True,
        presentation="text",
        component=ssb.Input,
    ),
    NewVariableIdentifiers.DATA_TYPE: DisplayNewVariablesMetadataDropdown(
        identifier=NewVariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        presentation="dropdown",
        component=ssb.Dropdown,
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.DataType,
        ),
    ),
    NewVariableIdentifiers.VARIABLE_ROLE: DisplayNewVariablesMetadataDropdown(
        identifier=NewVariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        presentation="dropdown",
        component=ssb.Dropdown,
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.VariableRole,
        ),
    ),
    NewVariableIdentifiers.DEFINITION_URI: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        url=True,
        obligatory=True,
        presentation="url",
        component=ssb.Input,
    ),
    NewVariableIdentifiers.DIRECT_PERSON_IDENTIFYING: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="DPI",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
        component=dbc.Checkbox,
        extra_kwargs={
            "label": "Direkte Personidentifiserende Informasjon",
            "label_class_name": "ssb-checkbox checkbox-label",
            "class_name": "ssb-checkbox",
        },
    ),
    NewVariableIdentifiers.DATA_SOURCE: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    NewVariableIdentifiers.POPULATION_DESCRIPTION: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    NewVariableIdentifiers.COMMENT: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
        multiple_language_support=True,
    ),
    NewVariableIdentifiers.MEASUREMENT_UNIT: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Måleenhet. Eksempel: NOK eller USD for valuta, KG eller TONN for vekt. Se også forslag til SSBs måletyper/måleenheter.",
        multiple_language_support=True,
    ),
    NewVariableIdentifiers.FORMAT: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering. Dette kan benyttes som en ytterligere presisering av datatypen (dataType) i de tilfellene hvor dette er relevant. ",
    ),
    NewVariableIdentifiers.CLASSIFICATION_URI: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS",
        url=True,
    ),
    NewVariableIdentifiers.SENTINEL_VALUE_URI: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.SENTINEL_VALUE_URI.value,
        display_name="Spesialverdienes URI",
        description="En lenke (URI) til en oversikt over 'spesialverdier' som inngår i variabelen.",
        url=True,
        presentation="url",
    ),
    NewVariableIdentifiers.INVALID_VALUE_DESCRIPTION: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="En beskrivelse av ugyldige verdier som inngår i variabelen dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        multiple_language_support=True,
    ),
    NewVariableIdentifiers.IDENTIFIER: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.IDENTIFIER.value,
        display_name="Unik ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        obligatory=False,
        editable=False,
    ),
    NewVariableIdentifiers.CONTAINS_DATA_FROM: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelforekomsten i datasettet inneholder data fra og med denne dato.",
        presentation="date",
        component=ssb.Input,
    ),
    NewVariableIdentifiers.CONTAINS_DATA_UNTIL: DisplayNewVariablesMetadata(
        identifier=NewVariableIdentifiers.CONTAINS_DATA_UNTIL.value,
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
