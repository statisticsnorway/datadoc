"""Components and layout for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab
from datadoc.frontend.components.resources_test_new_variables import build_edit_section
from datadoc.frontend.components.resources_test_new_variables import info_section
from datadoc.frontend.components.resources_test_new_variables import (
    variables_details_test_obligatory,
)
from datadoc.frontend.components.resources_test_new_variables import (
    variables_details_test_recommended,
)
from datadoc.frontend.components.resources_test_new_variables import (
    variables_test_names,
)
from datadoc.frontend.components.resources_test_new_variables import (
    variables_test_names_dropdown,
)


def build_navigation(value_list: list) -> html.Section:
    """Create dropdowns with links to workspace."""
    alphabet_part1: list = []
    alphabet_part2: list = []
    alphabet_part3: list = []
    alphabet_part4: list = []

    for value in value_list:
        if value.get("title")[0] <= "g":
            alphabet_part1.append(value)
        if value.get("title")[0] > "g" and value.get("title")[0] <= "n":
            alphabet_part2.append(value)
        if value.get("title")[0] > "n" and value.get("title")[0] <= "u":
            alphabet_part3.append(value)
        if value.get("title")[0] > "u":
            alphabet_part4.append(value)
    return html.Section(
        [
            ssb.Dropdown(
                id="dropdown-first",
                className="dropdown-navigation",
                header="Variabler A-G",
                items=alphabet_part1,
            ),
            ssb.Dropdown(
                id="dropdown-second",
                className="dropdown-navigation",
                header="Variabler H-N",
                items=alphabet_part2,
            ),
            ssb.Dropdown(
                id="dropdown-third",
                className="dropdown-navigation",
                header="Variabler O-U",
                items=alphabet_part3,
            ),
            ssb.Dropdown(
                id="dropdown-fourth",
                className="dropdown-navigation",
                header="Variabler V-Å",
                items=alphabet_part4,
            ),
        ],
        className="aside-section",
    )


def build_new_variables_tab_with_links() -> dbc.Tab:
    """Build page content for new variables tab."""
    return build_ssb_styled_tab(
        "Variabler Ny med lenker",
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
                            id="search-variables-link-page2",
                            n_submit=0,
                        ),
                    ],
                    className="variabels-header",
                ),
                html.Div(
                    [
                        html.Aside(
                            [
                                build_navigation(variables_test_names_dropdown),
                            ],
                        ),
                        html.Main(
                            id="variabels-details-link-page2",
                            className="main-content",
                            children=[
                                ssb.Paragraph(
                                    f"Variabler fullført 1/{len(variables_test_names)}",
                                ),
                                html.Div(
                                    [
                                        ssb.Accordion(
                                            id={
                                                "type": "variables-link-page2",
                                                "id": variable,
                                            },
                                            header=variable,
                                            className="variabel",
                                            children=[
                                                ssb.Input(
                                                    label="Ferdig",
                                                    type="checkbox",
                                                    id="variabels-checkbox2",
                                                ),
                                                build_edit_section(
                                                    variables_details_test_obligatory,
                                                    "obligatory2",
                                                    "Obligatoriske verdier",
                                                ),
                                                build_edit_section(
                                                    variables_details_test_recommended,
                                                    "recommended2",
                                                    "Anbefalte verdier",
                                                ),
                                            ],
                                        )
                                        for index, variable in enumerate(
                                            sorted(variables_test_names),
                                        )
                                    ],
                                    id="accordion-wrapper2",
                                    className="accordion-wrapper",
                                ),
                            ],
                        ),
                    ],
                    className="content-wrapper",
                ),
            ],
            class_name="page-wrapper",
        ),
    )
