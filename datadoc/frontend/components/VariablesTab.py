import dash_bootstrap_components as dbc
import datadoc.state as state
from dash import dash_table, html
from datadoc.frontend.Builders import make_ssb_styled_tab
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
            ],
        ),
    )
