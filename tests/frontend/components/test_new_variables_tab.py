"""Test new variables functions to build layout."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html

from datadoc.frontend.components.resources_test_new_variables import build_edit_section
from datadoc.frontend.components.resources_test_new_variables import (
    build_input_field_section,
)
from datadoc.frontend.components.resources_test_new_variables import build_ssb_accordion
from datadoc.frontend.fields.display_new_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import OPTIONAL_VARIABLES_METADATA

# set-up
obligatory_header = "Obligatorisk"
reccomended_header = "Anbefalt"

edit_sections = []
empty_metadata_input = []
obligatory_metadata_input = OBLIGATORY_VARIABLES_METADATA
optional_metadata_input = OPTIONAL_VARIABLES_METADATA
# DISPLAYED_VARIABLES_METADATA

NORSK_BOKMÅL = "nb"
NORSK_NYNORSK = "nn"
ENGLISH = "en"

variable_short_names = ["pers_id", "tidspunkt", "sykepenger"]


@pytest.fixture()
def build_test_variables():
    return [
        (
            {
                "header": i,
                "edit_section_id": i,
                "id": {"type": "variables-accordion", "id": i},
            }
        )
        for i in variable_short_names
    ]


# variable: model.Variable,
ACCORDION_TYPE = "variables-accordion"
ALERTS_TYPE = "variable-input-alerts"
INPUT_TYPE = "variable-inputs"

ACCORDION_INPUTS_EMPTY_LIST = [
    (
        "pers_id",
        {"type": ACCORDION_TYPE, "id": "pers_id"},
        "pers_id",
        empty_metadata_input,
        ssb.Accordion,
    ),
    (
        "sykepenger",
        {"type": ACCORDION_TYPE, "id": "sykepenger"},
        "sykepenger",
        empty_metadata_input,
        ssb.Accordion,
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        empty_metadata_input,
        ssb.Accordion,
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        empty_metadata_input,
        ssb.Accordion,
    ),
]

ACCORDION_INPUTS = [
    (
        "pers_id",
        {"type": ACCORDION_TYPE, "id": "pers_id"},
        "pers_id",
        obligatory_metadata_input,
        ssb.Accordion,
    ),
    (
        "sykepenger",
        {"type": ACCORDION_TYPE, "id": "sykepenger"},
        "sykepenger",
        optional_metadata_input,
        ssb.Accordion,
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        obligatory_metadata_input,
        ssb.Accordion,
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        optional_metadata_input,
        ssb.Accordion,
    ),
]

ACCORDION_CHILDREN = [
    (
        "pers_id",
        {"type": ACCORDION_TYPE, "id": "pers_id"},
        "pers_id",
        obligatory_metadata_input,
        html.Section,
    ),
    (
        "sykepenger",
        {"type": ACCORDION_TYPE, "id": "sykepenger"},
        "sykepenger",
        optional_metadata_input,
        html.Section,
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        obligatory_metadata_input,
        html.Section,
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        optional_metadata_input,
        html.Section,
    ),
]

ACCORDION_CHILDREN_ID = [
    (
        "pers_id",
        {"type": ACCORDION_TYPE, "id": "pers_id"},
        "pers_id",
        obligatory_metadata_input,
        [
            {"type": ALERTS_TYPE, "variable_short_name": "pers_id"},
            {"type": INPUT_TYPE, "variable_short_name": "pers_id"},
        ],
    ),
    (
        "sykepenger",
        {"type": ACCORDION_TYPE, "id": "sykepenger"},
        "sykepenger",
        optional_metadata_input,
        [
            {"type": ALERTS_TYPE, "variable_short_name": "sykepenger"},
            {"type": INPUT_TYPE, "variable_short_name": "sykepenger"},
        ],
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        obligatory_metadata_input,
        [
            {"type": ALERTS_TYPE, "variable_short_name": "ber_bruttoformue"},
            {"type": INPUT_TYPE, "variable_short_name": "ber_bruttoformue"},
        ],
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        optional_metadata_input,
        [
            {"type": ALERTS_TYPE, "variable_short_name": "hoveddiagnose"},
            {"type": INPUT_TYPE, "variable_short_name": "hoveddiagnose"},
        ],
    ),
]


@pytest.mark.parametrize(
    ("header", "key", "variable_short_name", "children", "expected"),
    ACCORDION_INPUTS_EMPTY_LIST,
)
def test_build_ssb_accordion_return_correct_component_metadata_list_is_empty(
    header,
    key: dict,
    variable_short_name,
    children,
    expected,
):
    accordion = build_ssb_accordion(header, key, variable_short_name, children)
    assert isinstance(
        accordion,
        expected,
    )
    assert accordion.id == key


@pytest.mark.parametrize(
    ("header", "key", "variable_short_name", "children", "expected"),
    ACCORDION_INPUTS,
)
def test_build_ssb_accordion_return_correct_component_metadata_input_list(
    header,
    key,
    variable_short_name,
    children,
    expected,
):
    accordion = build_ssb_accordion(header, key, variable_short_name, children)
    assert isinstance(
        accordion,
        expected,
    )
    assert accordion.id == key


@pytest.mark.parametrize(
    (
        "header",
        "key",
        "variable_short_name",
        "children",
        "expected",
    ),
    ACCORDION_CHILDREN,
)
def test_build_ssb_accordion_children_return_correct_component(
    header,
    key,
    variable_short_name,
    children,
    expected,
):
    accordion = build_ssb_accordion(header, key, variable_short_name, children)
    assert (
        isinstance(
            accordion.children[i],
            expected,
        )
        for i in ACCORDION_CHILDREN
    )


@pytest.mark.parametrize(
    (
        "header",
        "key",
        "variable_short_name",
        "children",
        "expected_id_list",
    ),
    ACCORDION_CHILDREN_ID,
)
def test_build_ssb_accordion_children_return_correct_id(
    header,
    key,
    variable_short_name,
    children,
    expected_id_list,
):
    accordion = build_ssb_accordion(header, key, variable_short_name, children)
    assert [
        (accordion.children[i].id == expected_id_list)
        for i in range(len(accordion.children))
    ]


def test_build_edit_section():
    current_variable = variable_short_names[0]
    obligatory_edit_section = build_edit_section(
        empty_metadata_input,
        obligatory_header,
        current_variable,
        NORSK_BOKMÅL,
    )
    assert obligatory_edit_section is not None


def test_build_edit_section_children():
    current_variable = variable_short_names[0]
    obligatory_edit_section = build_edit_section(
        empty_metadata_input,
        obligatory_header,
        current_variable,
        NORSK_BOKMÅL,
    )
    assert obligatory_edit_section.children[0].children == "Obligatorisk"
    assert isinstance(obligatory_edit_section.children[1], dbc.Form)


# Why function with empty list?
def test_build_input_field_section():
    test_input_section = build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        "pers_id",
        NORSK_NYNORSK,
    )
    assert test_input_section is not None
    assert isinstance(test_input_section, dbc.Form)
    assert (
        isinstance(
            (test_input_section.children[i], (ssb.Input, ssb.Dropdown, dbc.Checkbox)),
        )
        for i in test_input_section
    )
    assert len(test_input_section.children) == len(OBLIGATORY_VARIABLES_METADATA)


def test_input_section_will_build_form_but_no_components_with_empty_metadata_list():
    test_input_section = build_input_field_section(
        empty_metadata_input,
        "pers_id",
        NORSK_NYNORSK,
    )
    assert isinstance(test_input_section, dbc.Form)
    assert test_input_section.children == []
