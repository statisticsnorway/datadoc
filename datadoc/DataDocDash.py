import argparse
import re
from typing import Any, Dict, List, Tuple, Type

import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, State, ctx, dash_table, dcc, html
from datadoc.Enums import SupportedLanguages

import datadoc.globals as globals
from datadoc.Callbacks import (
    accept_dataset_metadata_input,
    accept_variable_metadata_input,
)
from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.frontend.DisplayVariables import DISPLAY_VARIABLES
from datadoc.frontend.DisplayDataset import (
    DISPLAY_DATASET,
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
    DatasetIdentifiers,
    DisplayDatasetMetadata,
)
from datadoc.utils import running_in_notebook


DATASET_METADATA_INPUT = "dataset-metadata-input"
COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}


def main(dash_class: Type[Dash], dataset_path: str) -> Dash:

    globals.metadata = DataDocMetadata(dataset_path)
    meta = globals.metadata.meta.dataset

    app = dash_class(
        name="DataDoc", external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
    )

    def make_dataset_metadata_accordion_item(
        title: str,
        metadata_inputs: List[DisplayDatasetMetadata],
    ) -> dbc.AccordionItem:
        return dbc.AccordionItem(
            title=title,
            children=[
                dbc.Row(
                    [
                        dbc.Col(html.Label(i.display_name)),
                        dbc.Col(
                            i.component(
                                placeholder=i.description,
                                disabled=not i.editable,
                                value=i.value_getter(meta, i.identifier),
                                id={
                                    "type": DATASET_METADATA_INPUT,
                                    "id": i.identifier,
                                },
                                **i.extra_kwargs,
                                **(i.options or {}),
                            ),
                            width=5,
                        ),
                        dbc.Col(width=4),
                    ]
                )
                for i in metadata_inputs
            ],
        )

    def make_ssb_styled_tab(label: str, content: dbc.Container) -> dbc.Tab:
        return dbc.Tab(
            label=label,
            # Replace all whitespace with dashes
            tab_id=re.sub(r"\s+", "-", label.lower()),
            label_class_name="ssb-tabs navigation-item",
            label_style={"margin-left": "10px", "margin-right": "10px"},
            style={"padding": "4px"},
            children=content,
        )

    def make_ssb_warning_alert(
        alert_identifier: str, title: str, content_identifier: str
    ) -> dbc.Alert:
        return dbc.Alert(
            id=alert_identifier,
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
                                    title,
                                ),
                                dcc.Markdown(
                                    id=content_identifier,
                                ),
                            ]
                        ),
                    ],
                )
            ],
            color="danger",
        )

    dataset_details = make_ssb_styled_tab(
        "Datasett",
        dbc.Container(
            [
                dbc.Row(html.H2("Datasett detaljer", className="ssb-title")),
                dbc.Accordion(
                    always_open=True,
                    children=[
                        make_dataset_metadata_accordion_item(
                            "Obligatorisk",
                            OBLIGATORY_EDITABLE_DATASET_METADATA,
                        ),
                        make_dataset_metadata_accordion_item(
                            "Valgfritt",
                            OPTIONAL_DATASET_METADATA,
                        ),
                        make_dataset_metadata_accordion_item(
                            "Maskingenerert",
                            NON_EDITABLE_DATASET_METADATA,
                        ),
                    ],
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
                        data=[v.dict() for v in globals.metadata.meta.variables],
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
                            v.identifier: v.description
                            for v in DISPLAY_VARIABLES.values()
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

    progress_bar = dbc.CardBody(
        style={"padding": "4px"},
        children=[dbc.Progress(id="progress-bar", color=COLORS["green_4"], value=40)],
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
                            id="save-button",
                        ),
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="language-dropdown",
                            placeholder="Velg språk",
                            value=globals.CURRENT_METADATA_LANGUAGE.value,
                            className="ssb-dropdown",
                            options=[
                                {"label": i.name, "value": i.value}
                                for i in SupportedLanguages
                            ],
                        ),
                        align="end",
                        width="auto",
                    ),
                ]
            )
        ],
    )
    dataset_validation_error = make_ssb_warning_alert(
        "dataset-validation-error",
        "Failed validation",
        "dataset-validation-explanation",
    )

    variables_validation_error = make_ssb_warning_alert(
        "variables-validation-error",
        "Failed validation",
        "variables-validation-explanation",
    )

    success_toast = dbc.Alert(
        id="success-message",
        is_open=False,
        dismissable=True,
        fade=True,
        class_name="ssb-dialog",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        width=3,
                        children=[
                            html.Div(
                                className="ssb-dialog icon-panel",
                                children=[
                                    html.I(
                                        className="bi bi-check-circle",
                                    ),
                                ],
                            )
                        ],
                    ),
                    dbc.Col(
                        [
                            html.H5(
                                "Successfuly saved metadata",
                            ),
                        ]
                    ),
                ],
                align="center",
            )
        ],
        color="success",
    )

    app.layout = dbc.Container(
        style={"padding": "4px"},
        children=[
            header,
            progress_bar,
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
            variables_validation_error,
            dataset_validation_error,
            success_toast,
        ],
    )

    @app.callback(
        Output("progress-bar", "value"),
        Output("progress-bar", "label"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        Input("variables-table", "data"),
    )
    def callback_update_progress(value, data) -> Tuple[int, str]:
        completion = globals.metadata.meta.percent_complete
        return completion, f"{completion}%"

    @app.callback(
        Output("success-message", "is_open"),
        Input("save-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(n_clicks):
        if n_clicks and n_clicks > 0:
            # Write the final completion percentage to the model
            globals.metadata.meta.percentage_complete = (
                globals.metadata.meta.percent_complete
            )
            globals.metadata.write_metadata_document()
            return True
        else:
            return False

    @app.callback(
        Output(
            {"type": DATASET_METADATA_INPUT, "id": ALL},
            "value",
        ),
        Input("language-dropdown", "value"),
        prevent_initial_call=True,
    )
    def callback_change_language(language):
        globals.CURRENT_METADATA_LANGUAGE = SupportedLanguages(language)
        print(f"Updated language: {globals.CURRENT_METADATA_LANGUAGE.name}")
        displayed_dataset_metadata: List[DisplayDatasetMetadata] = (
            OBLIGATORY_EDITABLE_DATASET_METADATA
            + OPTIONAL_DATASET_METADATA
            + NON_EDITABLE_DATASET_METADATA
        )
        return [
            m.value_getter(globals.metadata.meta.dataset, m.identifier)
            for m in displayed_dataset_metadata
        ]

    @app.callback(
        Output("dataset-validation-error", "is_open"),
        Output("dataset-validation-explanation", "children"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(value: Any) -> Tuple[bool, str]:
        print(value)
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
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_input(
        data: List[Dict], data_previous: List[Dict]
    ) -> Tuple[List[Dict], bool, str]:
        return accept_variable_metadata_input(data, data_previous)

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", help="Specify the path to a dataset")
    args = parser.parse_args()

    # Use example dataset if nothing specified
    dataset = args.dataset_path or "./klargjorte_data/person_data_v1.parquet"

    if running_in_notebook():
        from jupyter_dash import JupyterDash

        app = main(JupyterDash, dataset)
        app.run_server(mode="inline")
    else:
        # Assume running in server mode is better (largely for development purposes)
        print("Starting in development mode")
        app = main(Dash, dataset)
        app.run_server(debug=True)
