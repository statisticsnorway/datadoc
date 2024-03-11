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

INPUT_FIELD_SECTION = [
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        SupportedLanguages.NORSK_NYNORSK,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="pers_id"),
        SupportedLanguages.NORSK_BOKMÅL,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        SupportedLanguages.ENGLISH,
    ),
    build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
        SupportedLanguages.NORSK_BOKMÅL,
    ),
]


def test_build_input_field_section_no_input_return_empty_list():
    """Test build with empty inputs."""
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
    """Test input field for variable identifier 'NAME' obligatory section."""
    variable_input_field_for_name = input_field_section.children[0]
    assert variable_input_field_for_name.type == "text"
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
                SupportedLanguages.NORSK_NYNORSK,
            ),
            SupportedLanguages.NORSK_NYNORSK,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="pers_id"),
                SupportedLanguages.NORSK_BOKMÅL,
            ),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="ber_bruttoformue"),
                SupportedLanguages.ENGLISH,
            ),
            SupportedLanguages.ENGLISH,
        ),
        (
            build_input_field_section(
                OBLIGATORY_VARIABLES_METADATA,
                model.Variable(short_name="sykepenger"),
                SupportedLanguages.NORSK_BOKMÅL,
            ),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
    ],
)
def test_build_dropdown_fields_props_dropdown(input_field_section, language):
    """Test dropdown field for variable identifier 'VARIABLE_ROLE' obligatory section."""
    variable_input_field_for_dropdown = input_field_section.children[2]
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
    """Test checkbox field for variabel identifier 'DIRECT_PERSON_IDENTIFYING' obligatory section."""
    variable_checkbox_field = input_field_section.children[4]
    assert isinstance(variable_checkbox_field, dbc.Checkbox)
    assert variable_checkbox_field._type == "Checkbox"  # noqa: SLF001


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_props_url(input_field_section):
    """Test Input field type 'url' for variable identifier 'DEFINITION_URI' obligatory section."""
    variable_input_field_for_url = input_field_section.children[3]
    assert isinstance(variable_input_field_for_url, ssb.Input)
    assert variable_input_field_for_url.type == "url"


@pytest.mark.parametrize(
    ("input_field_section"),
    [
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="hoveddiagnose"),
            SupportedLanguages.NORSK_NYNORSK,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="pers_id"),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="ber_bruttoformue"),
            SupportedLanguages.ENGLISH,
        ),
        build_input_field_section(
            OPTIONAL_VARIABLES_METADATA,
            model.Variable(short_name="sykepenger"),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
    ],
)
def test_build_input_fields_props_optional_input_list(input_field_section):
    """Test Input field for variable identifier 'DATA_SOURCE' optional section."""
    variable_input_field_for_data_source = input_field_section.children[0]
    assert variable_input_field_for_data_source.type == "text"
    assert isinstance(variable_input_field_for_data_source, ssb.Input)
    assert variable_input_field_for_data_source.debounce is True
    assert variable_input_field_for_data_source.label == "Datakilde"
