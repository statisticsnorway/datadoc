"""Components and layout for variables tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import ssb_dash_components as ssb
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

VARIABLES_INFORMATION_ID = "variables-information"
ACCORDION_WRAPPER_ID = "accordion-wrapper"


def build_variables_tab() -> dbc.Tab:
    """Build the framework for the variables tab."""
    return build_ssb_styled_tab(
        "Variabler",
        html.Article(
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
                html.Article(
                    id=ACCORDION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            className="workspace-page-wrapper",
        ),
    )
