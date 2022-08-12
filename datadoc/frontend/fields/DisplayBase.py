import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from dash import dcc
from dash.development.base_component import Component
from datadoc import state
from datadoc_model.LanguageStrings import LanguageStrings
from pydantic import BaseModel

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
    directly assign a mutable type like a dict to a dataclass field"""
    return INPUT_KWARGS


def get_standard_metadata(metadata: BaseModel, identifier: str) -> Any:
    return metadata.dict()[identifier]


def get_multi_language_metadata(metadata: BaseModel, identifier: str) -> Optional[str]:
    value: LanguageStrings = getattr(metadata, identifier)
    if value is None:
        return value
    return getattr(value, state.current_metadata_language)


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
    options: Optional[Dict[str, List[Dict[str, str]]]] = None
    presentation: Optional[str] = "input"


@dataclass
class DisplayDatasetMetadata(DisplayMetadata):
    extra_kwargs: Dict[str, Any] = field(default_factory=kwargs_factory)
    component: Type[Component] = dcc.Input
    value_getter: Callable[[BaseModel, str], Any] = get_standard_metadata
