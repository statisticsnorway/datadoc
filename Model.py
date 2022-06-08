from enum import Enum, auto
from pydantic import BaseModel, constr

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"


class Datatype(str, Enum):
    STRING = auto
    INTEGER = auto
    FLOAT = auto
    DATETIME = auto
    BOOLEAN = auto


class DataDocVariable(BaseModel):
    short_name: constr(
        min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE
    ) = None
    name: constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    datatype: Datatype = None
