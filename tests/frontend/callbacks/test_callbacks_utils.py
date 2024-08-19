import pytest
from dapla_metadata.datasets import model
from dash import html

from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import render_tabs
from datadoc.frontend.callbacks.utils import select_tabs
from datadoc.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc.frontend.components.identifiers import SECTION_WRAPPER_ID


def test_find_existing_language_string_no_existing_strings(bokmål_name: str):
    dataset_metadata = model.Dataset()
    assert find_existing_language_string(
        dataset_metadata,
        bokmål_name,
        "name",
        "nb",
    ) == model.LanguageStringType(
        [model.LanguageStringTypeItem(languageCode="nb", languageText=bokmål_name)],
    )


def test_find_existing_language_string_no_existing_strings_empty_value():
    dataset_metadata = model.Dataset()
    assert (
        find_existing_language_string(
            dataset_metadata,
            "",
            "name",
            "nb",
        )
        is None
    )


def test_find_existing_language_string_pre_existing_strings(
    english_name: str,
    bokmål_name: str,
    nynorsk_name: str,
    language_object: model.LanguageStringType,
):
    dataset_metadata = model.Dataset()
    dataset_metadata.name = language_object
    language_strings = find_existing_language_string(
        dataset_metadata,
        nynorsk_name,
        "name",
        "nn",
    )
    assert language_strings == model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="en", languageText=english_name),
            model.LanguageStringTypeItem(languageCode="nb", languageText=bokmål_name),
            model.LanguageStringTypeItem(languageCode="nn", languageText=nynorsk_name),
        ],
    )


@pytest.mark.parametrize(
    ("tab", "identifier"),
    [
        ("dataset", SECTION_WRAPPER_ID),
        ("variables", ACCORDION_WRAPPER_ID),
    ],
)
def test_render_tabs(tab: str, identifier: str):
    result = render_tabs(tab)
    assert isinstance(result, html.Article)
    assert result.children[-1].id == identifier


def test_switch_tabs():
    keydown_right = {"key": "ArrowRight"}
    keydown_left = {"key": "ArrowLeft"}
    assert select_tabs(keydown_right, "dataset") == "variables"
    assert select_tabs(keydown_right, "variables") == "dataset"
    assert select_tabs(keydown_left, "dataset") == "variables"
    assert select_tabs(keydown_left, "variables") == "dataset"
