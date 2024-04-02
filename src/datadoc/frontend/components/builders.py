"""Factory functions for different components are defined here."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc.frontend.fields.display_base import DatasetFieldTypes
from datadoc.frontend.fields.display_base import VariablesFieldTypes

if TYPE_CHECKING:
    from datadoc_model import model


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
    def get_type(alert_type: AlertTypes) -> AlertType:
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


def build_ssb_styled_tab(label: str, content: html.Article) -> dbc.Tab:
    """Make a Dash Tab according to SSBs Design System."""
    return dbc.Tab(
        label=label,
        # Replace all whitespace with dashes
        tab_id=re.sub(r"\s+", "-", label.lower()),
        label_class_name="ssb-tabs navigation-item workspace-tab-label",
        children=content,
        className="workspace-tab",
    )


def build_ssb_alert(  # noqa: PLR0913 not immediately obvious how to improve this
    alert_type: AlertTypes,
    alert_identifier: str,
    title: str,
    content_identifier: str,
    message: str | None = None,
    *,
    start_open: bool = False,
) -> dbc.Alert:
    """Make a Dash Alert according to SSBs Design System."""
    alert = AlertType.get_type(alert_type)
    return dbc.Alert(
        id=alert_identifier,
        is_open=start_open,
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
                children=message,
            ),
        ],
        style={"width": "70%"},
    )


def build_input_field_section(
    metadata_fields: list[VariablesFieldTypes],
    variable: model.Variable,
    language: str,
) -> dbc.Form:
    """Create form with input fields for variable workspace."""
    return dbc.Form(
        [
            i.render(
                {
                    "type": VARIABLES_METADATA_INPUT,
                    "variable_short_name": variable.short_name,
                    "id": i.identifier,
                },
                language,
                variable,
            )
            for i in metadata_fields
        ],
        id=VARIABLES_METADATA_INPUT,
        className="edit-section-form",
    )


def build_edit_section(
    metadata_inputs: list,
    title: str,
    variable: model.Variable,
    language: str,
) -> html.Section:
    """Create input section for variable workspace."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            build_input_field_section(metadata_inputs, variable, language),
        ],
        className="edit-section",
    )


def build_ssb_accordion(
    header: str,
    key: dict,
    variable_short_name: str,
    children: list,
) -> ssb.Accordion:
    """Build Accordion for one variable in variable workspace."""
    return ssb.Accordion(
        header=header,
        id=key,
        children=[
            html.Section(
                id={
                    "type": "variable-input-alerts",
                    "variable_short_name": variable_short_name,
                },
                className="alert-section",
            ),
            html.Section(
                id={
                    "type": "variable-inputs",
                    "variable_short_name": variable_short_name,
                },
                children=children,
            ),
        ],
        className="variable-accordion",
    )


def build_dataset_edit_section(
    title: str,
    metadata_inputs: list[DatasetFieldTypes],
    language: str,
    dataset: model.Dataset,
    key: dict,
) -> html.Section:
    """Create edit section for dataset workspace."""
    return html.Section(
        id=key,
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            dbc.Form(
                [
                    i.render(
                        {
                            "type": DATASET_METADATA_INPUT,
                            "id": i.identifier,
                        },
                        language,
                        dataset,
                    )
                    for i in metadata_inputs
                ],
                id=f"{DATASET_METADATA_INPUT}-{title}",
                className="edit-section-form",
            ),
        ],
        className="edit-section dataset-edit-section",
    )
