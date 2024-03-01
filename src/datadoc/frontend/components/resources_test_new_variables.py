"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model.model import DataType

if TYPE_CHECKING:
    from datadoc.frontend.fields.display_new_variables import (
        DisplayNewVariablesMetadata,
    )

logger = logging.getLogger(__name__)

info_section = (
    "Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: osv.."
)

VARIABLES_METADATA_INPUT = "variables-metadata-input"

dropdown = []
index = 0

for index, val in enumerate(DataType):
    dropdown.append({"id": str(index), "title": val})


def build_input_field_section(
    metadata_inputs: list[DisplayNewVariablesMetadata],
    variable_short_name: str,
) -> dbc.Form:
    """Create input fields."""
    return dbc.Form(
        [
            (
                i.component(
                    label=i.display_name,
                    disabled=not i.editable,
                    className="variables-input",
                    id={
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": variable_short_name,
                        "id": i.identifier,
                    },
                    value="",
                    type=i.presentation,
                )
                if i.component == ssb.Input
                else (
                    i.component(
                        id={
                            "type": VARIABLES_METADATA_INPUT,
                            "variable_short_name": variable_short_name,
                            "id": i.identifier,
                        },
                        **i.extra_kwargs,
                    )
                    if i.component == dbc.Checkbox
                    else i.component(
                        header=i.display_name,
                        id={
                            "type": VARIABLES_METADATA_INPUT,
                            "variable_short_name": variable_short_name,
                            "id": i.identifier,
                        },
                        **i.extra_kwargs,
                    )
                )
            )
            for i in metadata_inputs
        ],
        id=VARIABLES_METADATA_INPUT,
        className="variables-input-group",
    )


def build_edit_section(
    metadata_inputs: list,
    title: str,
    variable_short_name: str,
) -> html.Section:
    """Create input section."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(metadata_inputs, variable_short_name),
        ],
        className="input-section",
    )


def build_ssb_accordion(
    header: str,
    key: dict,
    variable_short_name: str,
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
            ),
        ],
        className="variable",
    )
