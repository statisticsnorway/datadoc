"""Components and layout for the Dataset metadata tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import ssb_dash_components as ssb
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

SECTION_WRAPPER_ID = "section-wrapper-id"


def build_dataset_tab() -> dbc.Tab:
    """Build the Dataset metadata tab."""
    return build_ssb_styled_tab(
        "Datasett",
        html.Article(
            [
                html.Header(
                    [
                        ssb.Title(
                            "Datasett detaljer",
                            size=2,
                            className="workspace-title",
                        ),
                    ],
                    className="workspace-header",
                ),
                html.Article(
                    id=SECTION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            className="workspace-page-wrapper",
        ),
    )
