import dash_bootstrap_components as dbc
import datadoc.state as state
from dash import dcc, html
from datadoc_model.Enums import SupportedLanguages

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


def get_controls_bar() -> dbc.CardBody:
    return dbc.CardBody(
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
