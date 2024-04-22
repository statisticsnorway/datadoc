"""Test function build_edit_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc import state
from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA
from tests.backend.test_code_list import CODE_LIST_DIR
from tests.utils import TEST_RESOURCES_DIRECTORY


@pytest.mark.parametrize(
    ("field_list", "title", "variable"),
    [
        ([], "", model.Variable()),
        (
            OBLIGATORY_VARIABLES_METADATA,
            "",
            model.Variable(short_name="pers_id"),
        ),
    ],
)
def test_build_edit_section_return_correct_component(
    field_list,
    title,
    variable,
):
    """Assert method returns html section."""
    edit_section = build_edit_section(field_list, title, variable)
    assert isinstance(edit_section, html.Section)


@pytest.mark.parametrize(
    ("field_list", "title", "variable", "code_list_csv_filepath_nb"),
    [
        (
            [],
            "",
            model.Variable(),
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
        (
            OPTIONAL_VARIABLES_METADATA,
            "Anbefalt",
            model.Variable(short_name="sivilstand"),
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
        (
            OBLIGATORY_VARIABLES_METADATA,
            "Obligatorisk",
            model.Variable(short_name="sykepenger"),
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
    ],
)
def test_build_edit_section_children_return_correct_components(
    field_list,
    title,
    variable,
    code_list_fake_structure,
):
    """Assert method has a list of children which returns SSB dash component Title and dash bootstrap Form."""
    state.measurement_units = code_list_fake_structure
    state.measurement_units.wait_for_external_result()
    edit_section = build_edit_section(field_list, title, variable)
    title = edit_section.children[0]
    form = edit_section.children[1]
    assert isinstance(title, ssb.Title)
    assert isinstance(form, dbc.Form)


@pytest.mark.parametrize(
    ("field_list", "title", "variable"),
    [
        ([], "", model.Variable()),
        (
            OBLIGATORY_VARIABLES_METADATA,
            "",
            model.Variable(short_name="sykepenger"),
        ),
    ],
)
def test_build_edit_section_has_correct_id(field_list, title, variable):
    """Assert dictionary id is build correctly with 'type' and 'title'.

    'title' is children of Title component (which is the same as the content/value of Title)
    """
    edit_section = build_edit_section(field_list, title, variable)
    title = edit_section.children[0].children
    assert edit_section.id == {"type": "edit-section", "title": title}
