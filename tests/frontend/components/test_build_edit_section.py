"""Test function build_edit_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from dataset import model

from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA


@pytest.mark.usefixtures("_code_list_fake_classifications_variables")
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


@pytest.mark.usefixtures("_code_list_fake_classifications_variables")
@pytest.mark.parametrize(
    ("field_list", "title", "variable"),
    [
        (
            [],
            "",
            model.Variable(),
        ),
        (
            OPTIONAL_VARIABLES_METADATA,
            "Anbefalt",
            model.Variable(short_name="sivilstand"),
        ),
        (
            OBLIGATORY_VARIABLES_METADATA,
            "Obligatorisk",
            model.Variable(short_name="sykepenger"),
        ),
    ],
)
def test_build_edit_section_children_return_correct_components(
    field_list,
    title,
    variable,
):
    """Assert method has a list of children which returns SSB dash component Title and dash bootstrap Form."""
    edit_section = build_edit_section(field_list, title, variable)
    title = edit_section.children[0]
    form = edit_section.children[1]
    assert isinstance(title, ssb.Title)
    assert isinstance(form, dbc.Form)


@pytest.mark.usefixtures("_code_list_fake_classifications_variables")
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
