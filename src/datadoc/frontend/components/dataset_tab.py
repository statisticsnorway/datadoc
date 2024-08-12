"""Components and layout for the Dataset metadata tab."""

from __future__ import annotations

from dash import html

SECTION_WRAPPER_ID = "section-wrapper-id"


def build_dataset_tab() -> html.Article:
    """Build the Dataset metadata tab."""
    return html.Article(
        [
            html.Article(
                id=SECTION_WRAPPER_ID,
                className="workspace-content",
            ),
        ],
        className="workspace-page-wrapper",
    )
