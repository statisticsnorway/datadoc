"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.fields.display_new_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import OPTIONAL_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import DisplayNewVariablesMetadata

info_section = (
    "Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: osv.."
)

NEW_DATASET_METADATA_INPUT = "new-dataset-metadata-input"


# set Input type ...
def build_input_field_section(
    metadata_inputs: list[DisplayNewVariablesMetadata],
    input_type: str,
) -> html.Section:
    """Create input fields."""
    return html.Section(
        [
            html.Section(
                [
                    dbc.Form(
                        [
                            ssb.Input(
                                label=i.display_name,
                                disabled=not i.editable,
                                className="variabels-input",
                                id={
                                    "type": NEW_DATASET_METADATA_INPUT,
                                    "id": i.identifier,
                                },
                                value="",
                                type=input_type,
                            ),
                        ],
                    )
                    for i in metadata_inputs
                ],
                className="variables-input-group",
                id=NEW_DATASET_METADATA_INPUT,
            ),
        ],
        className="variables-input-group",
    )


def build_edit_section(
    metadata_inputs: list,
    title: str,
    input_type: str,
) -> html.Section:
    """Create input section."""
    return html.Section(
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(metadata_inputs, input_type),
        ],
        className="input-section",
    )


def build_ssb_accordion(
    header: str,
    key: dict,
) -> ssb.Accordion:
    """Build Accordion for one variabel."""
    return ssb.Accordion(
        header=header,
        id=key,  # must have unique key/id
        children=[
            build_edit_section(
                OBLIGATORY_VARIABLES_METADATA,
                "Obligatorisk",
                "text",
            ),
            build_edit_section(OPTIONAL_VARIABLES_METADATA, "Anbefalt", "text"),
        ],
    )
