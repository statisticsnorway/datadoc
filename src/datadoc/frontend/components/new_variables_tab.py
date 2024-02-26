"""Components and layout for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab
from datadoc.frontend.components.resources_test_new_variables import info_section


def build_new_variables_tab() -> dbc.Tab:
    """Build page content for new variables tab."""
    return build_ssb_styled_tab(
        "Variabler Ny",
        dbc.Container(
            [
                html.Header(
                    [
                        ssb.Title(
                            "Variabel detaljer",
                            size=2,
                            className="variabels-title",
                        ),
                        ssb.Paragraph(
                            info_section,
                        ),
                        ssb.Input(
                            label="Søk i variabler",
                            searchField=True,
                            id="search-variables",
                            n_submit=0,
                        ),
                    ],
                    className="variabels-header",
                ),
                html.Main(
                    id="variabels-details",
                    className="main-content",
                    children=[
                        html.Div(
                            id="accordion-wrapper",
                            className="accordion-wrapper",
                        ),
                    ],
                ),
            ],
            class_name="page-wrapper",
        ),
    )
