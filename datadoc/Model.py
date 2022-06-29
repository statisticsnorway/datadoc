from enum import Enum, auto
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, constr

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"
URL_FORMAT = "(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([-a-zA-Z0-9.]{1,254}[A-Za-z0-9])?\.[a-zA-Z0-9()]{1,6}([\/][-a-zA-Z0-9_]+)*[\/]?"


class Assessment(Enum):
    # TODO: May have some kind of relation to DataSetState (SSB decision not made yet)? E.g. if "PROCSESSED_DATA" then "PROTECTED"?
    SENSITIVE = auto()
    PROTECTED = auto()
    OPEN = auto()


class DataSetState(Enum):
    SOURCE_DATA = auto()
    INPUT_DATA = auto()
    PROCESSED_DATA = auto()
    STATISTIC = auto()
    OUPUT_DATA = auto()


class AdministrativeStatus(Enum):
    # TODO: The definition of this property is not complete (may change)?
    DRAFT = auto()
    INTERNAL = auto()
    OPEN = auto()
    DEPRECATED = auto()


class UnitType(Enum):
    # TODO: May change in the nearest future? See list of SSB unit types https://www.ssb.no/metadata/definisjoner-av-statistiske-enheter
    ARBEIDSULYKKE = auto()
    BOLIG = auto()
    BYGNING = auto()
    EIENDOM = auto()
    FAMILIE = auto()
    FORETAK = auto()
    FYLKE = auto()
    HAVNEANLOEP = auto()
    HUSHOLDNING = auto()
    KJOERETOEY = auto()
    KOMMUNE = auto()
    KURS = auto()
    LOVBRUDD = auto()
    PERSON = auto()
    STAT = auto()
    STORFE = auto()
    TRAFIKKULYKKE = auto()
    TRANSAKSJON = auto()
    VARE_TJENESTE = auto()
    VERDIPAPIR = auto()
    VIRKSOMHET = auto()


class TemporalityType(Enum):
    # More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    FIXED = auto()
    STATUS = auto()
    ACCUMULATED = auto()
    EVENT = auto()


class DataDocDataSet(BaseModel):
    """DataDoc data set. See documentation https://statistics-norway.atlassian.net/l/c/NgjE7yj1"""

    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    assessment: Optional[Assessment]
    dataset_state: Optional[DataSetState]
    name: Optional[str]
    data_source: Optional[str]
    population_description: Optional[str]
    administrative_status: Optional[AdministrativeStatus] = AdministrativeStatus.DRAFT
    version: Optional[str]
    unit_type: Optional[UnitType]
    temporality_type: Optional[TemporalityType]
    description: Optional[str]
    spatial_coverage_description: Optional[str]
    id: Optional[constr(regex=URL_FORMAT)]
    owner: Optional[str]
    data_source_path: Optional[str]
    created_date: Optional[datetime]
    created_by: Optional[str]
    last_updated_date: Optional[datetime]
    last_updated_by: Optional[str]


class Datatype(Enum):
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    DATETIME = auto()
    BOOLEAN = auto()


class VariableRole(Enum):
    IDENTIFIER = auto()
    MEASURE = auto()
    START_TIME = auto()
    STOP_TIME = auto()
    ATTRIBUTE = auto()


class DataDocVariable(BaseModel):
    """DataDoc instance variable. See documentation https://statistics-norway.atlassian.net/l/c/goyNhUPP"""

    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    name: Optional[str]
    datatype: Optional[Datatype]
    variable_role: Optional[VariableRole]
    definition_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    direct_person_identifying: Optional[bool]
    data_source: Optional[str]
    population_description: Optional[str]
    comment: Optional[str]
    temporality_type: Optional[TemporalityType]
    # TODO: measurement_unit implemented as string. In the future this should be implemente as a class? See https://www.ssb.no/klass/klassifikasjoner/303/koder
    measurement_unit: Optional[str]
    format: Optional[str]
    classification_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    sentinel_value_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    invalid_value_description: Optional[str]
    id: Optional[constr(regex=URL_FORMAT)]
    contains_data_from: Optional[date]
    contains_data_until: Optional[date]
