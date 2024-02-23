"""Components and layout for testing new layout for variables tab."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.components.builders import build_ssb_styled_tab

# In each section each detail from  https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst is represented by a Input component with Label
# Some Input components have dropdown enum values

# Test data
variables_test_names = [
    "fnr",
    "sivilstand",
    "bostedskommune",
    "inntekt",
    "bankinnskudd",
    "dato",
]

# dropdown: datatype,variabelens, DPI,temporalitetstype,
variables_details_test_obligatory = [
    "Kortnavn",
    "Navn",
    "Datatype",
    "Variabelens rolle",
    "Definition URI",
    "DPI",
]

data_type = [
    {
        "title": "Tekst",
        "id": "text",
    },
    {
        "title": "Heltall",
        "id": "integer",
    },
    {
        "title": "Desimaltall",
        "id": "float",
    },
    {
        "title": "Datotid",
        "id": "datetime",
    },
    {
        "title": "Boolsk",
        "id": "bool",
    },
]

variables_details_test_recommended = [
    "Nøkkelord",
    "Geografisk dekningsområde",
    "Datakilde",
    "Populasjonen",
    "Kommentar",
    "Temporalitetstype",
    "Måleenhet",
    "Format",
    "Kodeverkets URI",
    "Spesialverdienes URI",
    "Ugyldige verdier",
    "Inneholder data f.o.m.",
    "Inneholder data t.o.m",
]


# builders
def build_input_dropdowns(name: str, values: list) -> ssb.Dropdown:
    """Create dropdown."""
    return ssb.Dropdown(
        id=name,
        header=name,
        items=values,
        className="variabels-dropdown",
    )


def build_input_field_section(variabel_list: list, id_type: str) -> html.Section:
    """Create input fields."""
    return html.Section(
        [
            html.Section(
                [
                    ssb.Input(
                        label=value,
                        id={"type": id_type, "id": str(index)},
                        className="variabels-input",
                    )
                    for index, value in enumerate(variabel_list)
                ],
                className="variables-input-group",
            ),
            build_input_dropdowns("Datatype", data_type),
        ],
        className="variables-input-group",
    )


def build_edit_section(variabel_list: list, id_type: str, title: str) -> html.Section:
    """Create obligatory input section."""
    return html.Section(
        children=[
            ssb.Title(title, size=3, className="input-section-title"),
            build_input_field_section(variabel_list, id_type),
        ],
        className="input-section",
    )


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
                            f"Informasjon om antall variabler i datasettet {len(variables_test_names)} og hvordan/hva",
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
                            [
                                ssb.Accordion(
                                    id={"type": "variables", "id": index},
                                    header=variable,
                                    className="variabel",
                                    children=[
                                        ssb.Input(
                                            label="Ferdig",
                                            type="checkbox",
                                            id="variabels-checkbox",
                                        ),
                                        build_edit_section(
                                            variables_details_test_obligatory,
                                            "obligatory",
                                            "Obligatoriske verdier",
                                        ),
                                        build_edit_section(
                                            variables_details_test_recommended,
                                            "recommended",
                                            "Anbefalte verdier",
                                        ),
                                    ],
                                )
                                for index, variable in enumerate(
                                    sorted(variables_test_names),
                                )
                            ],
                            id="accordion-wrapper",
                            className="accordion-wrapper",
                        ),
                    ],
                ),
            ],
            class_name="page-wrapper",
        ),
    )
