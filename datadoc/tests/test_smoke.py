"""Smoke tests."""
import pytest
from dash import Dash
from jupyter_dash import JupyterDash

from datadoc import state
from datadoc.app import build_app
from datadoc.backend.datadoc_metadata import DataDocMetadata

from .utils import TEST_PARQUET_FILEPATH


@pytest.mark.parametrize("dash_class", [Dash, JupyterDash])
def test_build_app_dash(dash_class: Dash):
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    app = build_app(dash_class)
    assert app.config["name"] == "Datadoc"
    assert len(app.callback_map.items()) > 0
