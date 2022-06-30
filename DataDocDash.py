import re

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dash_table, dcc, html
from pydantic import ValidationError

from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.DisplayVariables import DISPLAY_VARIABLES, VariableIdentifiers
from datadoc.Model import DataDocVariable, DataSetState, Datatype

datadoc_metadata = DataDocMetadata("./klargjorte_data/person_data_v1.parquet")
# datadoc_metadata = DataDocMetadata("./datadoc/tests/resources/sasdata.sas7bdat")
metadata = datadoc_metadata.dataset_metadata
variables = datadoc_metadata.variables_metadata

app = Dash(
    name="DataDoc", external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)

COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

dataset_details_inputs = [
    {
        "name": "Kort Navn",
        "input_component": dcc.Input(
            placeholder="Et teknisk navn, ofte lik filnavnet",
            style={"width": "100%"},
            value=metadata.short_name,
            className="ssb-input",
        ),
    },
    {
        "name": "Navn",
        "input_component": dcc.Input(
            placeholder="Beskrivende navn for datasettet",
            style={"width": "100%"},
            value=metadata.name,
            className="ssb-input",
        ),
    },
    {
        "name": "Beskrivelse",
        "input_component": dcc.Textarea(
            placeholder="Besrive egenskaper av datasettet",
            style={"width": "100%"},
            value=metadata.description,
            className="ssb-input",
        ),
    },
    {
        "name": "Tilstand",
        "input_component": dcc.Dropdown(
            placeholder="Velg fra listen",
            options=[
                {"label": label, "value": value}
                for label, value in [
                    ("Kildedata", DataSetState.SOURCE_DATA.name),
                    ("Inndata", DataSetState.INPUT_DATA.name),
                    ("Klargjorte data", DataSetState.PROCESSED_DATA.name),
                    ("Utdata", DataSetState.OUTPUT_DATA.name),
                    ("Statistikk", DataSetState.STATISTIC.name),
                ]
            ],
            style={"width": "100%"},
            className="ssb-dropdown",
        ),
    },
    {
        "name": "Versjon",
        "input_component": dcc.Input(
            placeholder=1,
            type="number",
            style={"width": "100%"},
            value=metadata.version,
            className="ssb-input",
        ),
    },
    {
        "name": "Datasett sti",
        "input_component": dcc.Input(
            placeholder="Sti til datasett fil",
            style={"width": "100%"},
            value=metadata.data_source_path,
            className="ssb-input",
        ),
    },
    {
        "name": "Opprettet av",
        "input_component": dcc.Input(
            placeholder="kari.nordman@ssb.no",
            type="email",
            style={"width": "100%"},
            value=metadata.created_by,
            className="ssb-input",
        ),
    },
    {
        "name": "Opprettet dato",
        "input_component": dcc.Input(
            style={"width": "100%"},
            value=metadata.created_date,
            className="ssb-input",
        ),
    },
]


def make_ssb_styled_tab(label: str, content: dbc.Container) -> dbc.Tab:
    return dbc.Tab(
        label=label,
        # Replace all whitespace with dashes
        tab_id=re.sub(r"\s+", "-", label.lower()),
        label_class_name="ssb-tabs navigation-item",
        label_style={"margin-left": "10px", "margin-right": "10px"},
        style={"backgroundColor": COLORS["green_1"], "padding": "4px"},
        children=content,
    )


dataset_details = make_ssb_styled_tab(
    "Datasett",
    dbc.Container(
        [
            dbc.Row(html.H2("Datasett detaljer", className="ssb-title")),
            dbc.Row(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.Label(input["name"])),
                            dbc.Col(input["input_component"], width=4),
                            dbc.Col(width=6),
                        ]
                    )
                    for input in dataset_details_inputs
                ]
            ),
        ],
    ),
)

