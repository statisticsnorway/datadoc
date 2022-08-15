import logging
from typing import Dict, List, Optional, Tuple

from datadoc_model.Enums import SupportedLanguages
from pydantic import ValidationError

import datadoc.state as state
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


def accept_variable_metadata_input(
    data: List[Dict], data_previous: List[Dict]
) -> Tuple[List[Dict], bool, str]:
    updated_row_id: str = ""
    updated_column_id: str = ""
    new_value: Optional[str] = None
    show_error = False
    error_explanation = ""
    output_data = data
    update_diff = []
    # What has changed?
    for i in range(len(data)):
        update_diff = list(data[i].items() - data_previous[i].items())
        if update_diff:
            updated_row_id = data[i][VariableIdentifiers.SHORT_NAME.value]
            updated_column_id = update_diff[-1][0]
            new_value = update_diff[-1][-1]
            break  # We're only interested in one change so we break here

    if update_diff:
        try:
            if updated_column_id in MULTIPLE_LANGUAGE_VARIABLES_METADATA:
                if type(new_value) is str:
                    new_value = find_existing_language_string(
                        state.metadata.variables_lookup[updated_row_id],
                        new_value,
                        updated_column_id,
                    )
                elif new_value is None:
                    # This edge case occurs when the user removes the text in an input field
                    # We want to ensure we only remove the content for the current language,
                    # not create a new blank object!
                    new_value = find_existing_language_string(
                        state.metadata.variables_lookup[updated_row_id],
                        "",
                        updated_column_id,
                    )

            logger.debug(
                f"Row: {updated_row_id} Column: {updated_column_id} New value: {new_value}"
            )
            # Write the value to the variables structure
            setattr(
                state.metadata.variables_lookup[updated_row_id],
                updated_column_id,
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
) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
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
    data: List[Dict],
    language: SupportedLanguages,
) -> Tuple[List[Dict], bool, str]:
    state.current_metadata_language = language
    new_data = []
    for row in data:
        new_data.append(
            get_display_values(
                state.metadata.variables_lookup[
                    row[VariableIdentifiers.SHORT_NAME.value]
                ],
                state.current_metadata_language,
            )
        )
    logger.debug(f"Updated variable table language: {language.name}")
    return new_data, False, ""
