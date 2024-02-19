"""Smoke tests."""

from datadoc import state
from datadoc.app import get_app


def test_get_app(subject_mapping_fake_statistical_structure):
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    app, _ = get_app()
    assert app.config["name"] == "Datadoc"
    assert len(app.callback_map.items()) > 0
