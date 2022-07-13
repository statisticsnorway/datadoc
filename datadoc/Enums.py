from enum import Enum


class Assessment(str, Enum):
    # TODO: May have some kind of relation to DataSetState (SSB decision not made yet)? E.g. if "PROCSESSED_DATA" then "PROTECTED"?
    SENSITIVE = "SENSITIVE"
    PROTECTED = "PROTECTED"
    OPEN = "OPEN"


class DatasetState(str, Enum):
    SOURCE_DATA = "SOURCE_DATA"
    INPUT_DATA = "INPUT_DATA"
    PROCESSED_DATA = "PROCESSED_DATA"
    STATISTIC = "STATISTIC"
    OUTPUT_DATA = "OUTPUT_DATA"


class DatasetStatus(str, Enum):
    DRAFT = "DRAFT"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    DEPRECATED = "DEPRECATED"


class AdministrativeStatus(str, Enum):
    # TODO: The definition of this property is not complete (may change)?
    DRAFT = "DRAFT"
    INTERNAL = "INTERNAL"
    OPEN = "OPEN"
    DEPRECATED = "DEPRECATED"


class UnitType(str, Enum):
    # TODO: May change in the nearest future? See list of SSB unit types https://www.ssb.no/metadata/definisjoner-av-statistiske-enheter
    ARBEIDSULYKKE = "ARBEIDSULYKKE"
    BOLIG = "BOLIG"
    BYGNING = "BYGNING"
    EIENDOM = "EIENDOM"
    FAMILIE = "FAMILIE"
    FORETAK = "FORETAK"
    FYLKE = "FYLKE"
    HAVNEANLOEP = "HAVNEANLOEP"
    HUSHOLDNING = "HUSHOLDNING"
    KJOERETOEY = "KJOERETOEY"
    KOMMUNE = "KOMMUNE"
    KURS = "KURS"
    LOVBRUDD = "LOVBRUDD"
    PERSON = "PERSON"
    STAT = "STAT"
    STORFE = "STORFE"
    TRAFIKKULYKKE = "TRAFIKKULYKKE"
    TRANSAKSJON = "TRANSAKSJON"
    VARE_TJENESTE = "VARE_TJENESTE"
    VERDIPAPIR = "VERDIPAPIR"
    VIRKSOMHET = "VIRKSOMHET"


class TemporalityType(str, Enum):
    # More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    FIXED = "FIXED"
    STATUS = "STATUS"
    ACCUMULATED = "ACCUMULATED"
    EVENT = "EVENT"


class Datatype(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"


class VariableRole(str, Enum):
    IDENTIFIER = "IDENTIFIER"
    MEASURE = "MEASURE"
    START_TIME = "START_TIME"
    STOP_TIME = "STOP_TIME"
    ATTRIBUTE = "ATTRIBUTE"


class SupportedLanguages(str, Enum):
    "Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
    NORSK_BOKMÅL = "nb"
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"
