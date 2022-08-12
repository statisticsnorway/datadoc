from typing import List

import dash_bootstrap_components as dbc
from dash import html
from datadoc.frontend.Builders import make_ssb_styled_tab
from datadoc.frontend.fields.DisplayDataset import (
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
    DisplayDatasetMetadata,
)

DATASET_METADATA_INPUT = "dataset-metadata-input"


def make_dataset_metadata_accordion_item(
    title: str,
    metadata_inputs: List[DisplayDatasetMetadata],
) -> dbc.AccordionItem:
    return dbc.AccordionItem(
        title=title,
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
                ]
            )
            for i in metadata_inputs
        ],
    )


def get_dataset_tab() -> dbc.Tab:
    return make_ssb_styled_tab(
        "Datasett",
        dbc.Container(
            [
                dbc.Row(html.H2("Datasett detaljer", className="ssb-title")),
                dbc.Accordion(
                    always_open=True,
                    children=[
                        make_dataset_metadata_accordion_item(
                            "Obligatorisk",
                            OBLIGATORY_EDITABLE_DATASET_METADATA,
                        ),
                        make_dataset_metadata_accordion_item(
                            "Valgfritt",
                            OPTIONAL_DATASET_METADATA,
                        ),
                        make_dataset_metadata_accordion_item(
                            "Maskingenerert",
                            NON_EDITABLE_DATASET_METADATA,
                        ),
                    ],
                ),
            ],
        ),
    )
