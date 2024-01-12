"""Callback functions to do with variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import get_options_for_language
from datadoc.frontend.fields.display_variables import (
    DISPLAYED_DROPDOWN_VARIABLES_METADATA,
)
from datadoc.frontend.fields.display_variables import DISPLAYED_DROPDOWN_VARIABLES_TYPES
from datadoc.frontend.fields.display_variables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
)
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.utils import get_display_values

if TYPE_CHECKING:
    from datadoc_model import model

logger = logging.getLogger(__name__)


def get_boolean_options_for_language(
    language: SupportedLanguages,
) -> list[dict[str, bool | str]]:
    """Get boolean options for the given language.

    The Dash Datatable has no good support for boolean
    choices, so we use a Dropdown.
    """
    true_labels = {
        SupportedLanguages.ENGLISH: "Yes",
        SupportedLanguages.NORSK_NYNORSK: "Ja",
        SupportedLanguages.NORSK_BOKMÅL: "Ja",
    }
    false_labels = {
        SupportedLanguages.ENGLISH: "No",
        SupportedLanguages.NORSK_NYNORSK: "Nei",
        SupportedLanguages.NORSK_BOKMÅL: "Nei",
    }
    return [
        {
            "label": f"{true_labels[language]}",
            "value": True,
        },
        {
            "label": f"{false_labels[language]}",
            "value": False,
        },
    ]


def get_metadata_field(
    data: list[dict],
    data_previous: list[dict],
    active_cell: dict,
) -> str:
    """Find which field (column in the data table) has been updated."""
    for i in range(len(data)):
        # Find which column we're in; by diffing the current and previous data
        update_diff = list(data[i].items() - data_previous[i].items())
        if update_diff:
            return update_diff[-1][0]

    # When diffing fails, we fall back to the active cell (this happens
    # when the user pastes a value into the Data Table)
    return active_cell["column_id"]


def handle_multi_language_metadata(
    metadata_field: str,
    new_value: MetadataInputTypes,
    updated_row_id: str,
) -> MetadataInputTypes | model.LanguageStringType:
    """Handle updates to fields which support multiple languages."""
    if new_value is None:
        # This edge case occurs when the user removes the text in an input field
        # We want to ensure we only remove the content for the current language,
        # not create a new blank object!
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            "",
            metadata_field,
        )

    if isinstance(new_value, str):
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            new_value,
            metadata_field,
        )

    return new_value


def accept_variable_metadata_input(
    data: list[dict],
    active_cell: dict,
    data_previous: list[dict],
) -> tuple[list[dict], bool, str]:
    """Validate and save the value when variable metadata is updated."""
    show_error = False
    error_explanation = ""
    output_data = data
    metadata_field: str = get_metadata_field(data, data_previous, active_cell)

    for row_index in range(len(data)):
        # Update all the variables for this column to ensure we read in the value
        new_value: MetadataInputTypes = data[row_index][metadata_field]
        updated_row_id = data[row_index][VariableIdentifiers.SHORT_NAME.value]

        try:
            if metadata_field in MULTIPLE_LANGUAGE_VARIABLES_METADATA:
                new_value = handle_multi_language_metadata(
                    metadata_field,
                    new_value,
                    updated_row_id,
                )
            elif new_value == "":
                # Allow clearing non-multiple-language text fields
                new_value = None

            # Write the value to the variables structure
            setattr(
                state.metadata.variables_lookup[updated_row_id],
                metadata_field,
                new_value,
            )
        except ValidationError as e:
            show_error = True
            error_explanation = f"`{e}`"
            output_data = data_previous
            logger.debug("Caught ValidationError:", exc_info=True)
        else:
            logger.debug("Successfully updated %s with %s", updated_row_id, new_value)

    return output_data, show_error, error_explanation


def update_variable_table_dropdown_options_for_language(
    language: SupportedLanguages,
) -> dict[str, dict[str, object]]:
    """Retrieve enum options for dropdowns in the Datatable.

    Handles the special case of boolean values which we represent in the Datatable
    with a Dropdown but they're not backed by an Enum. Example return data structure as follows:

    ..  code-block:: python

        {
            "data_type": {
                "options": [
                    {"label": "TEKST", "value": "STRING"},
                    {"label": "HELTALL", "value": "INTEGER"},
                    {"label": "DESIMALTALL", "value": "FLOAT"},
                    {"label": "DATOTID", "value": "DATETIME"},
                    {"label": "BOOLSK", "value": "BOOLEAN"},
                ],
            },
            "direct_person_identifying": {
                "options": [
                    {"label": "Ja", "value": True},
                    {"label": "Nei", "value": False},
                ],
            },
            "temporality_type": {"options": [{"label": "FAST", "value": "FIXED"}]},
        }

    Args:
        language (SupportedLanguages): The language for metadata entry selected by the user.

    Returns:
        Data structure with options for all dropdowns.

    """
    options: list[dict[str, object]] = []
    for field_type in DISPLAYED_DROPDOWN_VARIABLES_TYPES:
        value = (
            get_boolean_options_for_language(language)
            if field_type is bool
            else get_options_for_language(language, field_type)
        )
        options.append({"options": value})
    return dict(zip(DISPLAYED_DROPDOWN_VARIABLES_METADATA, options, strict=True))


def update_variable_table_language(
    language: SupportedLanguages,
) -> tuple[list[dict], bool, str]:
    """Get data in the relevant language."""
    state.current_metadata_language = language
    logger.debug("Updated variable table language: %s", language.name)
    return (
        [
            get_display_values(
                v,
                state.current_metadata_language,
            )
            for v in state.metadata.meta.variables
        ],
        False,  # Don't show validation error
        "",  # No validation explanation needed
    )
