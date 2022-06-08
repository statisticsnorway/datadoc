import itertools
from jupyter_dash import JupyterDash
from dash import dash_table, html, Input, Output

import DataDoc as dd

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
    ]
)


@app.callback(
    Output("variables-table", "data"),
    Input("variables-table", "data"),
    Input("variables-table", "data_previous"),
)
def validate_input(data, data_previous):
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
    # IF NOT: Return in which way it is not valid
    # IF IT IS: Return the input data unchanged
    return data


if __name__ == "__main__":
    app.run_server(debug=True)
