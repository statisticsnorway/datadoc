"""Functions which aren't directly called from a decorated callback."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc import enums, state

if TYPE_CHECKING:
    from enum import Enum

    import pydantic

    from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)


MetadataInputTypes: type = str | int | float | bool | None


def update_global_language_state(language: SupportedLanguages) -> None:
    """Update global language state."""
    logger.debug("Updating language: %s", language.name)
    state.current_metadata_language = language


def get_language_strings_enum(enum: Enum) -> enums.LanguageStringsEnum:
    """Get the correct language strings enum for the given enum.

    We need multiple languages to display in the front end, but the model only defines a single language in the enums.
    """
    return getattr(enums, enum.__name__)


def get_options_for_language(
    language: SupportedLanguages,
    enum: Enum,
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    return [
        {
            "label": i.get_value_for_language(language),
            "value": i.name,
        }
        for i in get_language_strings_enum(enum)
    ]


def find_existing_language_string(
    metadata_model_object: pydantic.BaseModel,
    value: str,
    metadata_identifier: str,
) -> model.LanguageStringType | None:
    """Get or create a LanguageStrings object and return it."""
    # In this case we need to set the string to the correct language code
    language_strings = getattr(metadata_model_object, metadata_identifier)
    if language_strings is None:
        # This means that no strings have been saved yet so we need to construct
        # a new LanguageStrings object
        language_strings = model.LanguageStringType(
            **{state.current_metadata_language.value: value},
        )
    else:
        # In this case there's an existing object so we save this string
        # to the current language
        setattr(language_strings, state.current_metadata_language.value, value)
    return language_strings
