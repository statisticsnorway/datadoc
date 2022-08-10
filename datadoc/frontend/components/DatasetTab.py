import dash_bootstrap_components as dbc
from dash import html, dash_table

from datadoc.frontend.Builders import (
    make_dataset_metadata_accordion_item,
    make_ssb_styled_tab,
)
from datadoc.frontend.fields.DisplayDataset import (
    NON_EDITABLE_DATASET_METADATA,
    OBLIGATORY_EDITABLE_DATASET_METADATA,
    OPTIONAL_DATASET_METADATA,
)
from datadoc.frontend.fields.DisplayVariables import DISPLAY_VARIABLES
from datadoc.utils import get_display_values
import datadoc.state as state


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
