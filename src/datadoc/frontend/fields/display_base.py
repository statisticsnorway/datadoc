"""Functionality common to displaying dataset and variables metadata."""

from __future__ import annotations

import logging
import typing as t
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import dcc

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import get_language_strings_enum

if TYPE_CHECKING:
    from collections.abc import Callable
    from enum import Enum

    from dash.development.base_component import Component
    from datadoc_model import model
    from datadoc_model.model import LanguageStringType
    from pydantic import BaseModel

    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)


VARIABLES_METADATA_INPUT = "variables-metadata-input"
VARIABLES_METADATA_DATE_INPUT = "variables-metadata-date-input"

# Must be changed if new design
INPUT_KWARGS = {
    "debounce": True,
    "style": {"width": "100%"},
    "className": "ssb-input",
}


def get_enum_options_for_language(
    enum: Enum,
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    return [
        {
            "title": i.get_value_for_language(language),
            "id": i.name,
        }
        for i in get_language_strings_enum(enum)  # type: ignore [attr-defined]
    ]


def input_kwargs_factory() -> dict[str, t.Any]:
    """Initialize the field extra_kwargs.

    We aren't allowed to directly assign a mutable type like a dict to
    a dataclass field.
    """
    return INPUT_KWARGS


def empty_kwargs_factory() -> dict[str, t.Any]:
    """Initialize the field extra_kwargs.

    We aren't allowed to directly assign a mutable type like a dict to
    a dataclass field.
    """
    return {}


def get_standard_metadata(metadata: BaseModel, identifier: str) -> MetadataInputTypes:
    """Get a metadata value from the model."""
    return getattr(metadata, identifier)


def get_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value from the model and cast to string."""
    value = get_standard_metadata(metadata, identifier)
    if value is None:
        return None
    return str(value)


def get_multi_language_metadata(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value supporting multiple languages from the model."""
    value: LanguageStringType | None = getattr(metadata, identifier)
    if value is None:
        return value
    return str(getattr(value, state.current_metadata_language))


def get_comma_separated_string(metadata: BaseModel, identifier: str) -> str:
    """Get a metadata value which is a list of strings from the model and convert it to a comma separated string."""
    value: list[str] = getattr(metadata, identifier)
    try:
        return ", ".join(value)
    except TypeError:
        logger.exception("Type error")
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
class DisplayDatasetMetadata(DisplayMetadata):
    """Controls for how a given metadata field should be displayed.

    Specific to dataset fields.
    """

    extra_kwargs: dict[str, Any] = field(default_factory=input_kwargs_factory)
    component: type[Component] = dcc.Input
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify


@dataclass
class DisplayDatasetMetadataDropdown(DisplayDatasetMetadata):
    """Include the possible options which a user may choose from."""

    # fmt: off
    options_getter: Callable[[SupportedLanguages], list[dict[str, str]]] = lambda _: []  # noqa: E731
    # fmt: on
    extra_kwargs: dict[str, Any] = field(default_factory=empty_kwargs_factory)
    component: type[Component] = dcc.Dropdown


@dataclass
class VariablesInputField(DisplayMetadata):
    """Controls for how a given metadata field should be displayed.

    Specific to variable fields.
    """

    extra_kwargs: dict[str, Any] = field(default_factory=empty_kwargs_factory)
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify
    type: str = "text"

    def render(
        self,
        variable_id: dict,
        language: str,  # noqa: ARG002
        variable: model.Variable,
    ) -> ssb.Input:
        """Build Input component."""
        value = self.value_getter(variable, self.identifier)
        return ssb.Input(
            label=self.display_name,
            id=variable_id,
            debounce=True,
            type=self.type,
            disabled=not self.editable,
            value=value,
            className="variable-input",
        )


@dataclass
class VariablesPeriodField(DisplayMetadata):
    """Control how fields which define a time period are displayed.

    These are a special case since two fields have a relationship to one another.>
    """

    extra_kwargs: dict[str, Any] = field(default_factory=empty_kwargs_factory)
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify
    type: str = "date"

    def render(
        self,
        variable_id: dict,
        language: str,  # noqa: ARG002
        variable: model.Variable,
    ) -> ssb.Input:
        """Build Input date component."""
        value = self.value_getter(variable, self.identifier)
        variable_id["type"] = VARIABLES_METADATA_DATE_INPUT
        return ssb.Input(
            label=self.display_name,
            id=variable_id,
            debounce=False,
            type=self.type,
            disabled=not self.editable,
            value=value,
            className="variable-input",
        )


@dataclass
class VariablesDropdownField(DisplayMetadata):
    """Control how a Dropdown should be displayed."""

    extra_kwargs: dict[str, Any] = field(default_factory=empty_kwargs_factory)
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify
    # fmt: off
    options_getter: Callable[[SupportedLanguages], list[dict[str, str]]] = lambda _: []  # noqa: E731
    # fmt: on

    def render(
        self,
        variable_id: dict,
        language: str,
        variable: model.Variable,
    ) -> ssb.Dropdown:
        """Build Dropdown component."""
        value = self.value_getter(variable, self.identifier)
        return ssb.Dropdown(
            header=self.display_name,
            id=variable_id,
            items=self.options_getter(SupportedLanguages(language)),
            value=value,
            className="variable-dropdown",
        )


@dataclass
class VariablesCheckboxField(DisplayMetadata):
    """Controls for how a checkbox metadata field should be displayed."""

    extra_kwargs: dict[str, Any] = field(default_factory=input_kwargs_factory)
    value_getter: Callable[[BaseModel, str], Any] = get_standard_metadata

    def render(
        self,
        variable_id: dict,
        language: str,  # noqa: ARG002
        variable: model.Variable,
    ) -> dbc.Checkbox:
        """Build Checkbox component."""
        value = self.value_getter(variable, self.identifier)
        return dbc.Checkbox(
            label=self.display_name,
            id=variable_id,
            disabled=not self.editable,
            label_class_name="ssb-checkbox checkbox-label",
            class_name="ssb-checkbox",
            value=value,
        )


VariablesFieldTypes = (
    VariablesInputField
    | VariablesDropdownField
    | VariablesCheckboxField
    | VariablesPeriodField
)
