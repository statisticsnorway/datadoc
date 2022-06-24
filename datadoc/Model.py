from enum import Enum, auto
from typing import List, Optional
from pydantic import BaseModel, constr

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"
URL_FORMAT = "(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([-a-zA-Z0-9.]{1,254}[A-Za-z0-9])?\.[a-zA-Z0-9()]{1,6}([\/][-a-zA-Z0-9_]+)*[\/]?"


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
    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    name: Optional[List[str]]
    datatype: Optional[Datatype]
    definition_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
