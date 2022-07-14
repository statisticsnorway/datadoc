from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from datadoc.Enums import Datatype, TemporalityType, VariableRole


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


@dataclass
class DisplayMetadata:
    identifier: str
    display_name: str
    description: str
    options: Optional[Dict[str, List[Dict[str, str]]]] = None
    obligatory: bool = False
    presentation: Optional[str] = "input"
    editable: bool = True
    multiple_language_support: bool = False


DISPLAY_VARIABLES = {
    VariableIdentifiers.SHORT_NAME: DisplayMetadata(
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.NAME: DisplayMetadata(
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
    ),
    VariableIdentifiers.DATA_TYPE: DisplayMetadata(
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in Datatype]},
    ),
    VariableIdentifiers.VARIABLE_ROLE: DisplayMetadata(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in VariableRole]},
    ),
    VariableIdentifiers.DEFINITION_URI: DisplayMetadata(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        obligatory=True,
    ),
    VariableIdentifiers.DIRECT_PERSON_IDENTIFYING: DisplayMetadata(
        identifier=VariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="DPI",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
        presentation="dropdown",
        options={
            "options": [
                {"label": "Ja", "value": "True"},
                {"label": "Nei", "value": "False"},
            ]
        },
    ),
    VariableIdentifiers.DATA_SOURCE: DisplayMetadata(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: DisplayMetadata(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
    ),
    VariableIdentifiers.COMMENT: DisplayMetadata(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
    ),
    VariableIdentifiers.TEMPORALITY_TYPE: DisplayMetadata(
        identifier=VariableIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
        presentation="dropdown",
        options={
            "options": [{"label": i.name, "value": i.name} for i in TemporalityType]
        },
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: DisplayMetadata(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Måleenhet. Eksempel: NOK eller USD for valuta, KG eller TONN for vekt. Se også forslag til SSBs måletyper/måleenheter.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.FORMAT: DisplayMetadata(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering. Dette kan benyttes som en ytterligere presisering av datatypen (dataType) i de tilfellene hvor dette er relevant. ",
    ),
    VariableIdentifiers.CLASSIFICATION_URI: DisplayMetadata(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS",
    ),
    VariableIdentifiers.SENTINEL_VALUE_URI: DisplayMetadata(
        identifier=VariableIdentifiers.SENTINEL_VALUE_URI.value,
        display_name="Spesialverdienes URI",
        description="En lenke (URI) til en oversikt over 'spesialverdier' som inngår i variabelen.",
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: DisplayMetadata(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="En beskrivelse av ugyldige verdier som inngår i variabelen dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        multiple_language_support=True,
    ),
    VariableIdentifiers.IDENTIFIER: DisplayMetadata(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="Unik ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: DisplayMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelforekomsten i datasettet inneholder data fra og med denne dato.",
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: DisplayMetadata(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelforekomsten i datasettet inneholder data til og med denne dato.",
    ),
}
