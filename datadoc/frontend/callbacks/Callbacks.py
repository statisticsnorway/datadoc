import logging
from typing import Any, Dict, List, Optional, Tuple
from pydantic import ValidationError
from datadoc_model import Model
from dash import Dash, Output, Input, ctx, ALL

import datadoc.state as state
from datadoc.Enums import SupportedLanguages
from datadoc.utils import get_display_values
from datadoc.frontend.fields.DisplayDataset import (
    MULTIPLE_LANGUAGE_DATASET_METADATA,
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
    DisplayDatasetMetadata,
)
from datadoc.frontend.fields.DisplayVariables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
    VariableIdentifiers,
)
from datadoc.frontend.Builders import (
    DATASET_METADATA_INPUT,
)

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
    updated_row_id = None
    updated_column_id = None
    new_value = None
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
    try:
        if (
            metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA
            and type(value) is str
        ):
            value = find_existing_language_string(
                state.metadata.meta.dataset, value, metadata_identifier
            )

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


def update_dataset_metadata_language(language: SupportedLanguages) -> List[Any]:
    """Update the global language setting with the chosen language.
    Return new values for ALL the dataset metadata inputs to allow
    editing of strings in the chosen language"""

    state.current_metadata_language = language
    # The order of this list MUST match the order of display components, as defined
    # in dataset_variables in DataDocDash.py
    displayed_dataset_metadata: List[DisplayDatasetMetadata] = (
        OBLIGATORY_EDITABLE_DATASET_METADATA
        + OPTIONAL_DATASET_METADATA
        + NON_EDITABLE_DATASET_METADATA
    )
    logger.debug(f"Updated language: {state.current_metadata_language.name}")
    return [
        m.value_getter(state.metadata.meta.dataset, m.identifier)
        for m in displayed_dataset_metadata
    ]


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
        Output(
            {"type": DATASET_METADATA_INPUT, "id": ALL},
            "value",
        ),
        Input("language-dropdown", "value"),
    )
    def callback_change_language(language: str):
        return update_dataset_metadata_language(SupportedLanguages(language))

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
