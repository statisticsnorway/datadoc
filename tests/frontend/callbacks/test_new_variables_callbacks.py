"""Tests for new variable design."""

import pytest

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


def test_build_new_variables_workspace():
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    state.metadata.variables_lookup = DISPLAY_STUB_VARIABLES
    result_list = build_new_variables_workspace()
    assert result_list is not None


# self.variables_lookup dict[str, model.Variable] = {}


def test_callback_populate_accordion_workspace(build_variable):
    callback_input = ENGLISH
    output = build_ssb_accordion(
        build_variable["variable_short_name"],
        build_variable["id"],
        build_variable["variable_short_name"],
        children=build_edit_section(
            stub_variables_metadata,
            "Anbefalt",
            build_variable["variable_short_name"],
            callback_input,
        ),
    )
    assert output is not None


# callback_accept_variable_metadata_input
