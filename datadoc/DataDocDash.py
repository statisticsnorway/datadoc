import argparse
import logging
import os
import re
from typing import Any, Dict, List, Tuple, Type

import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, ctx, dash_table, dcc, html

from datadoc.Enums import SupportedLanguages
import datadoc.state as state
from datadoc.Callbacks import (
    accept_dataset_metadata_input,
    accept_variable_metadata_input,
    update_dataset_metadata_language,
    update_variable_table_language,
)
from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.frontend.DisplayVariables import DISPLAY_VARIABLES
from datadoc.frontend.DisplayDataset import (
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
    DisplayDatasetMetadata,
)
from datadoc.utils import running_in_notebook, get_display_values

logger = logging.getLogger(__name__)


DATASET_METADATA_INPUT = "dataset-metadata-input"
COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}


def build_app(dash_class: Type[Dash], dataset_path: str) -> Dash:

    state.metadata = DataDocMetadata(dataset_path)

    app = dash_class(
        name="DataDoc",
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
        assets_folder=f"{os.path.dirname(__file__)}/assets",
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
                        data=[
                            get_display_values(v, state.current_metadata_language)
                            for v in state.metadata.meta.variables
                        ],
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
                # html.Link(rel="stylesheet", href="assets/bundle.css"),
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
                            searchable=False,
                            value=state.current_metadata_language.value,
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

    return app


def main(dataset_path: str = None):
    if dataset_path is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--dataset-path", help="Specify the path to a dataset")
        args = parser.parse_args()
        # Use example dataset if nothing specified
        dataset = args.dataset_path or "./klargjorte_data/person_data_v1.parquet"
    else:
        dataset = dataset_path

    if running_in_notebook():
        logging.basicConfig(level=logging.WARNING)
        from jupyter_dash import JupyterDash

        JupyterDash.infer_jupyter_proxy_config()
        app = build_app(JupyterDash, dataset)
        app.run_server(mode="inline")
    else:
        logging.basicConfig(level=logging.DEBUG)
        # Assume running in server mode is better (largely for development purposes)
        logger.debug("Starting in development mode")
        app = build_app(Dash, dataset)
        app.run_server(debug=True)


if __name__ == "__main__":
    main()
