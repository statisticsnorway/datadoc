from unittest import mock

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import model
from dash import html

from datadoc import state
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import render_tabs
from datadoc.frontend.callbacks.utils import save_metadata_and_generate_alerts
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


def test_save_and_generate_alerts():
    mock_metadata = mock.Mock()
    mock_metadata.variables = [
        "var1",
        "var2",
    ]
    state.metadata = mock_metadata
    result = save_metadata_and_generate_alerts(
        mock_metadata,
    )

    num_list_of_alerts = 3
    assert len(result) == num_list_of_alerts
    assert (result[1] and result[2]) is None
    assert isinstance(result[0], dbc.Alert)
