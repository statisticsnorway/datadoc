from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

import datadoc.globals as globals
from datadoc.frontend.DisplayVariables import VariableIdentifiers


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
            # Write the value to the variables structure
            setattr(
                globals.metadata.variables_lookup[updated_row_id],
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
        # Update the value in the model
        setattr(
            globals.metadata.meta.dataset,
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
