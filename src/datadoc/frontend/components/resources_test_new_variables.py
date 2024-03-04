"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

if TYPE_CHECKING:
    from datadoc.frontend.fields.display_new_variables import (
        DisplayNewVariablesMetadataDropdown,
    )

from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)

info_section = (
    "Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: osv.."
)

VARIABLES_METADATA_INPUT = "variables-metadata-input"


# section of Inputs: Input, checkbox or dropdown
def build_input_field_section(
    metadata_inputs: list[DisplayNewVariablesMetadataDropdown],
    variable_short_name: str,
    language: str,
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
                    type=i.presentation,
                    debounce=True,
                )
                if i.component == ssb.Input
                else (
                    i.component(
                        header=i.display_name,
                        id={
                            "type": VARIABLES_METADATA_INPUT,
                            "variable_short_name": variable_short_name,
                            "id": i.identifier,
                        },
                        items=i.options_getter(SupportedLanguages(language)),
                    )
                    if i.component == ssb.Dropdown
                    else i.component(
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


# One section of inputs (either obligatory or recommended)
def build_edit_section(
    metadata_inputs: list,
    title: str,
    variable_short_name: str,
    language: str,
) -> html.Section:
    """Create input section."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(metadata_inputs, variable_short_name, language),
        ],
        className="input-section",
    )


# Accordion for variable
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
