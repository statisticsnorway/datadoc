"""Components and layout which are not inside a tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import dcc
from dash import html

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import get_dataset_path
from datadoc.utils import get_app_version

COLORS = {"dark_1": "#F0F8F9", "green_1": "#ECFEED", "green_4": "#00824D"}

header = ssb.Header(
    [ssb.Title("DataDoc", size=1, id="main-title", className="main-title")],
    className="datadoc-header",
)

progress_bar = dbc.CardBody(
    children=[dbc.Progress(id="progress-bar", color=COLORS["green_4"], value=40)],
    className="progress-bar-wrapper",
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


def build_controls_bar() -> html.Section:
    """Build the Controls Bar.

    This contains:
    - A text input to specify the path to a dataset
    - A button to open a dataset
    - A button to save metadata to disk
    """
    return html.Section(
        [
            ssb.Input(
                label="Filsti",
                value=get_dataset_path(),
                className="file-path-input",
                id="dataset-path-input",
            ),
            ssb.Button(
                children=["Åpne fil"],
                id="open-button",
                className="file-open-button",
            ),
            ssb.Button(
                children=["Lagre metadata"],
                id="save-button",
                className="file-save-button",
            ),
        ],
        className="control-bar-section",
    )
