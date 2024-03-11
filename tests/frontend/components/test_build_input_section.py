"""Test function build_input_field_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from datadoc_model import model

from datadoc import enums
from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_input_field_section
from datadoc.frontend.fields.display_base import get_enum_options_for_language
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

NORSK_BOKMÅL = "nb"
NORSK_NYNORSK = "nn"
ENGLISH = "en"

INPUT_FIELD_SECTION = [
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        NORSK_NYNORSK,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="pers_id"),
        NORSK_BOKMÅL,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        ENGLISH,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
        NORSK_BOKMÅL,
    ),
]


def test_build_input_field_section_no_input_return_empty_list():
    input_section = build_input_field_section(
        [],
        "",
        "",
    )
    assert input_section.children == []


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_props_input(input_field_section):
    variable_input_field_for_name = input_field_section.children[0]
    assert variable_input_field_for_name.type == "text"
    assert variable_input_field_for_name.value is None
    input_value = "Statistics"
    variable_input_field_for_name.value = input_value
    assert variable_input_field_for_name.value == input_value
    assert isinstance(variable_input_field_for_name, ssb.Input)
    assert variable_input_field_for_name.debounce is True
    assert variable_input_field_for_name.disabled is False
    assert variable_input_field_for_name.label == "Navn"


@pytest.mark.parametrize(
    ("input_field_section", "language"),
    [
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="hoveddiagnose"),
                NORSK_NYNORSK,
            ),
            NORSK_NYNORSK,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="pers_id"),
                NORSK_BOKMÅL,
            ),
            NORSK_BOKMÅL,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="ber_bruttoformue"),
                ENGLISH,
            ),
            ENGLISH,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="sykepenger"),
                NORSK_BOKMÅL,
            ),
            NORSK_BOKMÅL,
        ),
    ],
)
def test_build_dropdown_fields_props_dropdown(input_field_section, language):
    variable_input_field_for_dropdown = input_field_section.children[2]
    assert variable_input_field_for_dropdown.value is None
    variable_input_field_for_dropdown.value = "IDENTIFIKATOR"
    assert variable_input_field_for_dropdown.value == "IDENTIFIKATOR"
    assert isinstance(variable_input_field_for_dropdown, ssb.Dropdown)
    assert variable_input_field_for_dropdown._type == "Dropdown"  # noqa: SLF001
    assert variable_input_field_for_dropdown.header == "Variabelens rolle"
    assert variable_input_field_for_dropdown.items == get_enum_options_for_language(
        enums.VariableRole,
        SupportedLanguages(language),
    )


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_props_checkbox(input_field_section):
    variable_checkbox_field = input_field_section.children[4]
    assert isinstance(variable_checkbox_field, dbc.Checkbox)
    assert variable_checkbox_field._type == "Checkbox"  # noqa: SLF001
    assert variable_checkbox_field.value is None
    variable_checkbox_field.value = True
    assert variable_checkbox_field.value is True


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_props_url(input_field_section):
    variable_input_field_for_url = input_field_section.children[3]
    assert isinstance(variable_input_field_for_url, ssb.Input)
    assert variable_input_field_for_url.type == "url"
    assert variable_input_field_for_url.value is None
    input_value = "https://hattemaker.com"
    variable_input_field_for_url.value = input_value
    assert variable_input_field_for_url.value == input_value


@pytest.mark.parametrize(
    ("input_field_section"),
    [
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="hoveddiagnose"),
            NORSK_NYNORSK,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="pers_id"),
            NORSK_BOKMÅL,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="ber_bruttoformue"),
            ENGLISH,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="sykepenger"),
            NORSK_BOKMÅL,
        ),
    ],
)
def test_build_input_fields_props_optional_input_list(input_field_section):
    variable_input_field_for_data_source = input_field_section.children[0]
    assert variable_input_field_for_data_source.type == "text"
    assert variable_input_field_for_data_source.value is None
    assert isinstance(variable_input_field_for_data_source, ssb.Input)
    assert variable_input_field_for_data_source.debounce is True
    assert variable_input_field_for_data_source.label == "Datakilde"
