"""Test function build_dataset_edit_section."""

from dash import html
from datadoc_model import model

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import update_global_language_state
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA

# list DatasetFieldTypes


def test_build_dataset_section():
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    update_global_language_state(SupportedLanguages(SupportedLanguages.NORSK_BOKMÅL))
    edit_section = build_dataset_edit_section(
        "Obligatorisk",
        NON_EDITABLE_DATASET_METADATA,
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    )
    assert edit_section is not None
    assert isinstance(edit_section, html.Section)
