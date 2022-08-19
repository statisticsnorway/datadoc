import re

import dash_bootstrap_components as dbc
from dash import dcc, html


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
