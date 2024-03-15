"""Components and layout for the Dataset metadata tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
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
    accordion_item_id: str,
) -> dbc.AccordionItem:
    """Build a Dash AccordionItem for the given Metadata inputs with a unique ID.

    Typically used to categorize metadata fields.
    """
    return dbc.AccordionItem(
        title=title,
        id=accordion_item_id,
        children=[
            dbc.Row(
                [
                    dbc.Col(html.Label(i.display_name)),
                    dbc.Col(
                        i.component(
                            placeholder=i.description,
                            disabled=not i.editable,
                            id={
                                "type": DATASET_METADATA_INPUT,
                                "id": i.identifier,
                            },
                            **i.extra_kwargs,
                        ),
                        width=5,
                    ),
                    dbc.Col(width=4),
                ],
            )
            for i in metadata_inputs
        ],
    )


def build_dataset_metadata_accordion(n_clicks: int = 0) -> list[dbc.AccordionItem]:
    """Build the accordion on Dataset metadata tab.

    n_clicks parameter is appended to the accordions' items id
    to avoid browser caching and refresh the values
    """
    obligatory = build_dataset_metadata_accordion_item(
        "Obligatorisk",
        OBLIGATORY_EDITABLE_DATASET_METADATA,
        accordion_item_id=f"obligatory-metadata-accordion-item-{n_clicks}",
    )
    optional = build_dataset_metadata_accordion_item(
        "Anbefalt",
        OPTIONAL_DATASET_METADATA,
        accordion_item_id=f"optional-metadata-accordion-item-{n_clicks}",
    )
    non_editable = build_dataset_metadata_accordion_item(
        "Maskingenerert",
        NON_EDITABLE_DATASET_METADATA,
        accordion_item_id=f"non-editable-metadata-accordion-item-{n_clicks}",
    )
    return [obligatory, optional, non_editable]


def build_dataset_tab() -> dbc.Tab:
    """Build the Dataset metadata tab."""
    return build_ssb_styled_tab(
        "Datasett",
        dbc.Container(
            [
                dbc.Row(html.H2("Datasett detaljer", className="ssb-title")),
                dbc.Accordion(
                    id="dataset-accordion",
                    always_open=True,
                    children=build_dataset_metadata_accordion(),
                ),
            ],
        ),
    )
