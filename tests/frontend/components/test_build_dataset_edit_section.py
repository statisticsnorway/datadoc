"""Test function build_dataset_edit_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.fields.display_base import DatasetFieldTypes
from datadoc.frontend.fields.display_base import MetadataDropdownField
from datadoc.frontend.fields.display_base import MetadataInputField
from datadoc.frontend.fields.display_base import MetadataPeriodField
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
    and m.identifier != DatasetIdentifiers.SUBJECT_FIELD.value
    and m.identifier != DatasetIdentifiers.OWNER.value
]

INPUT_DATA_BUILD_DATASET_SECTION = [
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
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_section_is_html_section(
    title,
    field_types,
    language,
    dataset,
    key,
):
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
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_has_title_component(title, field_types, language, dataset, key):
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
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_is_form_component(title, field_types, language, dataset, key):
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
def test_build_dataset_edit_section_renders_ssb_components(
    edit_section,
    expected_inputs,
    expected_dropdowns,
):
    fields = edit_section.children[1].children

    input_components = [element for element in fields if isinstance(element, ssb.Input)]
    dropdown_components = [
        element for element in fields if isinstance(element, ssb.Dropdown)
    ]
    assert len(input_components) == expected_inputs
    assert len(dropdown_components) == expected_dropdowns


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_edit_section_input_component_props(
    title,
    field_types,
    language,
    dataset,
    key,
):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    fields = edit_section.children[1].children
    input_components = [element for element in fields if isinstance(element, ssb.Input)]
    for item in input_components:
        assert item.type in ("text", "url", "date")
    for item in input_components:
        if item.type in ("text", "url"):
            assert item.debounce is True
    for item in input_components:
        if item.type == "date":
            assert item.debounce is False
    for item in input_components:
        assert item.label != ""


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_edit_section_dropdown_component_props(
    title,
    field_types,
    language,
    dataset,
    key,
):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    fields = edit_section.children[1].children
    dropdown_components = [
        element for element in fields if isinstance(element, ssb.Dropdown)
    ]
    for item in dropdown_components:
        assert item.items != []
    for item in dropdown_components:
        assert item.header != ""


# Test data sorted by DatasetFieldTypes
DATASET_INPUT_FIELD_LIST: list[DatasetFieldTypes] = [
    m for m in DISPLAY_DATASET.values() if isinstance(m, MetadataInputField)
]

DATASET_INPUT_URL_FIELD_LIST: list[DatasetFieldTypes] = [
    m
    for m in DISPLAY_DATASET.values()
    if isinstance(m, MetadataInputField) and m.type == "url"
]

DATASET_DATE_FIELD_LIST: list[DatasetFieldTypes] = [
    m for m in DISPLAY_DATASET.values() if isinstance(m, MetadataPeriodField)
]

DATASET_DROPDOWN_FIELD_LIST_MINUS_ATYPICAL: list[DatasetFieldTypes] = [
    m
    for m in DISPLAY_DATASET.values()
    if isinstance(m, MetadataDropdownField)
    and m.identifier != DatasetIdentifiers.UNIT_TYPE.value
    and m.identifier != DatasetIdentifiers.SUBJECT_FIELD.value
    and m.identifier != DatasetIdentifiers.OWNER.value
]


@pytest.mark.parametrize(
    ("edit_section", "expected_num", "expected_component"),
    [
        (
            build_dataset_edit_section(
                "",
                DATASET_INPUT_FIELD_LIST,
                SupportedLanguages.NORSK_BOKMÅL,
                model.Dataset(short_name="input_dataset"),
                {"type": "dataset-edit-section", "id": "recommended-nb"},
            ),
            16,
            ssb.Input,
        ),
        (
            build_dataset_edit_section(
                "",
                DATASET_INPUT_URL_FIELD_LIST,
                SupportedLanguages.NORSK_BOKMÅL,
                model.Dataset(short_name="url_dataset"),
                {"type": "dataset-edit-section", "id": "obligatory-nb"},
            ),
            1,
            ssb.Input,
        ),
        (
            build_dataset_edit_section(
                "title",
                DATASET_DATE_FIELD_LIST,
                SupportedLanguages.NORSK_BOKMÅL,
                model.Dataset(short_name="date_dataset"),
                {"type": "dataset-edit-section", "id": "title-nb"},
            ),
            2,
            ssb.Input,
        ),
        (
            build_dataset_edit_section(
                "dropdown",
                DATASET_DROPDOWN_FIELD_LIST_MINUS_ATYPICAL,
                SupportedLanguages.ENGLISH,
                model.Dataset(short_name="dropdown_dataset"),
                {"type": "dataset-edit-section", "id": "dropdown-en"},
            ),
            4,
            ssb.Dropdown,
        ),
    ],
)
def test_build_dataset_input_fields_from_datasetidentifiers(
    edit_section,
    expected_num,
    expected_component,
):
    fields = edit_section.children[1].children
    assert len(fields) == expected_num
    for item in fields:
        assert isinstance(item, expected_component)
