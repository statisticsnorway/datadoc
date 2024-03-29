"""Test function build_edit_section."""

import pytest
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA


@pytest.mark.parametrize(
    ("build_edit_section"),
    [
        build_edit_section([], "", model.Variable(), ""),
        build_edit_section(
            OBLIGATORY_VARIABLES_METADATA,
            "",
            model.Variable(short_name="pers_id"),
            SupportedLanguages.NORSK_BOKMÅL,
        ),
    ],
)
def test_build_edit_section(build_edit_section):
    title = build_edit_section.children[0].children
    form = build_edit_section.children[1]
    assert title == build_edit_section.id["title"]
    assert form is not None
