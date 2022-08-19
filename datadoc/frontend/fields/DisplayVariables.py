from enum import Enum

from datadoc.frontend.fields.DisplayBase import DisplayVariablesMetadata
from datadoc_model import Model
from datadoc_model.LanguageStringsEnum import LanguageStringsEnum


class VariableIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst"""

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


DISPLAY_VARIABLES = {
    VariableIdentifiers.SHORT_NAME: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.NAME: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
        multiple_language_support=True,
    ),
    VariableIdentifiers.DATA_TYPE: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        presentation="dropdown",
    ),
    VariableIdentifiers.VARIABLE_ROLE: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        presentation="dropdown",
    ),
    VariableIdentifiers.DEFINITION_URI: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        obligatory=True,
    ),
    VariableIdentifiers.DIRECT_PERSON_IDENTIFYING: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="DPI",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
        presentation="dropdown",
    ),
    VariableIdentifiers.DATA_SOURCE: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.COMMENT: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
        multiple_language_support=True,
    ),
    VariableIdentifiers.TEMPORALITY_TYPE: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        presentation="dropdown",
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Måleenhet. Eksempel: NOK eller USD for valuta, KG eller TONN for vekt. Se også forslag til SSBs måletyper/måleenheter.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.FORMAT: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering. Dette kan benyttes som en ytterligere presisering av datatypen (dataType) i de tilfellene hvor dette er relevant. ",
    ),
    VariableIdentifiers.CLASSIFICATION_URI: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS",
    ),
    VariableIdentifiers.SENTINEL_VALUE_URI: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.SENTINEL_VALUE_URI.value,
        display_name="Spesialverdienes URI",
        description="En lenke (URI) til en oversikt over 'spesialverdier' som inngår i variabelen.",
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="En beskrivelse av ugyldige verdier som inngår i variabelen dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.IDENTIFIER: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="Unik ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelforekomsten i datasettet inneholder data fra og med denne dato.",
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: DisplayVariablesMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelforekomsten i datasettet inneholder data til og med denne dato.",
    ),
}

MULTIPLE_LANGUAGE_VARIABLES_METADATA = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.multiple_language_support
]

DISPLAYED_DROPDOWN_VARIABLES_METADATA = [
    m.identifier for m in DISPLAY_VARIABLES.values() if m.presentation == "dropdown"
]

DISPLAYED_DROPDOWN_VARIABLES_TYPES = []

for m in DISPLAY_VARIABLES.values():
    if m.presentation == "dropdown":
        field_type = Model.DataDocVariable.__fields__[m.identifier].type_
        if issubclass(field_type, LanguageStringsEnum) or field_type is bool:
            DISPLAYED_DROPDOWN_VARIABLES_TYPES.append(field_type)
