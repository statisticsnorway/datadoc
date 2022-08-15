import logging
from typing import Any, Dict, List, Optional, Tuple

from dash import ALL, Dash, Input, Output, ctx
from datadoc_model import Model
from datadoc_model.Enums import SupportedLanguages
from datadoc_model.LanguageStringsEnum import LanguageStringsEnum
from pydantic import ValidationError

import datadoc.state as state
from datadoc.frontend.components.DatasetTab import DATASET_METADATA_INPUT
from datadoc.frontend.fields.DisplayDataset import (
    DISPLAYED_DATASET_METADATA,
    DISPLAYED_DROPDOWN_DATASET_ENUMS,
    DISPLAYED_DROPDOWN_DATASET_METADATA,
    MULTIPLE_LANGUAGE_DATASET_METADATA,
)
from datadoc.frontend.fields.DisplayVariables import (
    DISPLAYED_DROPDOWN_VARIABLES_METADATA,
    DISPLAYED_DROPDOWN_VARIABLES_TYPES,
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
    VariableIdentifiers,
)
from datadoc.utils import get_display_values

logger = logging.getLogger(__name__)


def find_existing_language_string(
    metadata_model_object: "Model.DataDocBaseModel",
    value: str,
    metadata_identifier: str,
) -> Optional[Model.LanguageStrings]:
    # In this case we need to set the string to the correct language code
    language_strings = getattr(metadata_model_object, metadata_identifier)
    if language_strings is None:
        # This means that no strings have been saved yet so we need to construct
        # a new LanguageStrings object
        language_strings = Model.LanguageStrings(
            **{state.current_metadata_language.value: value}
        )
    else:
        # In this case there's an existing object so we save this string
        # to the current language
        setattr(language_strings, state.current_metadata_language.value, value)
    return language_strings


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


def accept_dataset_metadata_input(
    value: Any, metadata_identifier: str
) -> Tuple[bool, str]:
    logger.debug(f"Received update {value = } for {metadata_identifier = }")
    try:
        if (
            metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA
            and type(value) is str
        ):
            value = find_existing_language_string(
                state.metadata.meta.dataset, value, metadata_identifier
            )

        logger.debug(f"Updating {value = } for {metadata_identifier = }")
        # Update the value in the model
        setattr(
            state.metadata.meta.dataset,
            metadata_identifier,
            value,
        )
    except ValidationError as e:
        show_error = True
        error_explanation = f"`{e}`"
        logger.debug("Caught ValidationError:", exc_info=True)
    else:
        show_error = False
        error_explanation = ""
        logger.debug(f"Successfully updated {metadata_identifier} with {value}")

    return show_error, error_explanation


def update_global_language_state(language: SupportedLanguages):
    logger.debug(f"Updating language: {language.name}")
    state.current_metadata_language = language


def update_dataset_metadata_language() -> List[Any]:
    """Return new values for ALL the dataset metadata inputs to allow
    editing of strings in the chosen language"""
    return [
        m.value_getter(state.metadata.meta.dataset, m.identifier)
        for m in DISPLAYED_DATASET_METADATA
    ]


def change_language_dataset_metadata(language):
    update_global_language_state(language)
    return (
        *(
            get_options_for_language(language, e)
            for e in DISPLAYED_DROPDOWN_DATASET_ENUMS
        ),
        update_dataset_metadata_language(),
    )


def get_options_for_language(
    language: SupportedLanguages, enum: LanguageStringsEnum
) -> List[Dict[str, str]]:
    """Generate the list of options based on the currently chosen language"""
    return [
        {
            "label": i.get_value_for_language(language),
            "value": i.name,
        }
        for i in enum
    ]


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


def register_callbacks(app: Dash) -> None:
    @app.callback(
        Output("progress-bar", "value"),
        Output("progress-bar", "label"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        Input("variables-table", "data"),
    )
    def callback_update_progress(value, data) -> Tuple[int, str]:
        completion = state.metadata.percent_complete
        return completion, f"{completion}%"

    @app.callback(
        Output("success-message", "is_open"),
        Input("save-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(n_clicks):
        if n_clicks and n_clicks > 0:
            # Write the final completion percentage to the model
            state.metadata.meta.percentage_complete = state.metadata.percent_complete
            state.metadata.write_metadata_document()
            return True
        else:
            return False

    @app.callback(
        *[
            Output(
                {
                    "type": DATASET_METADATA_INPUT,
                    "id": m.identifier,
                },
                "options",
            )
            for m in DISPLAYED_DROPDOWN_DATASET_METADATA
        ],
        Output(
            {"type": DATASET_METADATA_INPUT, "id": ALL},
            "value",
        ),
        Input("language-dropdown", "value"),
    )
    def callback_change_language_dataset_metadata(language: str):
        return change_language_dataset_metadata(SupportedLanguages(language))

    @app.callback(
        Output("dataset-validation-error", "is_open"),
        Output("dataset-validation-explanation", "children"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(value: Any) -> Tuple[bool, str]:
        # Get the ID of the input that changed. This MUST match the attribute name defined in DataDocDataSet
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"], ctx.triggered_id["id"]
        )

    @app.callback(
        Output("variables-table", "data"),
        Output("variables-validation-error", "is_open"),
        Output("variables-validation-explanation", "children"),
        Input("variables-table", "data"),
        Input("variables-table", "data_previous"),
        Input("language-dropdown", "value"),
        prevent_initial_call=True,
    )
    def callback_variable_table(
        data: List[Dict], data_previous: List[Dict], language: str
    ) -> Tuple[List[Dict], bool, str]:
        if ctx.triggered_id == "language-dropdown":
            return update_variable_table_language(data, SupportedLanguages(language))
        else:
            return accept_variable_metadata_input(data, data_previous)

    @app.callback(
        Output("variables-table", "dropdown"),
        Input("language-dropdown", "value"),
    )
    def callback_variable_table_dropdown_options(language: str):
        language = SupportedLanguages(language)
        return update_variable_table_dropdown_options_for_language(language)
