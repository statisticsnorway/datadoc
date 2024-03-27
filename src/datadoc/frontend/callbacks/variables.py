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
            "Validation failed for %s, %s, %s:",
            metadata_field,
            variable_short_name,
            value,
        )
        return str(e)
    else:
        if value == "":
            value = None
        logger.debug(
            "Successfully updated %s, %s with %s",
            metadata_field,
            variable_short_name,
            value,
        )
        return None


def accept_variable_metadata_date_input(
    variable_identifier: VariableIdentifiers,
    variable_short_name: str,
    contains_data_from: str,
    contains_data_until: str,
) -> tuple[bool, str, bool, str]:
    """Validate and save date range inputs."""
    message = accept_variable_metadata_input(
        (
            contains_data_from
            if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM
            else contains_data_until
        ),
        variable_short_name,
        variable_identifier,
    )

    try:
        (
            parsed_contains_data_from,
            parsed_contains_data_until,
        ) = parse_and_validate_dates(
            str(
                contains_data_from
                or state.metadata.variables_lookup[
                    variable_short_name
                ].contains_data_from,
            ),
            str(
                contains_data_until
                or state.metadata.variables_lookup[
                    variable_short_name
                ].contains_data_until,
            ),
        )

        # Save both values to the model if they pass validation.
        state.metadata.variables_lookup[
            variable_short_name
        ].contains_data_from = parsed_contains_data_from
        state.metadata.variables_lookup[
            variable_short_name
        ].contains_data_until = parsed_contains_data_until
    except (ValidationError, ValueError) as e:
        logger.exception(
            "Validation failed for %s, %s, %s: %s, %s: %s",
            variable_identifier,
            variable_short_name,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message = str(e)
    else:
        logger.debug(
            "Successfully updated %s, %s, %s: %s, %s: %s",
            variable_identifier,
            variable_short_name,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message = None

    no_error = (False, "")
    if not message:
        # No error to display.
        return no_error + no_error

    error = (True, message)
    return (
        error + no_error
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM
        else no_error + error
    )
