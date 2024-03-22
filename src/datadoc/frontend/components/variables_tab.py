"""Components and layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab

VARIABLES_INFORMATION_ID = "variables-information"
ACCORDION_WRAPPER_ID = "accordion-wrapper"


def build_variables_tab() -> dbc.Tab:
    """Build the framework for the variables tab."""
    return build_ssb_styled_tab(
        "Variabler",
        dbc.Container(
            [
                html.Header(
                    [
                        ssb.Title(
                            "Variabel detaljer",
                            size=2,
                            className="workspace-title",
                        ),
                        ssb.Paragraph(
                            id=VARIABLES_INFORMATION_ID,
                            className="workspace-info-paragraph",
                        ),
                        ssb.Input(
                            label="Søk i variabler",
                            searchField=True,
                            disabled=True,
                            placeholder="Kommer...",
                            id="search-variables",
                            n_submit=0,
                            value="",
                        ),
                    ],
                    className="workspace-header",
                ),
                html.Main(
                    id=ACCORDION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            class_name="workspace-page-wrapper",
        ),
    )
