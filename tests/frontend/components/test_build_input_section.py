"""Test function build_input_field_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_input_field_section
from datadoc.frontend.fields.display_base import VariablesCheckboxField
from datadoc.frontend.fields.display_base import VariablesDropdownField
from datadoc.frontend.fields.display_base import VariablesInputField
from datadoc.frontend.fields.display_base import VariablesPeriodField
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
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_input_components(input_field_section):
    """Assert fields input field for ."""
    type_input = ssb.Input
    elements_of_input = list(
        filter(lambda x: isinstance(x, type_input), input_field_section.children),
    )
    elements_of_input_and_type_text_url = list(
        filter(
            lambda x: isinstance(x, type_input)
            and x.type == "text"
            or isinstance(x, type_input)
            and x.type == "url",
            input_field_section.children,
        ),
    )
    variable_identifier_input = list(
        filter(lambda x: isinstance(x, VariablesInputField), VARIABLES_METADATA),
    )
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
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_checkbox_components(input_field_section):
    """Test checkbox fields for variabel identifiers."""
    type_checkbox = dbc.Checkbox
    elements_of_checkbox = list(
        filter(lambda x: isinstance(x, type_checkbox), input_field_section.children),
    )
    variable_identifier_checkbox = list(
        filter(lambda x: isinstance(x, VariablesCheckboxField), VARIABLES_METADATA),
    )
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
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_date(input_field_section):
    """Test Input field type 'url'."""
    type_input = ssb.Input
    elements_of_input = list(
        filter(lambda x: isinstance(x, type_input), input_field_section.children),
    )
    elements_of_date = list(
        filter(lambda x: (x.type == "date"), elements_of_input),
    )
    variable_identifier_date = list(
        filter(lambda x: isinstance(x, VariablesPeriodField), VARIABLES_METADATA),
    )
    for item1, item2 in zip(elements_of_date, variable_identifier_date):
        assert item1.label == item2.display_name
    assert all(item.debounce is False for item in elements_of_date)


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_url(input_field_section):
    variable_identifier_input = list(
        filter(lambda x: isinstance(x, VariablesInputField), VARIABLES_METADATA),
    )
    variable_identifier_url = list(
        filter(lambda x: (x.type == "url"), variable_identifier_input),
    )
    elements_of_input_and_type_url = list(
        filter(
            lambda x: isinstance(x, ssb.Input) and x.type == "url",
            input_field_section.children,
        ),
    )
    assert all(item.url is True for item in variable_identifier_url)
    assert all(item.debounce is True for item in elements_of_input_and_type_url)
    for item1, item2 in zip(elements_of_input_and_type_url, variable_identifier_url):
        assert item1.label == item2.display_name


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
def test_build_input_fields_dropdown_components(input_field_section, language):
    """Test props for variable identifiers fields."""
    type_dropdown = ssb.Dropdown
    elements_of_dropdown = list(
        filter(lambda x: isinstance(x, type_dropdown), input_field_section.children),
    )
    variable_identifier_dropdown = list(
        filter(lambda x: isinstance(x, VariablesDropdownField), VARIABLES_METADATA),
    )
    assert all(isinstance(item, type_dropdown) for item in elements_of_dropdown)
    for item in elements_of_dropdown:
        assert item._type == "Dropdown"  # noqa: SLF001
    for item1, item2 in zip(elements_of_dropdown, variable_identifier_dropdown):
        assert item1.header == item2.display_name
    for item1, item2 in zip(elements_of_dropdown, variable_identifier_dropdown):
        assert item1.items == item2.options_getter(language)
