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
    desired_type = ssb.Input
    elements_of_input = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert [
        isinstance(elements_of_input[i], ssb.Input)
        for i, field in enumerate(elements_of_input)
    ]
    assert [
        type(elements_of_input[i]) == VariablesInputField
        for i, field in enumerate(elements_of_input)
    ]
    assert [
        elements_of_input[i].debounce is True
        for i, field in enumerate(elements_of_input)
    ]


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_dropdown_components(input_field_section):
    """Test dropdown fields for variabel identifiers."""
    desired_type = ssb.Dropdown
    elements_of_dropdown = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert [
        isinstance(elements_of_dropdown[i], desired_type)
        for i, field in enumerate(elements_of_dropdown)
    ]
    assert [
        isinstance(elements_of_dropdown[i], VariablesDropdownField)
        for i, field in enumerate(elements_of_dropdown)
    ]
    assert [
        elements_of_dropdown[i]._type == "Dropdown"  # noqa: SLF001
        for i, field in enumerate(elements_of_dropdown)
    ]


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_checkbox_components(input_field_section):
    """Test checkbox fields for variabel identifiers."""
    desired_type = dbc.Checkbox
    elements_of_checkbox = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    assert [
        isinstance(elements_of_checkbox[i], desired_type)
        for i, field in enumerate(elements_of_checkbox)
    ]
    assert [
        isinstance(elements_of_checkbox[i], VariablesCheckboxField)
        for i, field in enumerate(elements_of_checkbox)
    ]
    assert [
        elements_of_checkbox[i]._type == "Checkbox"  # noqa: SLF001
        for i, field in enumerate(elements_of_checkbox)
    ]
    assert [
        elements_of_checkbox[i].disabled is False
        for i, field in enumerate(elements_of_checkbox)
    ]


@pytest.mark.parametrize(
    ("input_field_section"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_date(input_field_section):
    """Test Input field type 'url'."""
    desired_type = ssb.Input
    elements_of_input = list(
        filter(lambda x: isinstance(x, desired_type), input_field_section.children),
    )
    elements_of_date = list(
        filter(lambda x: (x.type == "date"), elements_of_input),
    )
    assert [
        isinstance(elements_of_date[i], VariablesPeriodField)
        for i, field in enumerate(elements_of_date)
    ]


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
def test_build_input_fields_props(input_field_section, language):
    """Test props for variable identifiers fields."""
    type_input = ssb.Input
    elements_of_input = list(
        filter(lambda x: isinstance(x, type_input), input_field_section.children),
    )
    variable_identifier_input = list(
        filter(lambda x: isinstance(x, VariablesInputField), VARIABLES_METADATA),
    )
    variable_identifier_input_date = list(
        filter(lambda x: isinstance(x, VariablesPeriodField), VARIABLES_METADATA),
    )
    variable_inputs = variable_identifier_input + variable_identifier_input_date
    type_dropdown = ssb.Dropdown
    elements_of_dropdown = list(
        filter(lambda x: isinstance(x, type_dropdown), input_field_section.children),
    )
    variable_identifier_dropdown = list(
        filter(lambda x: isinstance(x, VariablesDropdownField), VARIABLES_METADATA),
    )
    type_checkbox = dbc.Checkbox
    elements_of_checkbox = list(
        filter(lambda x: isinstance(x, type_checkbox), input_field_section.children),
    )
    variable_identifier_checkbox = list(
        filter(lambda x: isinstance(x, VariablesCheckboxField), VARIABLES_METADATA),
    )
    elements_of_date = list(
        filter(lambda x: (x.type == "date"), elements_of_input),
    )
    elements_of_url = list(
        filter(lambda x: (x.type == "url"), variable_identifier_input),
    )
    assert [
        field.items == variable_identifier_dropdown[i].options_getter(language)
        for i, field in enumerate(
            elements_of_dropdown,
        )
    ]
    assert [
        elements_of_input[i].label == variable_inputs[i].display_name
        for i, field in enumerate(
            elements_of_input,
        )
    ]
    assert [
        elements_of_dropdown[i].header == variable_identifier_dropdown[i].display_name
        for i, field in enumerate(
            elements_of_dropdown,
        )
    ]
    assert [
        elements_of_checkbox[i].label == variable_identifier_checkbox[i].display_name
        for i, field in enumerate(
            elements_of_checkbox,
        )
    ]
    assert [
        elements_of_date[i].debounce is False
        for i, field in enumerate(
            variable_identifier_input_date,
        )
    ]
    assert [elements_of_url[i].url is True for i, field in enumerate(elements_of_url)]
