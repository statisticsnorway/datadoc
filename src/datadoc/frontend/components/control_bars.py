"""Components and layout which are not inside a tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import get_dataset_path
from datadoc.frontend.components.builders import build_ssb_button
from datadoc.utils import get_app_version

COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

header = dbc.CardBody(
    dbc.Row(
        children=[
            html.H1("DataDoc", className="ssb-title", style={"color": "white"}),
        ],
    ),
    style={"backgroundColor": COLORS["green_4"]},
)

progress_bar = dbc.CardBody(
    style={"padding": "4px"},
    children=[dbc.Progress(id="progress-bar", color=COLORS["green_4"], value=40)],
)


def build_language_dropdown() -> dbc.Row:
    """Build the language dropdown."""
    return dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    html.P(f"v{get_app_version()}", className="small"),
                    align="end",
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
                    align="center",
                    width="auto",
                ),
            ],
            justify="between",
        ),
    )


def build_controls_bar() -> dbc.CardBody:
    """Build the Controls Bar.

    This contains:
    - A text input to specify the path to a dataset
    - A button to open a dataset
    - A button to save metadata to disk
    """
    return dbc.CardBody(
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Input(
                                        value=get_dataset_path(),
                                        size="50",
                                        placeholder="Sti til datasettet f.eks 'gs://my-bucket/my-dataset.parquet'",
                                        id="dataset-path-input",
                                    ),
                                    align="center",
                                    width="auto",
                                ),
                                dbc.Col(
                                    build_ssb_button(
                                        text="Åpne fil",
                                        icon_class="bi bi-folder2-open",
                                        button_id="open-button",
                                    ),
                                    width=2,
                                ),
                            ],
                        ),
                        width=6,
                    ),
                    dbc.Col(),
                    dbc.Col(
                        build_ssb_button(
                            text="Lagre metadata",
                            icon_class="bi bi-save",
                            button_id="save-button",
                        ),
                        width=2,
                    ),
                ],
                justify="between",
            ),
        ],
    )
