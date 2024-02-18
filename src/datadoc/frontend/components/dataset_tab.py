"""Components and layout for the Dataset metadata tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OBLIGATORY_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OPTIONAL_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DisplayDatasetMetadata

DATASET_METADATA_INPUT = "dataset-metadata-input"


def build_dataset_metadata_accordion_item(
    title: str,
    metadata_inputs: list[DisplayDatasetMetadata],
) -> ssb.Accordion:
    """Build a Dash AccordionItem for the given Metadata inputs.

    Typically used to categorize metadata fields.
    """
    return ssb.Accordion(
        header=title,
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        ssb.Input(
                            label=i.display_name,
                            id=i.identifier,
                            type="text",
                            disabled=not i.editable,
                            className="dataset-input",
                        ),
                    ),
                ],
            )
            for i in metadata_inputs
        ],
    )


def build_dataset_tab() -> dbc.Tab:
    """Build the Dataset metadata tab."""
    return build_ssb_styled_tab(
        "Datasett",
        dbc.Container(
            [
                dbc.Row(ssb.Title("Datasett detaljer", size=2)),
                ssb.Paragraph(
                    children=["Paragraph with info about the dataset"],
                    id="dataset-info",
                ),
                html.Div(
                    children=[
                        build_dataset_metadata_accordion_item(
                            "Obligatorisk",
                            OBLIGATORY_EDITABLE_DATASET_METADATA,
                        ),
                        build_dataset_metadata_accordion_item(
                            "Valgfritt",
                            OPTIONAL_DATASET_METADATA,
                        ),
                        build_dataset_metadata_accordion_item(
                            "Maskingenerert",
                            NON_EDITABLE_DATASET_METADATA,
                        ),
                    ],
                ),
            ],
        ),
    )
