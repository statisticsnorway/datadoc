"""Callback functions to do with variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from datadoc import state
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import parse_and_validate_dates
from datadoc.frontend.fields.display_variables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
)
from datadoc.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    from datadoc_model.model import LanguageStringType

logger = logging.getLogger(__name__)


def handle_multi_language_metadata(
    metadata_field: str,
    new_value: MetadataInputTypes | LanguageStringType,
    updated_row_id: str,
) -> MetadataInputTypes | LanguageStringType:
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
    value: MetadataInputTypes,
    variable_short_name: str,
    metadata_field: str,
) -> str | None:
    """Validate and save the value when variable metadata is updated.

    Returns an error message if an exception was raised, otherwise returns None.
    """
    logger.debug(
        "Updating %s, %s with %s",
        metadata_field,
        variable_short_name,
        value,
    )
    try:
        if metadata_field in MULTIPLE_LANGUAGE_VARIABLES_METADATA:
            new_value = handle_multi_language_metadata(
                metadata_field,
                value,
                variable_short_name,
            )
        elif value and metadata_field == VariableIdentifiers.CONTAINS_DATA_FROM.value:
            new_value, _ = parse_and_validate_dates(
                str(value),
                getattr(
                    state.metadata.variables_lookup[variable_short_name],
                    VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
                ),
            )
        elif value and metadata_field == VariableIdentifiers.CONTAINS_DATA_UNTIL.value:
            _, new_value = parse_and_validate_dates(
                getattr(
                    state.metadata.variables_lookup[variable_short_name],
                    VariableIdentifiers.CONTAINS_DATA_FROM.value,
                ),
                str(value),
            )
        elif value == "":
            # Allow clearing non-multiple-language text fields
            new_value = None
        else:
            new_value = value

        # Write the value to the variables structure
        setattr(
            state.metadata.variables_lookup[variable_short_name],
            metadata_field,
            new_value,
        )
    except (ValidationError, ValueError) as e:
        logger.exception(
            "Could not validate %s, %s, %s:",
            metadata_field,
            variable_short_name,
            value,
        )
        return str(e)
    else:
        logger.debug(
            "Successfully updated %s, %s with %s",
            metadata_field,
            variable_short_name,
            value,
        )
        return None
