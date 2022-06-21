import itertools
import os
from jupyter_dash import JupyterDash
from dash import Dash, dash_table, html, Input, Output, dcc
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
from pydantic import ValidationError
from flask import send_from_directory
from typing import Type
import pandas as pd
from datadoc import DataDocMetadata
from datadoc.Model import DataDocVariable, Datatype, VariableRole

# metadata = DataDocMetadata("./klargjorte_data/person_data_v1.parquet").meta
metadata = DataDocMetadata("./datadoc/tests/resources/sasdata.sas7bdat").meta
variables = metadata["variables"]

app = Dash(name="DataDoc", external_stylesheets=[dbc.themes.GRID])

colors = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

df = pd.DataFrame(variables)

dataset_details_inputs = [
    {
        "name": "Kort Navn",
        "input_component": dcc.Input(
            placeholder="Et teknisk navn, ofte lik filnavnet",
            style={"width": "100%"},
            value=metadata["shortName"],
        ),
    },
    {
        "name": "Navn",
        "input_component": dcc.Input(
            placeholder="Beskrivende navn for datasettet", style={"width": "100%"}
        ),
    },
    {
        "name": "Beskrivelse",
        "input_component": dcc.Textarea(
            placeholder="Besrive egenskaper av datasettet", style={"width": "100%"}
        ),
    },
    {
        "name": "Tilstand",
        "input_component": dcc.Dropdown(
            options=["Kildedata", "Inndata", "Klargjorte data", "Utdata"],
            style={"width": "100%"},
        ),
    },
    {
        "name": "Versjon",
        "input_component": dcc.Input(
            placeholder=1,
            type="number",
            style={"width": "100%"},
            value=metadata["version"],
        ),
    },
    {
        "name": "Datasett sti",
        "input_component": dcc.Input(
            placeholder="Sti til datasett fil",
            style={"width": "100%"},
            value=metadata["dataSourcePath"],
        ),
    },
    {
        "name": "Opprettet av",
        "input_component": dcc.Input(
            placeholder="kari.nordman@ssb.no",
            type="email",
            style={"width": "100%"},
            value=metadata["createdBy"],
        ),
    },
    {
        "name": "Opprettet dato",
        "input_component": dcc.Input(
            style={"width": "100%"}, value=metadata["createdDate"]
        ),
    },
]

dataset_details = html.Div(
    style={
        "backgroundColor": colors["green_1"],
        "padding": "4px",
        "display": "inline-block",
        "width": "50%",
        "min-width": "600px",
        "verticalAlign": "top",
    },
    children=[
        dbc.Row(html.H2("Datasett detaljer", className="ssb-title")),
        dbc.Row(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Label(input["name"]), width=3),
                        dbc.Col(input["input_component"]),
                    ]
                )
                for input in dataset_details_inputs
            ]
        ),
    ],
)

variables_table = html.Div(
    children=[
        html.H2("Variabel detaljer", className="ssb-title"),
        dash_table.DataTable(
            id="variables-table",
            data=df[["shortName", "name", "dataType"]].to_dict("records"),
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
    style={"padding": "4px"},
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


if __name__ == "__main__":
    app.run_server(debug=True)
