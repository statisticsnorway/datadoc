import itertools
from jupyter_dash import JupyterDash
from dash import dash_table, html, Input, Output
from pydantic import ValidationError

import DataDoc as dd
from Model import DataDocVariable, Datatype

variables = dd.DataDocMetadata("./klargjorte_data/person_data_v1.parquet").meta[
    "variables"
]

app = JupyterDash(__name__)

# Display only the first 6 variables
display_variable_metadata = []
for variable in variables:
    display_variable_metadata.append(dict(itertools.islice(variable.items(), 6)))

app.layout = html.Div(
    children=[
        dash_table.DataTable(
            id="variables-table",
            data=display_variable_metadata,
            columns=[
                {"name": "Kort navn", "id": "shortName", "editable": False},
                {
                    "name": "Navn",
                    "id": "name",
                },
                {"name": "Datatype", "id": "dataType", "presentation": "dropdown"},
                {
                    "name": "Variabelens rolle",
                    "id": "variableRole",
                    "presentation": "dropdown",
                },
                {"name": "VarDef ID", "id": "definitionUri"},
            ],
            editable=True,
            dropdown={
                "dataType": {
                    "options": [
                        {"label": i, "value": i}
                        for i in ["STRING", "INTEGER", "FLOAT", "DATETIME", "BOOLEAN"]
                    ]
                },
                "variableRole": {
                    "options": [
                        {"label": i, "value": i}
                        for i in [
                            "IDENTIFIER",
                            "MEASURE",
                            "START_TIME",
                            "STOP_TIME",
                            "ATTRIBUTE",
                        ]
                    ]
                },
            },
        ),
        html.Dialog(
            id="validation-error",
            open=True,
            hidden=False,
            children=[html.P(id="validation-explanation")],
        ),
    ],
)


@app.callback(
    Output("variables-table", "data"),
    Output("validation-error", "hidden"),
    Output("validation-explanation", "children"),
    Input("variables-table", "data"),
    Input("variables-table", "data_previous"),
)
def validate_input(data, data_previous):
    updated_row_id = None
    updated_column_id = None
    new_value = None
    show_error = False
    error_explanation = ""
    # What has changed?
    if data is not None and data_previous is not None:
        for i in range(len(data)):
            update_diff = list(data[i].items() - data_previous[i].items())
            if update_diff:
                print(update_diff)
                updated_row_id = data[i]["shortName"]
                updated_column_id = update_diff[-1][0]
                new_value = update_diff[-1][-1]
                print(
                    f"Row: {updated_row_id} Column: {updated_column_id} New value: {new_value}"
                )
    # Is the change valid?
    try:
        if updated_column_id == "name":
            validated_data = DataDocVariable(name=new_value)
        elif updated_column_id == "dataType":
            validated_data = DataDocVariable(datatype=Datatype[new_value])
        else:
            validated_data = None
            print("Unexpected type")
    except ValidationError as e:
        show_error = True
        error_explanation = str(e)
        print(f"Failed validation: {e}")
    else:
        print(f"Success: {validated_data}")

    # IF NOT: Return in which way it is not valid
    # IF IT IS: Return the input data unchanged
    return data, not show_error, error_explanation


if __name__ == "__main__":
    app.run_server(debug=True)
