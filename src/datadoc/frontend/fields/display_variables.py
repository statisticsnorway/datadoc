"""Functionality for displaying variables metadata."""

from __future__ import annotations

import functools
from enum import Enum

from datadoc import enums
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import MetadataCheckboxField
from datadoc.frontend.fields.display_base import MetadataDropdownField
from datadoc.frontend.fields.display_base import MetadataInputField
from datadoc.frontend.fields.display_base import MetadataPeriodField
from datadoc.frontend.fields.display_base import VariablesFieldTypes
from datadoc.frontend.fields.display_base import get_enum_options_for_language
from datadoc.frontend.fields.display_base import get_multi_language_metadata


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


DISPLAY_VARIABLES: dict[
    VariableIdentifiers,
    VariablesFieldTypes,
] = {
    VariableIdentifiers.SHORT_NAME: MetadataInputField(
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.NAME: MetadataInputField(
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
        multiple_language_support=True,
        type="text",
    ),
    VariableIdentifiers.DATA_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.DataType,
        ),
    ),
    VariableIdentifiers.VARIABLE_ROLE: MetadataDropdownField(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.VariableRole,
        ),
    ),
    VariableIdentifiers.DEFINITION_URI: MetadataInputField(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        url=True,
        obligatory=True,
        type="url",
    ),
    VariableIdentifiers.DIRECT_PERSON_IDENTIFYING: MetadataCheckboxField(
        identifier=VariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="Direkte personidentifiserende informasjon",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
    ),
    VariableIdentifiers.DATA_SOURCE: MetadataInputField(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
        type="text",
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: MetadataInputField(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
        type="text",
    ),
    VariableIdentifiers.COMMENT: MetadataInputField(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
        multiple_language_support=True,
        type="text",
    ),
    VariableIdentifiers.TEMPORALITY_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        options_getter=functools.partial(
            get_enum_options_for_language,
            enums.TemporalityTypeType,
        ),
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: MetadataInputField(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Måleenhet. Eksempel: NOK eller USD for valuta, KG eller TONN for vekt. Se også forslag til SSBs måletyper/måleenheter.",
        type="text",
    ),
    VariableIdentifiers.FORMAT: MetadataInputField(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering. Dette kan benyttes som en ytterligere presisering av datatypen (dataType) i de tilfellene hvor dette er relevant. ",
    ),
    VariableIdentifiers.CLASSIFICATION_URI: MetadataInputField(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS",
        url=True,
        type="url",
    ),
    VariableIdentifiers.SENTINEL_VALUE_URI: MetadataInputField(
        identifier=VariableIdentifiers.SENTINEL_VALUE_URI.value,
        display_name="Spesialverdienes URI",
        description="En lenke (URI) til en oversikt over 'spesialverdier' som inngår i variabelen.",
        url=True,
        type="url",
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: MetadataInputField(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="En beskrivelse av ugyldige verdier som inngår i variabelen dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.IDENTIFIER: MetadataInputField(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        editable=False,
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelforekomsten i datasettet inneholder data fra og med denne dato.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelforekomsten i datasettet inneholder data til og med denne dato.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
    ),
}

MULTIPLE_LANGUAGE_VARIABLES_METADATA = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.multiple_language_support
]

for v in DISPLAY_VARIABLES.values():
    if v.multiple_language_support:
        v.value_getter = get_multi_language_metadata

OBLIGATORY_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if m.obligatory and m.editable
]

OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.obligatory and m.editable
]

OPTIONAL_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if not m.obligatory and m.editable
]
