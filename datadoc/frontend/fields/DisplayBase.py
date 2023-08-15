import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dash import dcc
from dash.development.base_component import Component
from pydantic import BaseModel

from datadoc import state

if TYPE_CHECKING:
    from datadoc_model.LanguageStrings import LanguageStrings

logger = logging.getLogger(__name__)

INPUT_KWARGS = {
    "debounce": True,
    "style": {"width": "100%"},
    "className": "ssb-input",
}
NUMBER_KWARGS = dict(**INPUT_KWARGS, **{"type": "number"})
DROPDOWN_KWARGS = {
    "style": {"width": "100%"},
    "className": "ssb-dropdown",
}


def kwargs_factory():
    """For initialising the field extra_kwargs. We aren't allowed to
    directly assign a mutable type like a dict to a dataclass field.
    """
    return INPUT_KWARGS


def get_standard_metadata(metadata: BaseModel, identifier: str) -> Any:
    return metadata.dict()[identifier]


def get_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str:
    return str(metadata.dict()[identifier])


def get_multi_language_metadata(metadata: BaseModel, identifier: str) -> str | None:
    value: LanguageStrings = getattr(metadata, identifier)
    if value is None:
        return value
    return getattr(value, state.current_metadata_language)


def get_list_of_strings(metadata: BaseModel, identifier: str) -> str:
    value: list[str] = getattr(metadata, identifier)
    if value is None:
        return ""
    return ", ".join(value)


@dataclass
class DisplayMetadata:
    identifier: str
    display_name: str
    description: str
    obligatory: bool = False
    editable: bool = True
    multiple_language_support: bool = False


@dataclass
class DisplayVariablesMetadata(DisplayMetadata):
    options: dict[str, list[dict[str, str]]] | None = None
    presentation: str | None = "input"


@dataclass
class DisplayDatasetMetadata(DisplayMetadata):
    extra_kwargs: dict[str, Any] = field(default_factory=kwargs_factory)
    component: type[Component] = dcc.Input
    value_getter: Callable[[BaseModel, str], Any] = get_standard_metadata
