"""Tests for new variable design."""

import pytest

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

stub_variables_metadata = []

# OBLIGATORY_VARIABLES_METADATA,
# "Obligatorisk",
# variable,
# state.current_metadata_language.value

# mock/stub state

# state language callback_input = ENGLISH  state.current_metadata_language.value
# state state.metadata.variables_lookup.keys()

#   header: str,
#   key: dict,
#    variable_short_name: str,
#  children list
# stub build_ssb_accordion?

DISPLAY_STUB_VARIABLES = {
    "pers_id": {
        "identifier": "short_name",
        "display_name": "Kortnavn",
        "description": "Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        "obligatory": True,
        "editable": False,
    },
}


# class build variable
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


def test_callback_populate_accordion_workspace(build_variable):
    callback_input_language = ENGLISH
    output = build_ssb_accordion(
        build_variable["variable_short_name"],
        build_variable["id"],
        build_variable["variable_short_name"],
        children=build_edit_section(
            stub_variables_metadata,
            "Anbefalt",
            build_variable["variable_short_name"],
            callback_input_language,
        ),
    )
    assert output != []


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
