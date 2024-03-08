"""Test new variables functions to build layout."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.components.builders import build_input_field_section
from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

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

VARIABLE_SHORT_NAMES = [
    "pers_id",
    "sykepenger",
    "ber_bruttoformue",
    "hoveddiagnose",
]


ACCORDION_INPUTS = [
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
        OPTIONAL_VARIABLES_METADATA,
        ssb.Accordion,
    ),
    (
        "ber_bruttoformue",
        {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
        "ber_bruttoformue",
        OBLIGATORY_VARIABLES_METADATA,
        ssb.Accordion,
    ),
    (
        "hoveddiagnose",
        {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
        "hoveddiagnose",
        empty_metadata_input,
        ssb.Accordion,
    ),
    (
        "",
        {"type": ACCORDION_TYPE, "id": ""},
        "ber_bruttoformue",
        OBLIGATORY_VARIABLES_METADATA,
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

INPUT_COMPONENTS_PROPS = [
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
    ),
    (OPTIONAL_VARIABLES_METADATA, model.Variable(short_name="pers_id")),
    (
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
    ),
    (
        OPTIONAL_VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
    ),
]


@pytest.mark.parametrize(
    ("header", "key", "variable_short_name", "children", "expected"),
    ACCORDION_INPUTS,
)
def test_build_ssb_accordion_return_correct_component(
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
    # TODO(@tilen1976): replace constant expression  # noqa: TD003
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


def test_build_edit_section_empty_inputs():
    obligatory_edit_section = build_edit_section(
        empty_metadata_input,
        "",
        "",
        "",
    )
    assert isinstance(obligatory_edit_section, html.Section)
    assert isinstance(obligatory_edit_section.children[0], ssb.Title)
    assert isinstance(obligatory_edit_section.children[1], dbc.Form)


@pytest.mark.parametrize(
    ("metadata_inputs", "variable", "language"),
    INPUT_FIELDS,
)
def test_build_input_field_section(metadata_inputs, variable, language):
    # TODO(@tilen1976): replace constant expression  # noqa: TD003
    input_section = build_input_field_section(
        metadata_inputs,
        variable,
        language,
    )
    assert (
        isinstance(
            (input_section.children[i], (ssb.Input, ssb.Dropdown, dbc.Checkbox)),
        )
        for i in enumerate(INPUT_FIELDS)
    )


def test_build_input_field_section_no_input_return_empty_list():
    input_section = build_input_field_section(
        empty_metadata_input,
        "",
        "",
    )
    assert input_section.children == []


def test_build_input_section_component_props():
    # TODO(@tilen1976): refactor, improve, split up  # noqa: TD003
    input_section = build_input_field_section(
        OBLIGATORY_VARIABLES_METADATA,
        model.Variable(
            short_name="alm_inntekt",
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
    url_example = input_section.children[3]
    dropdown_example = input_section.children[2]
    assert input_section.id == "variables-metadata-input"
    assert input_section.children[0].id == {
        "type": "variables-metadata-input",
        "variable_short_name": "alm_inntekt",
        "id": "name",
    }
    assert input_example.debounce is True
    assert input_example.disabled is False
    assert input_example.label == "Navn"
    assert url_example.value == "https://hattemaker.com/"
    assert dropdown_example.header == "Variabelens rolle"
