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

VARIABLES_METADATA = OBLIGATORY_VARIABLES_METADATA + OPTIONAL_VARIABLES_METADATA
TEST_VARIABLE = model.Variable(short_name="sykepenger")

INPUT_FIELD_SECTION = [
    build_input_field_section(
        VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        SupportedLanguages.NORSK_NYNORSK,
    ),
    build_input_field_section(
        VARIABLES_METADATA,
        model.Variable(short_name="pers_id"),
        SupportedLanguages.NORSK_BOKMÅL,
    ),
    build_input_field_section(
        VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        SupportedLanguages.ENGLISH,
    ),
    build_input_field_section(
        VARIABLES_METADATA,
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


# Form


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_input_components(input_field_section):
    """Test input field for variable identifier 'NAME' obligatory section."""
    desired_type = ssb.Input
    input_test_variable = list(
        filter(lambda x: isinstance(x, desired_type), TEST_VARIABLE),
    )
    elements_of_input = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert (isinstance(elements_of_input[i], desired_type) for i in elements_of_input)
    assert (
        elements_of_input[i]._type == "text" for i in elements_of_input  # noqa: SLF001
    )
    assert (
        elements_of_input[i].display_name == input_test_variable[i].display_name
        for i in elements_of_input
    )


# debounce, disabled,label, value
@pytest.mark.parametrize(
    ("input_field_section", "language"),
    [
        (
            build_input_field_section(
                VARIABLES_METADATA,
                model.Variable(short_name="hoveddiagnose"),
                SupportedLanguages.NORSK_NYNORSK,
            ),
            SupportedLanguages.NORSK_NYNORSK,
        ),
        (
            build_input_field_section(
                VARIABLES_METADATA,
                model.Variable(short_name="pers_id"),
                SupportedLanguages.NORSK_BOKMÅL,
            ),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
        (
            build_input_field_section(
                VARIABLES_METADATA,
                model.Variable(short_name="ber_bruttoformue"),
                SupportedLanguages.ENGLISH,
            ),
            SupportedLanguages.ENGLISH,
        ),
        (
            build_input_field_section(
                VARIABLES_METADATA,
                model.Variable(short_name="sykepenger"),
                SupportedLanguages.NORSK_BOKMÅL,
            ),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
    ],
)
def test_build_dropdown_fields_dropdown_components(input_field_section, language):
    """Test dropdown fields."""
    desired_type = ssb.Dropdown
    dropddown_test_variable = list(
        filter(lambda x: isinstance(x, desired_type), TEST_VARIABLE),
    )
    elements_of_dropdown = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert (
        isinstance(elements_of_dropdown[i], desired_type) for i in elements_of_dropdown
    )
    assert (isinstance(dropddown_test_variable[i], desired_type) for i in TEST_VARIABLE)
    assert (
        elements_of_dropdown[i]._type == "Dropdown"  # noqa: SLF001
        for i in elements_of_dropdown
    )
    assert (
        elements_of_dropdown[i].header == dropddown_test_variable[i].header
        for i in elements_of_dropdown
    )
    assert (
        elements_of_dropdown[i].items
        == get_enum_options_for_language(
            enums[i].__name__,
            SupportedLanguages(language),
        )
        for i in elements_of_dropdown
    )


# test one input, dropdown, checkbox, header,
@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_checkbox_components(input_field_section):
    """Test checkbox field for variabel identifier 'DIRECT_PERSON_IDENTIFYING' obligatory section."""
    desired_type = dbc.Checkbox
    checkbox_test_variable = list(
        filter(lambda x: isinstance(x, desired_type), TEST_VARIABLE),
    )
    elements_of_checkbox = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert (
        isinstance(elements_of_checkbox[i], desired_type) for i in elements_of_checkbox
    )
    assert (
        elements_of_checkbox[i]._type == "Checkbox"  # noqa: SLF001
        for i in elements_of_checkbox
    )
    assert (
        elements_of_checkbox[i].description == checkbox_test_variable[i].description
        for i in elements_of_checkbox
    )


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
