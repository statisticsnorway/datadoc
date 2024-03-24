"""Test function build_dataset_edit_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OPTIONAL_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers

# List of obligatory and editable fields minus dropdowns with atypical options-getters
OBLIGATORY_MINUS_ATYPICAL_DROPDOWNS = [
    m
    for m in DISPLAY_DATASET.values()
    if m.obligatory
    and m.editable
    and m.identifier != DatasetIdentifiers.UNIT_TYPE.value
    and m.identifier != DatasetIdentifiers.KEYWORD.value
    and m.identifier != DatasetIdentifiers.SUBJECT_FIELD.value
    and m.identifier != DatasetIdentifiers.OWNER.value
]

INPUT_DATA = [
    (
        "Obligatorisk",
        NON_EDITABLE_DATASET_METADATA,
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        "",
        [],
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        "",
        [],
        "",
        None,
        {},
    ),
    (
        "Amazing title",
        [],
        SupportedLanguages.ENGLISH,
        None,
        {"type": "dataset-edit-section", "id": "obligatory-en"},
    ),
    (
        "New title",
        OPTIONAL_DATASET_METADATA,
        SupportedLanguages.NORSK_NYNORSK,
        model.Dataset(),
        {},
    ),
    (
        "New title",
        {},
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="last_dataset"),
        {},
    ),
    (
        "Lazy title",
        OBLIGATORY_MINUS_ATYPICAL_DROPDOWNS,
        SupportedLanguages.NORSK_BOKMÅL,
        model.Dataset(short_name="nosy_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
]


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    INPUT_DATA,
)
def test_build_dataset_section(title, field_types, language, dataset, key):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    assert isinstance(edit_section, html.Section)
    assert edit_section._namespace == "dash_html_components"  # noqa: SLF001
    assert edit_section.id == key


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    INPUT_DATA,
)
def test_build_dataset_title(title, field_types, language, dataset, key):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    section_title = edit_section.children[0]
    assert isinstance(section_title, ssb.Title)
    section_title_content = section_title.children
    assert section_title_content == title


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    INPUT_DATA,
)
def test_build_dataset_form(title, field_types, language, dataset, key):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    dataset_form = edit_section.children[1]
    assert dataset_form.id == f"dataset-metadata-input-{title}"
    assert isinstance(dataset_form, dbc.Form)


@pytest.mark.parametrize(
    ("edit_section", "expected_inputs", "expected_dropdowns"),
    [
        (
            build_dataset_edit_section(
                "",
                NON_EDITABLE_DATASET_METADATA,
                SupportedLanguages.NORSK_BOKMÅL,
                model.Dataset(short_name="fantastic_dataset"),
                {"type": "dataset-edit-section", "id": "obligatory-nb"},
            ),
            7,
            0,
        ),
        (
            build_dataset_edit_section(
                "New title",
                OPTIONAL_DATASET_METADATA,
                SupportedLanguages.NORSK_NYNORSK,
                model.Dataset(),
                {},
            ),
            3,
            1,
        ),
        (
            build_dataset_edit_section(
                "",
                OBLIGATORY_MINUS_ATYPICAL_DROPDOWNS,
                SupportedLanguages.ENGLISH,
                model.Dataset(short_name="super_dataset"),
                {"type": "dataset-edit-section", "id": "obligatory-en"},
            ),
            8,
            3,
        ),
    ],
)
def test_build_dataset_input_fields_from_datasetidentifiers_class(
    edit_section,
    expected_inputs,
    expected_dropdowns,
):
    dataset_form = edit_section.children[1]
    fields = dataset_form.children
    inputs = [element for element in fields if isinstance(element, ssb.Input)]
    dropdowns = [element for element in fields if isinstance(element, ssb.Dropdown)]
    for item in inputs:
        if item.type != "date":
            assert item.debounce is True
    for item in inputs:
        assert item.type in ("text", "url", "date")
    for item in inputs:
        assert item.label != ""
    for item in dropdowns:
        assert item.items is not None
    for item in dropdowns:
        assert item.header != ""
    assert len(inputs) == expected_inputs
    assert len(dropdowns) == expected_dropdowns
