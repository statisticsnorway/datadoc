"""Functionality common to displaying dataset and variables metadata."""

from __future__ import annotations

import logging
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

import ssb_dash_components as ssb

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import get_language_strings_enum

if TYPE_CHECKING:
    from collections.abc import Callable
    from enum import Enum

    from dash.development.base_component import Component
    from datadoc_model.model import LanguageStringType
    from pydantic import BaseModel

    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)

DATASET_METADATA_INPUT = "dataset-metadata-input"

VARIABLES_METADATA_INPUT = "variables-metadata-input"
VARIABLES_METADATA_DATE_INPUT = "variables-metadata-date-input"
DATASET_METADATA_DATE_INPUT = "dataset-metadata-date-input"


def get_enum_options_for_language(
    enum: Enum,
    language: SupportedLanguages,
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    dropdown_options = [
        {
            "title": i.get_value_for_language(language),
            "id": i.name,
        }
        for i in get_language_strings_enum(enum)  # type: ignore [attr-defined]
    ]
    dropdown_options.insert(0, {"title": "", "id": ""})
    return dropdown_options


def get_standard_metadata(metadata: BaseModel, identifier: str) -> MetadataInputTypes:
    """Get a metadata value from the model."""
    return getattr(metadata, identifier)


def get_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value from the model and cast to string."""
    value = get_standard_metadata(metadata, identifier)
    if value is None:
        return None
    return str(value)


def get_date_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata date value from the model.

    Handle converting datetime format to date format string.
    """
    value = get_standard_metadata(metadata, identifier)
    if value is None:
        return ""
    logger.info("Date registered: %s", value)
    date = str(value)
    # Pattern for datetime without T, with space - used for variables
    pattern = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}"
    if re.match(pattern, date):
        convert_date_to_iso = date.replace(" ", "T")
        logger.info("Date converted to iso format: %s", convert_date_to_iso)
        convert_date_format = convert_date_to_iso[:10]
        logger.info("Display date: %s", convert_date_format)
        return convert_date_format
    convert_value = date[:10]
    logger.info("Display date: %s", convert_value)
    return convert_value


def get_multi_language_metadata(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value supporting multiple languages from the model."""
    value: LanguageStringType | None = getattr(metadata, identifier)
    if value is None:
        return value
    return _get_string_type_item(value, state.current_metadata_language)


def _get_string_type_item(
    language_strings: LanguageStringType,
    current_metadata_language: SupportedLanguages,
) -> str | None:
    if language_strings.root is not None:
        for i in language_strings.root:
            if i.languageCode == current_metadata_language:
                return i.languageText
    return None


def get_comma_separated_string(metadata: BaseModel, identifier: str) -> str:
    """Get a metadata value which is a list of strings from the model and convert it to a comma separated string."""
    value: list[str] = getattr(metadata, identifier)
    try:
        return ", ".join(value)
    except TypeError:
        # This just means we got None
        return ""


@dataclass
class DisplayMetadata(ABC):
    """Controls how a given metadata field should be displayed."""

    identifier: str
    display_name: str
    description: str
    obligatory: bool = False
    editable: bool = True
    multiple_language_support: bool = False
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify
    show_description: bool = True
    disabled: bool = False

    @abstractmethod
    def render(
        self,
        component_id: dict,
        language: str,
        metadata: BaseModel,
    ) -> Component:
        """Build a component."""
        ...


@dataclass
class MetadataInputField(DisplayMetadata):
    """Controls how an input field should be displayed."""

    type: str = "text"

    def render(
        self,
        component_id: dict,
        language: str,  # noqa: ARG002
        metadata: BaseModel,
    ) -> ssb.Input:
        """Build an Input component."""
        value = self.value_getter(metadata, self.identifier)
        return ssb.Input(
            label=self.display_name,
            id=component_id,
            debounce=True,
            type=self.type,
            showDescription=self.show_description,
            description=self.description,
            readOnly=not self.editable,
            value=value,
            disabled=self.disabled,
            className="input-component",
        )


@dataclass
class MetadataDropdownField(DisplayMetadata):
    """Controls how a Dropdown should be displayed."""

    # fmt: off
    options_getter: Callable[[SupportedLanguages], list[dict[str, str]]] = lambda _: []
    # fmt: on

    def render(
        self,
        component_id: dict,
        language: str,
        metadata: BaseModel,
    ) -> ssb.Dropdown:
        """Build Dropdown component."""
        value = self.value_getter(metadata, self.identifier)
        return ssb.Dropdown(
            header=self.display_name,
            id=component_id,
            items=self.options_getter(SupportedLanguages(language)),
            value=value,
            className="dropdown-component",
            showDescription=self.show_description,
            description=self.description,
        )


@dataclass
class MetadataPeriodField(DisplayMetadata):
    """Controls how fields which define a time period are displayed.

    These are a special case since two fields have a relationship to one another.
    """

    id_type: str = ""
    value_getter: Callable[[BaseModel, str], Any] = get_date_metadata_and_stringify

    def render(
        self,
        component_id: dict,
        language: str,  # noqa: ARG002
        metadata: BaseModel,
    ) -> ssb.Input:
        """Build Input date component."""
        value = self.value_getter(metadata, self.identifier)
        component_id["type"] = self.id_type
        return ssb.Input(
            label=self.display_name,
            id=component_id,
            debounce=False,
            type="date",
            disabled=not self.editable,
            showDescription=self.show_description,
            description=self.description,
            value=value,
            className="input-component",
        )


@dataclass
class MetadataCheckboxField(DisplayMetadata):
    """Controls for how a checkbox metadata field should be displayed."""

    value_getter: Callable[[BaseModel, str], Any] = get_standard_metadata

    def render(
        self,
        component_id: dict,
        language: str,  # noqa: ARG002
        metadata: BaseModel,
    ) -> ssb.Checkbox:
        """Build Checkbox component."""
        value = self.value_getter(metadata, self.identifier)
        return ssb.Checkbox(
            label=self.display_name,
            id=component_id,
            disabled=not self.editable,
            value=value,
            showDescription=self.show_description,
            description=self.description,
        )


VariablesFieldTypes = (
    MetadataInputField
    | MetadataDropdownField
    | MetadataCheckboxField
    | MetadataPeriodField
)

DatasetFieldTypes = (
    MetadataInputField
    | MetadataDropdownField
    | MetadataPeriodField
    | MetadataCheckboxField
)
