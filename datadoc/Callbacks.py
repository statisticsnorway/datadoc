from typing import Dict, List, Tuple

from pydantic import ValidationError

from datadoc.DisplayVariables import VariableIdentifiers
import globals


def accept_variable_metadata_input(
    data: List[Dict], data_previous: List[Dict]
) -> Tuple[List[Dict], bool, str]:
    updated_row_id = None
    updated_column_id = None
    new_value = None
    show_error = False
    error_explanation = ""
    output_data = []
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
            break

    try:
        # Write the value to the variables structure
        setattr(
            globals.metadata.variables_metadata[updated_row_id],
            updated_column_id,
            new_value,
        )
    except ValidationError as e:
        show_error = True
        error_explanation = f"`{e}`"
        output_data = data_previous
        print(error_explanation)
    else:
        output_data = data
        print(f"Successfully updated {updated_row_id} with {new_value}")

    return output_data, show_error, error_explanation
