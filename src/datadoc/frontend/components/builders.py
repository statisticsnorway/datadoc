"""Factory functions for different components are defined here."""

import re
from dataclasses import dataclass
from enum import Enum
from enum import auto

import dash_bootstrap_components as dbc
from dash import html


class AlertTypes(Enum):
    """Types of alerts."""

    SUCCESS = auto()
    WARNING = auto()


@dataclass
class AlertType:
    """Attributes of a concrete alert type."""

    alert_class_name: str
    color: str

    @staticmethod
    def get_type(alert_type: AlertTypes) -> "AlertType":
        """Get a concrete alert type based on the given enum values."""
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


def build_ssb_styled_tab(label: str, content: dbc.Container) -> dbc.Tab:
    """Make a Dash Tab according to SSBs Design System."""
    return dbc.Tab(
        label=label,
        # Replace all whitespace with dashes
        tab_id=re.sub(r"\s+", "-", label.lower()),
        label_class_name="ssb-tabs navigation-item",
        label_style={"margin-left": "10px", "margin-right": "10px"},
        style={"padding": "4px"},
        children=content,
    )


def build_ssb_alert(
    alert_type: AlertTypes,
    alert_identifier: str,
    title: str,
    content_identifier: str,
) -> dbc.Alert:
    """Make a Dash Alert according to SSBs Design System."""
    alert = AlertType.get_type(alert_type)
    return dbc.Alert(
        id=alert_identifier,
        is_open=False,
        dismissable=True,
        fade=True,
        color=alert.color,
        duration=5000 if alert_type == AlertTypes.SUCCESS else None,
        children=[
            html.H5(
                title,
            ),
            html.P(
                id=content_identifier,
            ),
        ],
    )


def build_ssb_button(text: str, icon_class: str, button_id: str) -> dbc.Button:
    """Make a Dash Button according to SSBs Design System."""
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
