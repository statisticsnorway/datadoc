"""Test methods for building tab content."""

import pytest
from dash import html

from datadoc.frontend.components.dataset_tab import build_dataset_tab
from datadoc.frontend.components.variables_tab import build_variables_tab


@pytest.mark.parametrize(
    ("title", "component"),
    [
        ("Datasett detaljer", build_dataset_tab()),
        ("Variabel detaljer", build_variables_tab()),
    ],
)
def test_build_tab_sections(title, component):
    assert isinstance(component, html.Article)
    assert component.children[0].children[0].children == title
