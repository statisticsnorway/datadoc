"""Test resources for testing new layout for variables tab."""

from __future__ import annotations

import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

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

variables_test_names_dropdown = [
    {"id": "1", "title": "fnr"},
    {"id": "2", "title": "sivilstand"},
    {"id": "3", "title": "bostedskommune"},
    {"id": "4", "title": "inntekt"},
    {"id": "5", "title": "bankinnskudd"},
    {"id": "6", "title": "dato"},
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

info_section = f"Informasjon om hvordan jobbe i Datadoc, antall variabler i datasettet: {len(variables_test_names)} osv.."


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
