import itertools
import os
from jupyter_dash import JupyterDash
from dash import dash_table, html, Input, Output, dcc
from dash.development.base_component import Component
from pydantic import ValidationError
from flask import send_from_directory
from typing import Type

from datadoc import DataDocMetadata
from datadoc.Model import DataDocVariable, Datatype, VariableRole

variables = DataDocMetadata("./klargjorte_data/person_data_v1.parquet").meta[
    "variables"
]

app = JupyterDash(__name__)

colors = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

# Display only the first 6 variables
display_variable_metadata = []
for variable in variables:
    display_variable_metadata.append(dict(itertools.islice(variable.items(), 6)))


def make_input_element(
    label: str, placeholder: str, input_class: Type[Component], input_type: str = "text"
):
    return html.Div(
        style={"backgroundColor": colors["green_1"], "padding": "4px"},
        children=[
            html.Label(label),
            input_class(
                placeholder=placeholder,
                type=input_type,
            ),
        ],
    )


dataset_short_name = make_input_element(
    "Kort Navn", "Et teknisk navn, ofte lik filnavnet", dcc.Input, "text"
)
dataset_name = make_input_element(
    "Navn", "Beskrivende navn for datasettet", dcc.Input, "text"
)
# dataset_description = make_input_element(
#     "Beskrivelse",
#     "Beskriv: Hva datasettet er egnet til, hvor dataen kommer fra osv",
#     dcc.Textarea,
#     "text",
# )
dataset_version = make_input_element("Versjon", "1", dcc.Input, "number")

dataset_details = html.Div(
    children=[
        html.H2("Datasett detaljer", className="ssb-title"),
        dataset_short_name,
        dataset_name,
        dcc.Dropdown(className="ssb-dropdown"),
        dataset_version,
    ]
)

variables_table = html.Div(
    children=[
        html.H2("Variabel detaljer", className="ssb-title"),
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
                {"name": "Definition URI", "id": "definitionUri"},
            ],
            editable=True,
            dropdown={
                "dataType": {
                    "options": [{"label": i.name, "value": i.name} for i in Datatype]
                },
                "variableRole": {
                    "options": [
                        {"label": i.name, "value": i.name} for i in VariableRole
                    ]
                },
            },
        ),
    ]
)

validation_error_dialog = html.Dialog(
    id="validation-error",
    open=True,
    hidden=False,
    children=[dcc.Markdown(id="validation-explanation")],
)

app.layout = html.Div(
    style={"width": "50%", "padding": "4px"},
    children=[
        html.Div(
            [
                html.Link(rel="stylesheet", href="/assets/bundle.css"),
                html.H1("DataDoc", className="ssb-title", style={"color": "white"}),
            ],
            style={"backgroundColor": colors["green_4"], "padding": "4px"},
        ),
        dataset_details,
        variables_table,
        validation_error_dialog,
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
    output_data = []
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
        elif updated_column_id == "definitionUri":
            validated_data = DataDocVariable(definition_uri=new_value)
        else:
            validated_data = None
            print("Unexpected type")
    except ValidationError as e:
        show_error = True
        error_explanation = f"Failed validation: `{e}`"
        output_data = data_previous
        print(error_explanation)
    else:
        output_data = data
        print(f"Success: {validated_data}")

    # IF NOT: Return in which way it is not valid
    # IF IT IS: Return the input data unchanged
    return output_data, not show_error, error_explanation


@app.server.route("/assets/<path:path>")
def assets_file(path):
    assets_folder = os.path.join(os.getcwd(), "assets")
    return send_from_directory(assets_folder, path)


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == "__main__":
    app.run_server(debug=True)
