"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

if TYPE_CHECKING:
    from datadoc_model import model

    from datadoc.frontend.fields.display_new_variables import VariablesInputField

logger = logging.getLogger(__name__)

info_section = (
    "Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: osv.."
)

VARIABLES_METADATA_INPUT = "variables-metadata-input"


def build_input_field_section(
    metadata_inputs: list[VariablesInputField],
    variable: model.Variable,
    language: str,
) -> dbc.Form:
    """Create input fields."""
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
            for i in metadata_inputs
        ],
        id=VARIABLES_METADATA_INPUT,
        className="variables-input-group",
    )


# One section of inputs (either obligatory or recommended)
def build_edit_section(
    metadata_inputs: list,
    title: str,
    variable: model.Variable,
    language: str,
) -> html.Section:
    """Create input section."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(metadata_inputs, variable, language),
        ],
        className="input-section",
    )


# Accordion for variable
def build_ssb_accordion(
    header: str,
    key: dict,
    variable_short_name: str,
    children: list,
) -> ssb.Accordion:
    """Build Accordion for one variable."""
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
        className="variable",
    )
