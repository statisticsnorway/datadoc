"""Functionality common to displaying dataset and variables metadata."""

from __future__ import annotations

import logging
import typing as t
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from dash import dcc

from datadoc import state

if TYPE_CHECKING:
    from collections.abc import Callable

    from dash.development.base_component import Component
    from datadoc_model.model import LanguageStringType
    from pydantic import BaseModel

    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)

INPUT_KWARGS = {
    "debounce": True,
    "style": {"width": "100%"},
    "className": "ssb-input",
}
NUMBER_KWARGS = dict(type="number", **INPUT_KWARGS)
DROPDOWN_KWARGS = {
    "style": {"width": "100%"},
    "className": "ssb-dropdown",
}


def kwargs_factory() -> dict[str, t.Any]:
    """Initialize the field extra_kwargs.

    We aren't allowed to directly assign a mutable type like a dict to
    a dataclass field.
    """
    return INPUT_KWARGS


def get_standard_metadata(metadata: BaseModel, identifier: str) -> MetadataInputTypes:
    """Get a metadata value from the model."""
    value = metadata.model_dump()[identifier]
    if value is None:
        return None
    return str(value)


def get_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str:
    """Get a metadata value from the model and cast to string."""
    return str(get_standard_metadata(metadata, identifier))


def get_multi_language_metadata(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value supportng multiple languages from the model."""
    value: LanguageStringType = getattr(metadata, identifier)
    if value is None:
        return value
    return str(getattr(value, state.current_metadata_language))


def get_comma_separated_string(metadata: BaseModel, identifier: str) -> str:
    """Get a metadata value which is a list of strings from the model and convert it to a comma separated string."""
    value: list[str] = getattr(metadata, identifier)
    try:
        return ", ".join(value)
    except TypeError:
        return ""


@dataclass
class DisplayMetadata:
    """Controls for how a given metadata field should be displayed."""

    identifier: str
    display_name: str
    description: str
    obligatory: bool = False
    editable: bool = True
    url: bool = False
    multiple_language_support: bool = False


@dataclass
class DisplayVariablesMetadata(DisplayMetadata):
    """Controls for how a given metadata field should be displayed.

    Specific to variable fields.
    """

    options: dict[str, list[dict[str, str]]] | None = None
    presentation: str | None = "input"


@dataclass
class DisplayDatasetMetadata(DisplayMetadata):
    """Controls for how a given metadata field should be displayed.

    Specific to dataset fields.
    """

    extra_kwargs: dict[str, Any] = field(default_factory=kwargs_factory)
    component: type[Component] = dcc.Input
    value_getter: Callable[[BaseModel, str], Any] = get_standard_metadata
