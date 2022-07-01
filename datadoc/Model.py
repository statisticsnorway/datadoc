from enum import Enum, auto
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, constr, conint

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"
URL_FORMAT = "(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([-a-zA-Z0-9.]{1,254}[A-Za-z0-9])?\.[a-zA-Z0-9()]{1,6}([\/][-a-zA-Z0-9_]+)*[\/]?"


class Assessment(str, Enum):
    # TODO: May have some kind of relation to DataSetState (SSB decision not made yet)? E.g. if "PROCSESSED_DATA" then "PROTECTED"?
    SENSITIVE = "SENSITIVE"
    PROTECTED = "PROTECTED"
    OPEN = "OPEN"


class DataSetState(str, Enum):
    SOURCE_DATA = "SOURCE_DATA"
    INPUT_DATA = "INPUT_DATA"
    PROCESSED_DATA = "PROCESSED_DATA"
    STATISTIC = "STATISTIC"
    OUTPUT_DATA = "OUTPUT_DATA"


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


class DataDocBaseModel(BaseModel):
    """Defines configuration which applies to all Models in this application"""

    class Config:
        # Runs validation when a field value is assigned, not just in the constructor
        validate_assignment = True
        # Write only the values of enums during serialization
        use_enum_values = True


class DataDocDataSet(DataDocBaseModel):
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
    spatial_coverage_description: Optional[List[Dict[str, str]]]
    id: Optional[constr(regex=URL_FORMAT)]
    owner: Optional[str]
    data_source_path: Optional[str]
    created_date: Optional[datetime]
    created_by: Optional[str]
    last_updated_date: Optional[datetime]
    last_updated_by: Optional[str]


class DataDocVariable(DataDocBaseModel):
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


class MetadataDocument(DataDocBaseModel):
    """Represents the data structure on file. Includes the dataset metadata from the user as
    well as meta-metadata like the percentage of completed metadata fields and the document version"""

    percentage_complete: conint(ge=0, le=100)
    document_version: str
    dataset: DataDocDataSet
    variables: List[DataDocVariable]
