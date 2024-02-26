"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.fields.display_new_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import OPTIONAL_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import DisplayNewVariablesMetadata

info_section = (
    "Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: osv.."
)

DATASET_METADATA_INPUT = "dataset-metadata-input"


# set Input type ...
def build_input_field_section(
    metadata_inputs: list[DisplayNewVariablesMetadata],
) -> html.Section:
    """Create input fields."""
    return html.Section(
        [
            html.Section(
                [
                    ssb.Input(
                        label=i.display_name,
                        disabled=not i.editable,
                        className="variabels-input",
                        id={"type": DATASET_METADATA_INPUT, "id": i.identifier},
                        value="",
                        # **i.extra_kwargs,
                    )
                    for i in metadata_inputs
                ],
                className="variables-input-group",
            ),
        ],
        className="variables-input-group",
    )


def build_edit_section(
    metadata_inputs: list,
    title: str,
) -> html.Section:
    """Create input section."""
    return html.Section(
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(metadata_inputs),
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
            build_edit_section(OBLIGATORY_VARIABLES_METADATA, "Obligatorisk"),
            build_edit_section(OPTIONAL_VARIABLES_METADATA, "Anbefalt"),
        ],
    )
