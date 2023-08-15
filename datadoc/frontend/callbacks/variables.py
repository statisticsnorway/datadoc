from __future__ import annotations

import logging

from datadoc_model.Enums import SupportedLanguages
from pydantic import ValidationError

from datadoc import state
from datadoc.frontend.callbacks.utils import (
    find_existing_language_string,
    get_options_for_language,
)
from datadoc.frontend.fields.DisplayVariables import (
    DISPLAYED_DROPDOWN_VARIABLES_METADATA,
    DISPLAYED_DROPDOWN_VARIABLES_TYPES,
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
    VariableIdentifiers,
)
from datadoc.utils import get_display_values

logger = logging.getLogger(__name__)


def get_boolean_options_for_language(language: SupportedLanguages):
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


def get_metadata_field(data, data_previous, active_cell) -> str:
    for i in range(len(data)):
        # First strategy to find which column we're in; diff the current and previous data
        update_diff = list(data[i].items() - data_previous[i].items())
        if update_diff:
            return update_diff[-1][0]

    # When copy/pasting the diff fails, so we fall back to the active cell
    return active_cell["column_id"]


def handle_multi_language_metadata(
    metadata_field,
    new_value,
    updated_row_id,
) -> str | None:
    if type(new_value) is str:
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            new_value,
            metadata_field,
        )
    elif new_value is None:
        # This edge case occurs when the user removes the text in an input field
        # We want to ensure we only remove the content for the current language,
        # not create a new blank object!
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            "",
            metadata_field,
        )
    else:
        return new_value


def accept_variable_metadata_input(
    data: list[dict],
    active_cell: dict,
    data_previous: list[dict],
) -> tuple[list[dict], bool, str]:
    show_error = False
    error_explanation = ""
    output_data = data
    metadata_field = get_metadata_field(data, data_previous, active_cell)

    for row_index in range(len(data)):
        # Update all the variables for this column to ensure we read in the value
        new_value = data[row_index][metadata_field]
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

            logger.debug(
                f"{row_index = } | {updated_row_id = } | {metadata_field = } | {new_value = }",
            )
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
            logger.debug(f"Successfully updated {updated_row_id} with {new_value}")

    return output_data, show_error, error_explanation


def update_variable_table_dropdown_options_for_language(
    language: SupportedLanguages,
) -> dict[str, dict[str, list[dict[str, str]]]]:
    """Retrieves enum options for dropdowns in the Datatable. Handles the
    special case of boolean values which we represent in the Datatable
    with a Dropdown but they're not backed by an Enum.

    Example return structure:
        {'data_type': {'options': [{'label': 'TEKST', 'value': 'STRING'},
                                {'label': 'HELTALL', 'value': 'INTEGER'},
                                {'label': 'DESIMALTALL', 'value': 'FLOAT'},
                                {'label': 'DATOTID', 'value': 'DATETIME'},
                                {'label': 'BOOLSK', 'value': 'BOOLEAN'}]},
        'direct_person_identifying': {'options': [{'label': 'Ja', 'value': True},
                                                {'label': 'Nei', 'value': False}]},
        'temporality_type': {'options': [{'label': 'FAST', 'value': 'FIXED'},
            ...
        }
    """
    options = []
    for field_type in DISPLAYED_DROPDOWN_VARIABLES_TYPES:
        value = (
            get_boolean_options_for_language(language)
            if field_type is bool
            else get_options_for_language(language, field_type)
        )
        options.append({"options": value})
    return dict(zip(DISPLAYED_DROPDOWN_VARIABLES_METADATA, options))


def update_variable_table_language(
    language: SupportedLanguages,
) -> tuple[list[dict], bool, str]:
    state.current_metadata_language = language
    new_data = []
    for v in state.metadata.meta.variables:
        new_data.append(
            get_display_values(
                v,
                state.current_metadata_language,
            ),
        )
    logger.debug(f"Updated variable table language: {language.name}")
    return new_data, False, ""
