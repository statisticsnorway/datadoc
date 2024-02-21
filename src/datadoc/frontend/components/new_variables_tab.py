"""Components and layout for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc.frontend.components.builders import build_ssb_styled_tab

# build variables Tab
# This will be returned when you select new variables
# A menu/aside section with interactive buttons .. with variables name
# click/select and open a section ... form?
# two "sections" obligatory and reccomended
# In each section each detail from  https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst is represented by a Input component with Label
# Some Input components have dropdown enum values


def build_new_variables_tab() -> dbc.Tab:
    """Build page content fro new variables tab."""
    return build_ssb_styled_tab(
        "Variabler Ny",
        dbc.Container(
            [
                dbc.Row(ssb.Title("Variabel detaljer", size=2)),  # Title
                dbc.Row(
                    [
                        ssb.Paragraph("Informasjon"),
                    ],
                ),  # info
                dbc.Row(
                    [
                        dbc.Col(
                            [],
                        ),  # aside
                        dbc.Col(),  # workspace
                    ],
                ),
            ],
        ),
    )
