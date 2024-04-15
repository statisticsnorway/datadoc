"""Test function build_input_field_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_input_field_section
from datadoc.frontend.fields.display_base import MetadataCheckboxField
from datadoc.frontend.fields.display_base import MetadataDropdownField
from datadoc.frontend.fields.display_base import MetadataInputField
from datadoc.frontend.fields.display_base import MetadataPeriodField
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

VARIABLES_METADATA = OBLIGATORY_VARIABLES_METADATA + OPTIONAL_VARIABLES_METADATA

INPUT_FIELD_SECTION = [
    (
        VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        SupportedLanguages.NORSK_NYNORSK,
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="pers_id"),
        SupportedLanguages.NORSK_BOKMÅL,
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        SupportedLanguages.ENGLISH,
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
        SupportedLanguages.NORSK_BOKMÅL,
    ),
]


def test_build_input_field_section_no_input():
    """Assert build with empty inputs returns dash bootstrap Form component and empty children list."""
    input_section = build_input_field_section(
        [],
        "",
        "",
    )
    assert input_section.children == []
    assert isinstance(input_section, dbc.Form)


@pytest.mark.parametrize(
    ("field_list", "variable", "language"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_input_components(field_list, variable, language):
    input_section = build_input_field_section(field_list, variable, language)
    type_input = ssb.Input
    elements_of_input = [
        element for element in input_section.children if isinstance(element, type_input)
    ]
    elements_of_input_and_type_text_url = [
        element
        for element in input_section.children
        if isinstance(element, type_input)
        and element.type == "text"
        or isinstance(element, type_input)
        and element.type == "url"
    ]
    variable_identifier_input = [
        element
        for element in VARIABLES_METADATA
        if isinstance(element, MetadataInputField)
    ]
    assert all(isinstance(field, ssb.Input) for field in elements_of_input)
    for item in elements_of_input_and_type_text_url:
        assert item.debounce is True
    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(
            elements_of_input_and_type_text_url,
            variable_identifier_input,
        )
    )


@pytest.mark.parametrize(
    ("field_list", "variable", "language"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_checkbox_components(field_list, variable, language):
    """Test checkbox fields for variabel identifiers."""
    input_section = build_input_field_section(field_list, variable, language)
    type_checkbox = ssb.Checkbox
    elements_of_checkbox = [
        element
        for element in input_section.children
        if isinstance(element, type_checkbox)
    ]
    variable_identifier_checkbox = [
        element
        for element in VARIABLES_METADATA
        if isinstance(element, MetadataCheckboxField)
    ]
    assert all(isinstance(item, type_checkbox) for item in elements_of_checkbox)
    for item in elements_of_checkbox:
        assert item._type == "Checkbox"  # noqa: SLF001
    for item in elements_of_checkbox:
        assert item.disabled is False
    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(elements_of_checkbox, variable_identifier_checkbox)
    )


@pytest.mark.parametrize(
    ("field_list", "variable", "language"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_date(field_list, variable, language):
    """Test Input field type 'url'."""
    input_section = build_input_field_section(field_list, variable, language)
    type_input = ssb.Input
    elements_of_input = [
        element for element in input_section.children if isinstance(element, type_input)
    ]
    elements_of_date = [
        element for element in elements_of_input if element.type == "date"
    ]
    variable_identifier_date = [
        element for element in field_list if isinstance(element, MetadataPeriodField)
    ]
    for item1, item2 in zip(elements_of_date, variable_identifier_date):
        assert item1.label == item2.display_name
    assert all(item.debounce is False for item in elements_of_date)


@pytest.mark.parametrize(
    ("field_list", "variable", "language"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_url(field_list, variable, language):
    input_section = build_input_field_section(field_list, variable, language)
    variable_identifier_input = [
        element for element in field_list if isinstance(element, MetadataInputField)
    ]
    variable_identifier_url = [
        element for element in variable_identifier_input if element.type == "url"
    ]
    elements_of_input_and_type_url = [
        element
        for element in input_section.children
        if isinstance(element, ssb.Input) and element.type == "url"
    ]
    assert all(item.debounce is True for item in elements_of_input_and_type_url)
    for item1, item2 in zip(elements_of_input_and_type_url, variable_identifier_url):
        assert item1.label == item2.display_name


@pytest.mark.parametrize(
    ("field_list", "variable", "language"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_dropdown_components(field_list, variable, language):
    """Test props for variable identifiers fields."""
    input_section = build_input_field_section(field_list, variable, language)
    type_dropdown = ssb.Dropdown
    elements_of_dropdown = [
        element
        for element in input_section.children
        if isinstance(element, type_dropdown)
    ]
    variable_identifier_dropdown = [
        element for element in field_list if isinstance(element, MetadataDropdownField)
    ]
    assert all(isinstance(item, type_dropdown) for item in elements_of_dropdown)
    for item in elements_of_dropdown:
        assert item._type == "Dropdown"  # noqa: SLF001
    for item1, item2 in zip(elements_of_dropdown, variable_identifier_dropdown):
        assert item1.header == item2.display_name
    for item1, item2 in zip(elements_of_dropdown, variable_identifier_dropdown):
        assert item1.items == item2.options_getter(language)
