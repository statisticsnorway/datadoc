"""Components and layout which are not inside a tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import get_dataset_path
from datadoc.utils import get_app_version

COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

# SSB Header with Title
header = ssb.Header(
    [
        ssb.Title("DataDoc", size=1),
    ],
)

progress_bar = dbc.CardBody(
    style={"padding": "4px"},
    children=[dbc.Progress(id="progress-bar", color=COLORS["green_4"], value=40)],
)


# ssb.Dropdown with error - value and options -> callback error
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
                    ssb.Dropdown(
                        id="language-dropdown",
                        searchable=False,
                        header="Velg språk",
                        selectedItem=state.current_metadata_language.value,
                        items=[
                            {"id": i.value, "title": i.name} for i in SupportedLanguages
                        ],
                    ),
                ),
            ],
            justify="between",
        ),
    )


# SSB Input and SSB Button
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
                                    ssb.Input(
                                        value=get_dataset_path(),
                                        id="dataset-path-input",
                                        label="Dataset",
                                    ),
                                    align="center",
                                    width="auto",
                                ),
                                dbc.Col(
                                    ssb.Button("Åpne fil", id="open-button"),
                                ),
                            ],
                        ),
                        width=6,
                    ),
                    dbc.Col(),
                    dbc.Col(
                        ssb.Button("Lagre metadata", id="save-button"),
                    ),
                ],
                justify="between",
            ),
        ],
    )
