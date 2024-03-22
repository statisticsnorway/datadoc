"""Test function build_dataset_edit_section."""

from dash import html
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA

# list DatasetFieldTypes


def test_build_dataset_section():
    edit_section = build_dataset_edit_section(
        "Obligatorisk",
        NON_EDITABLE_DATASET_METADATA,
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    )
    assert edit_section is not None
    assert isinstance(edit_section, html.Section)
