"""Tests for new variable design."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.new_variables import build_new_variables_workspace
from datadoc.frontend.components.resources_test_new_variables import build_edit_section
from datadoc.frontend.components.resources_test_new_variables import build_ssb_accordion

# testdata/stubs/fixture - mocks?
obligatory_header = "Obligatorisk"
reccomended_header = "Anbefalt"
accordion_key = {"type": "variables-accordion", "id": "pers_id"}
variable_short_name = "pers_id"
edit_sections = []
language = ""
NORSK_BOKMÅL = "nb"
NORSK_NYNORSK = "nn"
ENGLISH = "en"

variable_short_names = ["pers_id", "tidspunkt", "sykepenger"]

empty_variables_metadata = []


@pytest.fixture()
def build_variable():
    return {
        "variable_short_name": "pers_id",
        "id": {"type": "variables-accordion", "id": "pers_id"},
    }


@pytest.fixture()
def build_variables_list(build_variable):
    variables_list = []
    for i in variable_short_names:
        variables_list += build_variable(i, {"variables-accordion", i})
    return variables_list


@pytest.fixture()
def build_test_variables():
    return [
        (
            {
                "variable_short_name": i,
                "id": {"type": "variables-accordion", "id": i},
            }
        )
        for i in variable_short_names
    ]


@pytest.fixture()
def variable_accordion(build_variable):
    return build_ssb_accordion(
        obligatory_header,
        build_variable["id"],
        build_variable["variable_short_name"],
        edit_sections,
    )


def test_callback_populate_accordion_workspace_return_correct_component(build_variable):
    callback_input_language = ENGLISH
    output = build_ssb_accordion(
        build_variable["variable_short_name"],
        build_variable["id"],
        build_variable["variable_short_name"],
        children=build_edit_section(
            empty_variables_metadata,
            "Anbefalt",
            build_variable["variable_short_name"],
            callback_input_language,
        ),
    )
    assert output != []
    assert isinstance(output, ssb.Accordion)


def test_callback_populate_accordion_workspace_not_return_incorrect_component(
    build_variable,
):
    callback_input_language = ENGLISH
    output = build_ssb_accordion(
        build_variable["variable_short_name"],
        build_variable["id"],
        build_variable["variable_short_name"],
        children=build_edit_section(
            empty_variables_metadata,
            "Anbefalt",
            build_variable["variable_short_name"],
            callback_input_language,
        ),
    )
    assert not isinstance(output, dbc.Accordion)


def test_callback_function(metadata):
    state.metadata = metadata
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    state.metadata.variables = state.metadata.variables_lookup["pers_id"]
    result = build_new_variables_workspace()
    assert isinstance(result[0], ssb.Accordion)


def test_callback_empty_language_raises_attribute_error(metadata):
    state.metadata = metadata
    state.current_metadata_language = ""
    state.metadata.variables = state.metadata.variables_lookup["sykepenger"]
    with pytest.raises(AttributeError) as excinfo:
        build_new_variables_workspace()
    assert "'str' object has no attribute 'value" in str(excinfo.value)


"""
def callback_accept_variable_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> dbc.Alert:
        message = accept_variable_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["variable_short_name"],
            ctx.triggered_id["id"],
        )
        if not message:
            # No error to display.
            return False, ""
        return True, message
"""
