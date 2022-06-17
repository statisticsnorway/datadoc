from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from .Model import Datatype, VariableRole


class VariableIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst"""

    SHORT_NAME = "shortName"
    NAME = "name"
    DATA_TYPE = "dataType"
    VARIABLE_ROLE = "variableRole"
    DEFINITION_URI = "definitionUri"
    DIRECT_PERSON_IDENTIFYING = "directPersonIdentifying"
    DATA_SOURCE = "dataSource"
    POPULATION_DESCRIPTION = "populationDescription"
    COMMENT = "comment"
    TEMPORALITY_TYPE = "temporalityType"
    MEASUREMENT_UNIT = "measurementUnit"
    FORMAT = "format"
    CLASSIFICATION_URI = "classificationUri"
    SENTINEL_VALUE_URI = "sentinelValueUri"
    INVALID_VALUE_DESCRIPTION = "invalidValueDescription"
    IDENTIFIER = "id"
    CONTAINS_DATA_FROM = "containsDataFrom"
    CONTAINS_DATA_UNTIL = "containsDataUntil"


@dataclass
class DisplayVariable:
    identifier: str
    display_name: str
    description: str
    obligatory: bool = False
    presentation: Optional[str] = "input"
    options: Optional[List[Any]] = field(default_factory=list)
    editable: bool = True


DISPLAY_VARIABLES = {
    VariableIdentifiers.SHORT_NAME: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#shortName
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.NAME: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#name
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
        obligatory=True,
    ),
    VariableIdentifiers.DATA_TYPE: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#datatype
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Datatype",
        obligatory=True,
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in Datatype]},
    ),
    VariableIdentifiers.VARIABLE_ROLE: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#variabelRole
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Variabelens rolle i datasett",
        obligatory=True,
        presentation="dropdown",
        options={"options": [{"label": i.name, "value": i.name} for i in VariableRole]},
    ),
    VariableIdentifiers.DEFINITION_URI: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#definitionUri
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="En lenke (URI) til variabelens definisjon i SSB (Vardok/VarDef)",
        obligatory=True,
    ),
    VariableIdentifiers.DIRECT_PERSON_IDENTIFYING: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#directPersonIdentifying
        identifier=VariableIdentifiers.DIRECT_PERSON_IDENTIFYING.value,
        display_name="DPI",
        description="Direkte personidentifiserende informasjon (DPI)",
        obligatory=True,
    ),
    VariableIdentifiers.DATA_SOURCE: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#dataSource
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilde. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#populationDescription
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen variabelen beskriver kan spesifiseres nærmere her. Settes på datasettnivå, men kan overstyres på variabelforekomstnivå.",
    ),
    VariableIdentifiers.COMMENT: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#populationDescription
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
    ),
    VariableIdentifiers.COMMENT: DisplayVariable(
        # https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst#comment
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Ytterligere presiseringer av variabeldefinisjon",
    ),
}
