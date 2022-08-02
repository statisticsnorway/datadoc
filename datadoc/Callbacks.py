from typing import Any, Dict, List, Optional, Tuple
from pydantic import ValidationError
from datadoc_model.Enums import SupportedLanguages
from datadoc_model import Model

import datadoc.state as state
from datadoc.utils import get_display_values
from datadoc.frontend.DisplayDataset import (
    MULTIPLE_LANGUAGE_DATASET_METADATA,
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
    DisplayDatasetMetadata,
)
from datadoc.frontend.DisplayVariables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
    VariableIdentifiers,
)


def store_language_string(
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
            print(
                f"Row: {updated_row_id} Column: {updated_column_id} New value: {new_value}"
            )
            break  # We're only interested in one change so we break here

    if update_diff:
        try:
            if (
                updated_column_id in MULTIPLE_LANGUAGE_DATASET_METADATA
                and type(new_value) is str
            ):
                new_value = store_language_string(
                    state.metadata.variables_lookup[updated_row_id],
                    new_value,
                    updated_column_id,
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
            print(error_explanation)
        else:
            print(f"Successfully updated {updated_row_id} with {new_value}")

    return output_data, show_error, error_explanation


def accept_dataset_metadata_input(
    value: Any, metadata_identifier: str
) -> Tuple[bool, str]:
    try:
        if (
            metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA
            and type(value) is str
        ):
            value = store_language_string(
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
        print(error_explanation)
    else:
        show_error = False
        error_explanation = ""
        print(f"Successfully updated {metadata_identifier} with {value}")

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
    print(f"Updated language: {state.current_metadata_language.name}")
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
    print(f"Updated variable table language: {language.name}")
    return new_data, False, ""
