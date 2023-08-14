import dash_bootstrap_components as dbc
from dash import dcc, html

from datadoc.frontend.Builders import make_ssb_button
from datadoc.frontend.callbacks.dataset import get_dataset_path

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
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Input(
                                        value=get_dataset_path(),
                                        size="60",
                                        id="dataset-path-input",
                                    ),
                                    align="center",
                                    width="auto",
                                ),
                                dbc.Col(
                                    make_ssb_button(
                                        text="Åpne",
                                        icon_class="bi bi-folder2-open",
                                        button_id="open-button",
                                    ),
                                    width=1,
                                ),
                            ]
                        )
                    ),
                    dbc.Col(
                        make_ssb_button(
                            text="Lagre",
                            icon_class="bi bi-save",
                            button_id="save-button",
                        ),
                        width=1,
                    ),
                ],
                justify="between",
            )
        ],
    )
