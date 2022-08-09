from dash import Dash

from datadoc.app import build_app
from datadoc.DataDocMetadata import DataDocMetadata
import datadoc.state as state
from .utils import TEST_PARQUET_FILEPATH


def test_build_app():
    state.metadata = DataDocMetadata(TEST_PARQUET_FILEPATH)
    app = build_app(Dash)
    assert app.config["name"] == "Datadoc"
    assert len(app.callback_map.items()) > 0
