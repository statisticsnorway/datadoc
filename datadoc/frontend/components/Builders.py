import re
from dataclasses import dataclass
from enum import Enum, auto

import dash_bootstrap_components as dbc
from dash import dcc, html


class AlertTypes(Enum):
    SUCCESS = auto()
    WARNING = auto()


@dataclass
class AlertType:
    alert_class_name: str
    color: str

    @staticmethod
    def get_type(alert_type: AlertTypes) -> "AlertType":
        return ALERT_TYPES[alert_type]


ALERT_TYPES = {
    AlertTypes.WARNING: AlertType(
        alert_class_name="ssb-dialog warning",
        color="danger",
    ),
    AlertTypes.SUCCESS: AlertType(
        alert_class_name="ssb-dialog",
        color="success",
    ),
}


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


def make_ssb_alert(
    alert_type: AlertTypes, alert_identifier: str, title: str, content_identifier: str
) -> dbc.Alert:
    alert = AlertType.get_type(alert_type)
    return dbc.Alert(
        id=alert_identifier,
        is_open=False,
        dismissable=True,
        fade=True,
        class_name=alert.alert_class_name,
        color=alert.color,
        duration=5000,
        children=[
            html.H5(
                title,
            ),
            dcc.Markdown(
                id=content_identifier,
            ),
        ],
    )


def make_ssb_button(text: str, icon_class: str, button_id: str) -> dbc.Button:
    return dbc.Button(
        [
            html.I(
                className=icon_class,
                style={"padding-right": "10px"},
            ),
            f"   {text}",
        ],
        class_name="ssb-btn primary-btn",
        id=button_id,
    )
