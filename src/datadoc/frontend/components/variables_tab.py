"""Components and layout for the Variables metadata tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table
from dash import html

from datadoc import state
from datadoc.frontend.components.builders import build_ssb_styled_tab
from datadoc.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.utils import get_display_values


def build_variables_tab() -> dbc.Tab:
    """Build the Variables metadata tab."""
    return build_ssb_styled_tab(
        "Variabler",
        dbc.Container(
            children=[
                dbc.Row(html.H2("Variabel detaljer", className="ssb-title")),
                dbc.Row(
                    dash_table.DataTable(
                        id="variables-table",
                        # Populate fields with known values
                        data=[
                            get_display_values(v, state.current_metadata_language)
                            for v in state.metadata.meta.variables
                        ],
                        # Define columns based on the information in DISPLAY_VARIABLES
                        columns=[
                            {
                                "name": variable.display_name,
                                "id": variable.identifier,
                                "editable": variable.editable,
                                "presentation": variable.presentation,
                                "hideable": variable.editable,
                            }
                            for variable in DISPLAY_VARIABLES.values()
                            if variable.identifier
                            != VariableIdentifiers.IDENTIFIER.value  # Should be removed from the model, for now we hide it
                        ],
                        # Non-obligatory variables are hidden by default
                        hidden_columns=[
                            v.identifier
                            for v in DISPLAY_VARIABLES.values()
                            if v.obligatory is False
                        ],
                        # Include tooltips for all columns
                        tooltip_header={
                            v.identifier: v.description
                            for v in DISPLAY_VARIABLES.values()
                        },
                        editable=True,
                        # Exclude short_name column from scrolling
                        fixed_columns={"headers": True, "data": 1},
                        # Enable sorting and pagination
                        sort_action="native",
                        page_action="native",
                        page_size=20,
                        # Enable filtering
                        filter_action="native",
                        filter_options={"case": "insensitive"},
                        # Use horizontal scroll, keep full width
                        style_table={
                            "overflowX": "auto",
                            "minWidth": "100%",
                            "accentColor": "black",
                        },
                    ),
                ),
            ],
        ),
    )
