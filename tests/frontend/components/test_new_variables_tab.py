"""Test new variables functions to build layout."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc.frontend.components.resources_test_new_variables import build_edit_section
from datadoc.frontend.components.resources_test_new_variables import (
    build_input_field_section,
)
from datadoc.frontend.components.resources_test_new_variables import build_ssb_accordion
from datadoc.frontend.fields.display_new_variables import OBLIGATORY_VARIABLES_METADATA

# test data - refactor set-up
obligatory_header = "Obligatorisk"
reccomended_header = "Anbefalt"

edit_sections = []
empty_meta_data_input = []

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


# Tests - refactor - use mark as parameterized
def test_build_ssb_accordions(build_test_variables):
    accordions = [
        build_ssb_accordion(
            variable["header"],
            variable["id"],
            variable["edit_section_id"],
            edit_sections,
        )
        for variable in build_test_variables
    ]
    assert accordions is not None
    assert accordions[0].header == "pers_id"
    assert accordions[2].id == {
        "type": "variables-accordion",
        "id": accordions[2].header,
    }


def test_build_ssb_accordion_is_correct_type(build_test_variables):
    test_variable = build_test_variables[0]
    accordion = build_ssb_accordion(
        test_variable["header"],
        test_variable["id"],
        test_variable["edit_section_id"],
        edit_sections,
    )
    assert isinstance(accordion, ssb.Accordion)


def test_build_ssb_accordion_header(build_test_variables):
    test_variable = build_test_variables[0]
    accordion = build_ssb_accordion(
        test_variable["header"],
        test_variable["id"],
        test_variable["edit_section_id"],
        edit_sections,
    )
    assert [accordion.header == test_header for test_header in build_test_variables]


def test_build_edit_section():
    current_variable = variable_short_names[0]
    obligatory_edit_section = build_edit_section(
        empty_meta_data_input,
        obligatory_header,
        current_variable,
        NORSK_BOKMÅL,
    )
    assert obligatory_edit_section is not None


def test_build_edit_section_children():
    current_variable = variable_short_names[0]
    obligatory_edit_section = build_edit_section(
        empty_meta_data_input,
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
