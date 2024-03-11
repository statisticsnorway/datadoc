"""Test new variables functions to build layout."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.components.builders import build_input_field_section
from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.fields.display_base import VariablesInputField
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA
from datadoc.utils import get_display_values

# set-up
empty_metadata_input = []
obligatory_metadata_input = OBLIGATORY_VARIABLES_METADATA
optional_metadata_input = OPTIONAL_VARIABLES_METADATA

NORSK_BOKMÅL = "nb"
NORSK_NYNORSK = "nn"
ENGLISH = "en"

ACCORDION_TYPE = "variables-accordion"
ALERTS_TYPE = "variable-input-alerts"
INPUT_TYPE = "variable-inputs"

# Different input lists
ACCORDION_INPUTS = [
    (
        "pers_id",
        {"type": ACCORDION_TYPE, "id": "pers_id"},
        "pers_id",
        empty_metadata_input,
    ),
    (
        "sykepenger",
        {"type": ACCORDION_TYPE, "id": "sykepenger"},
        "sykepenger",
        OPTIONAL_VARIABLES_METADATA,
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        OBLIGATORY_VARIABLES_METADATA,
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        empty_metadata_input,
    ),
    (
        "",
        {"type": ACCORDION_TYPE, "id": ""},
        "ber_bruttoformue",
        OBLIGATORY_VARIABLES_METADATA,
    ),
]

accordion_obligatory_input = build_ssb_accordion(
    "pers_id",
    {"type": ACCORDION_TYPE, "id": "pers_id"},
    "pers_id",
    obligatory_metadata_input,
)
accordion_optional_input = build_ssb_accordion(
    "sykepenger",
    {"type": ACCORDION_TYPE, "id": "sykepenger"},
    "sykepenger",
    optional_metadata_input,
)
accordion_empty_input = build_ssb_accordion(
    "hoveddiagnose",
    {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
    "hoveddiagnose",
    empty_metadata_input,
)
display_variable_datatype = accordion_obligatory_input.children[1].children[1]
display_variable_name = accordion_obligatory_input.children[1].children[0]
display_direct_person_identifying = accordion_obligatory_input.children[1].children[4]

RETURN_CORRECT_COMPONENT = [
    (
        accordion_obligatory_input,
        ssb.Accordion,
    ),
    (accordion_obligatory_input.children[0], html.Section),
    (display_variable_datatype, ssb.Dropdown),
    (display_variable_name, ssb.Input),
    (display_direct_person_identifying, dbc.Checkbox),
    (
        accordion_optional_input,
        ssb.Accordion,
    ),
    (accordion_optional_input.children[1], html.Section),
    (accordion_empty_input, ssb.Accordion),
]

# Remove?
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

INPUT_FIELDS = [
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        NORSK_NYNORSK,
    ),
    (OPTIONAL_VARIABLES_METADATA, model.Variable(short_name="pers_id"), NORSK_BOKMÅL),
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        ENGLISH,
    ),
    (
        OPTIONAL_VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
        NORSK_BOKMÅL,
    ),
]

INPUT_COMPONENTS = [
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
        NORSK_NYNORSK,
    ),
    (OPTIONAL_VARIABLES_METADATA, model.Variable(short_name="pers_id"), NORSK_BOKMÅL),
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
        ENGLISH,
    ),
    (
        OPTIONAL_VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
        NORSK_BOKMÅL,
    ),
]


@pytest.mark.parametrize(
    ("header", "key", "variable_short_name", "children"),
    ACCORDION_INPUTS,
)
def test_build_ssb_accordion(header, key, variable_short_name, children):
    accordion = build_ssb_accordion(header, key, variable_short_name, children)
    assert accordion.id == key


@pytest.mark.parametrize(
    (
        "build",
        "expected_component",
    ),
    RETURN_CORRECT_COMPONENT,
)
def test_build_returns_correct_component(
    build,
    expected_component,
):
    assert (
        isinstance(
            build,
            expected_component,
        )
        for index in RETURN_CORRECT_COMPONENT
    )


# remove?
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


# empty input returns empty string/list
def test_build_edit_section_empty_inputs():
    obligatory_edit_section = build_edit_section(
        empty_metadata_input,
        "",
        "",
        "",
    )
    title = obligatory_edit_section.children[0].children
    form = obligatory_edit_section.children[1]
    assert title == ""
    assert form.children == []


def test_build_input_field_section_no_input_return_empty_list():
    input_section = build_input_field_section(
        empty_metadata_input,
        "",
        "",
    )
    assert input_section.children == []


@pytest.mark.parametrize(
    ("metadata_inputs", "variable", "language"),
    INPUT_FIELDS,
)
def test_build_input_field_section_input_component(
    metadata_inputs,
    variable,
    language,
):
    # TODO(@tilen1976): replace constant expression  # noqa: TD003
    input_section = build_input_field_section(
        metadata_inputs,
        variable,
        language,
    )
    # for input_field in input_section:
    input_field_for_name = VariablesInputField(
        input_section.children[0],
        "Navn",
        "Variabelnavn kan arves fra VarDef, men kan også dokumenteres/endres her.",
    )
    assert input_field_for_name.type == "text"
    name_is_input_field = input_section.children[0]
    assert name_is_input_field.type == input_field_for_name.type
    assert name_is_input_field.value is None
    name_is_input_field.value = "Navnet"
    assert name_is_input_field.value == "Navnet"
    assert isinstance(input_section.children[0], ssb.Input)


def test_build_input_section_component_props(
    # language_object model.LanguageStringType,
):
    # TODO(@tilen1976): refactor, improve, split up  # noqa: TD003
    # values get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    input_section = build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(
            short_name="alm_inntekt",
            name=None,
            data_type="INTEGER",
            variable_role="MEASURE",
            definition_uri="https://hattemaker.com",
            direct_person_identifying="false",
            contains_data_from=2024 - 3 - 10,
            contains_data_until=2024 - 5 - 12,
        ),
        NORSK_BOKMÅL,
    )
    input_example = input_section.children[0]
    dropdown_example2 = input_section.children[1]
    url_example = input_section.children[3]
    dropdown_example = input_section.children[2]
    checkbox_example = input_section.children[4]
    assert input_section.id == "variables-metadata-input"
    assert input_section.children[0].id == {
        "type": "variables-metadata-input",
        "variable_short_name": "alm_inntekt",
        "id": "name",
    }
    assert input_example.debounce is True
    assert input_example.disabled is False
    assert input_example.label == "Navn"
    assert input_example.value is None
    assert url_example.value == "https://hattemaker.com/"
    assert dropdown_example.header == "Variabelens rolle"
    assert dropdown_example.items == [
        {"title": "IDENTIFIKATOR", "id": "IDENTIFIER"},
        {"title": "MÅLEVARIABEL", "id": "MEASURE"},
        {"id": "START_TIME", "title": "STARTTID"},
        {"id": "STOP_TIME", "title": "STOPPTID"},
        {"id": "ATTRIBUTE", "title": "ATTRIBUTT"},
    ]
    assert checkbox_example.value is False
    checkbox_example.value = True
    assert checkbox_example.value is True
    assert dropdown_example2.value == "INTEGER"


def test_with_values(language_object: model.LanguageStringType, bokmål_name: str):
    variable = model.Variable(
        short_name="pers_id",
        name=language_object,
        data_type="DATETIME",
        direct_person_identifying=True,
    )
    values = get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    assert values["name"] == bokmål_name
    assert values["short_name"] == "pers_id"
    assert variable.data_type == "DATETIME"
    assert variable.direct_person_identifying is True
