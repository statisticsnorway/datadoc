"""Components and layout for the Dataset metadata tab."""

from __future__ import annotations

import ssb_dash_components as ssb
from dash import html

SECTION_WRAPPER_ID = "section-wrapper-id"


def build_dataset_tab() -> html.Article:
    """Build the Dataset metadata tab."""
    return html.Article(
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
    )
