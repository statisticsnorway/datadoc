"""Tests for new variable design."""

import pytest

from datadoc.frontend.components.resources_test_new_variables import build_edit_section

# Import the names of callback functions you want to test
from datadoc.frontend.components.resources_test_new_variables import build_ssb_accordion
from datadoc.frontend.fields.display_new_variables import OPTIONAL_VARIABLES_METADATA

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
def variable_accordion(build_variable):
    return build_ssb_accordion(
        obligatory_header,
        build_variable["id"],
        build_variable["variable_short_name"],
        edit_sections,
    )


def test_callback_populate_accordion_workspace(build_variable):
    callback_input = ENGLISH
    output = build_ssb_accordion(
        build_variable["variable_short_name"],
        build_variable["id"],
        build_variable["variable_short_name"],
        children=build_edit_section(
            OPTIONAL_VARIABLES_METADATA,
            "Anbefalt",
            build_variable["variable_short_name"],
            callback_input,
        ),
    )
    assert output is not None


"""def test_run_callback_populate_accordion_workspace():
    def run_callback():
        context_value.set(
            AttributeDict(triggered_inputs=[{"prop_id": "language-dropdown"}]),
        )
        # return

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert output == ""

"""
# accept variable_metadata_input
# callback populate_accordion_workspace(ENGLISH)
# callback_accept_variable_metadata_input
