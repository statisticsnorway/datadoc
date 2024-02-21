"""Components and layout for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab

# build variables Tab
# This will be returned when you select new variables in Tabs menu
# A menu/aside section with interactive buttons .. with variables name
# click/select and open a section ... form?
# two "sections" obligatory and reccomended
# In each section each detail from  https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst is represented by a Input component with Label
# Some Input components have dropdown enum values

variables_test_names = [
    "fnr",
    "sivilstand",
    "bostedskommune",
    "inntekt",
    "bankinnskudd",
    "dato",
]


def build_new_variabels_accordion(header: str) -> ssb.Accordion:
    """Build workspace for single variabel to edit."""
    return ssb.Accordion(
        id="variabel",
        className="variabel",
        header=header,
        openByDefault=True,
        children=[ssb.Input(label="Test input", id="dataset", type="text")],
    )


def build_new_variables_tab() -> dbc.Tab:
    """Build page content fro new variables tab."""
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
                        ssb.Paragraph("Informasjon"),
                    ],
                ),
                html.Div(
                    id="variables-content",
                    className="page-content",
                    children=[
                        html.Aside(
                            id="variables-overview",
                            children=[
                                ssb.Title(
                                    "Variabler A-Å",
                                    size=4,
                                    className="",
                                ),
                                html.Nav(
                                    [
                                        html.Ul(
                                            id="display-variables-link",
                                            children=[
                                                html.Li(i) for i in variables_test_names
                                            ],  # unique id list items dash bootstrap?
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Main(
                            id="variabels-workspace",
                            className="main-content",
                            children=[
                                ssb.Title("Test", size=3),
                                html.Div(
                                    children=[
                                        build_new_variabels_accordion(header=name)
                                        for name in variables_test_names
                                    ],
                                ),
                            ],  # probably section iterated
                        ),
                    ],
                ),
            ],
            class_name="page-wrapper",
        ),
    )