variables_table = make_ssb_styled_tab(
    "Variabler",
    dbc.Container(
        children=[
            dbc.Row(html.H2("Variabel detaljer", className="ssb-title")),
            dbc.Row(
                dash_table.DataTable(
                    id="variables-table",
                    # Populate fields with known values
                    data=[v.export_for_datatable() for v in variables],
                    # Define columns based on the information in DISPLAY_VARIABLES
                    columns=[
                        {
                            "name": variable.display_name,
                            "id": variable.identifier,
                            "editable": variable.editable,
                            "presentation": variable.presentation,
                            "hideable": variable.editable,
                        }
                        for variable in DISPLAY_VARIABLES.values()
                    ],
                    # Non-obligatory variables are hidden by default
                    hidden_columns=[
                        v.identifier
                        for v in DISPLAY_VARIABLES.values()
                        if v.obligatory is False
                    ],
                    # Include tooltips for all columns
                    tooltip_header={
                        v.identifier: v.description for v in DISPLAY_VARIABLES.values()
                    },
                    editable=True,
                    # Enable sorting and pagination
                    sort_action="native",
                    page_action="native",
                    # Populate the options for all dropdown values
                    dropdown={
                        v.identifier: v.options
                        for v in DISPLAY_VARIABLES.values()
                        if v.options
                    },
                )
            ),
        ],
    ),
)

header = dbc.CardBody(
    dbc.Row(
        children=[
            html.Link(rel="stylesheet", href="/assets/bundle.css"),
            html.H1("DataDoc", className="ssb-title", style={"color": "white"}),
        ],
    ),
    style={"backgroundColor": COLORS["green_4"]},
)

controls_bar = dbc.CardBody(
    style={"padding": "4px"},
    children=[
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        [
                            html.I(
                                className="bi bi-save",
                                style={"padding-right": "10px"},
                            ),
                            "   Lagre",
                        ],
                        class_name="ssb-btn primary-btn",
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        placeholder="Velg språk",
                        className="ssb-dropdown",
                        options=["Norsk Bokmål", "Nynorsk", "English"],
                        value="Norsk Bokmål",
                        disabled=True,
                    ),
                    align="end",
                    width="auto",
                ),
            ]
        )
    ],
)

validation_error = dbc.Alert(
    id="validation-error",
    is_open=False,
    dismissable=True,
    fade=True,
    class_name="ssb-dialog warning",
    children=[
        dbc.Row(
            [
                dbc.Col(
                    width=1,
                    children=[
                        html.Div(
                            className="ssb-dialog warning icon-panel",
                            children=[
                                html.I(
                                    className="bi bi-exclamation-triangle",
                                ),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    [
                        html.H5(
                            "Failed validation",
                        ),
                        dcc.Markdown(
                            id="validation-explanation",
                        ),
                    ]
                ),
            ]
        )
    ],
    color="danger",
)

app.layout = dbc.Container(
    style={"padding": "4px"},
    children=[
        header,
        controls_bar,
        dbc.CardBody(
            style={"padding": "4px"},
            children=[
                dbc.Tabs(
                    id="tabs",
                    class_name="ssb-tabs",
                    children=[
                        dataset_details,
                        variables_table,
                    ],
                ),
            ],
        ),
        validation_error,
    ],
)


@app.callback(
    Output("variables-table", "data"),
    Output("validation-error", "is_open"),
    Output("validation-explanation", "children"),
    Input("variables-table", "data"),
    Input("variables-table", "data_previous"),
    prevent_initial_call=True,
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
                print(data[i])
                updated_row_id = data[i][VariableIdentifiers.SHORT_NAME.value]
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
    except ValidationError as e:
        show_error = True
        error_explanation = f"`{e}`"
        output_data = data_previous
        print(error_explanation)
    else:
        if validated_data is not None:
            output_data = data
            print(f"Success: {validated_data}")

    # IF NOT: Return in which way it is not valid
    # IF IT IS: Return the input data unchanged
    return output_data, show_error, error_explanation


if __name__ == "__main__":
    app.run_server(debug=True)
