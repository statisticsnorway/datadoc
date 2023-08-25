"""Smoke tests."""

from datadoc import state
from datadoc.app import get_app
from datadoc.backend.datadoc_metadata import DataDocMetadata

from .utils import TEST_PARQUET_FILEPATH


def test_get_app():
    state.metadata = DataDocMetadata(str(TEST_PARQUET_FILEPATH))
    app, _ = get_app()
    assert app.config["name"] == "Datadoc"
    assert len(app.callback_map.items()) > 0
