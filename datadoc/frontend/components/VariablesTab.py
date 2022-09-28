import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

import datadoc.state as state
from datadoc.frontend.Builders import make_ssb_styled_tab
from datadoc.frontend.fields.DisplayBase import DROPDOWN_KWARGS, INPUT_KWARGS
from datadoc.frontend.fields.DisplayVariables import DISPLAY_VARIABLES
from datadoc.utils import get_display_values


def get_variables_tab() -> dbc.Tab:
    return make_ssb_styled_tab(
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
                        # Enable sorting and pagination
                        sort_action="native",
                        page_action="native",
                    )
                ),
                dbc.Card(
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Input(
                                    id="vardok-search-text",
                                    placeholder="Søk i Vardok",
                                    **INPUT_KWARGS,
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Søk",
                                    id="vardok-search-button",
                                    class_name="ssb-btn primary-btn",
                                ),
                                width=1,
                            ),
                            dbc.Col(
                                dcc.Dropdown(id="vardok-dropdown", **DROPDOWN_KWARGS),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "OK",
                                    id="vardok-ok-button",
                                    disabled=True,
                                    class_name="ssb-btn primary-btn",
                                ),
                                width=1,
                            ),
                        ],
                        justify="center",
                        align="center",
                    ),
                    style={"width": "48rem", "align": "center"},
                ),
            ],
        ),
    )
