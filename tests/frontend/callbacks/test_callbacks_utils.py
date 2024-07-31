from enum import Enum

import pytest
from dash import html
from datadoc_model import model

from datadoc.backend.src.enums import LanguageStringsEnum
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import get_language_strings_enum
from datadoc.frontend.callbacks.utils import render_tabs


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
    "model_enum",
    [
        model.Assessment,
        model.DataSetStatus,
        model.DataSetState,
        model.DataType,
        model.VariableRole,
        model.TemporalityTypeType,
    ],
)
def test_get_language_strings_enum(model_enum: Enum):
    assert issubclass(get_language_strings_enum(model_enum), LanguageStringsEnum)  # type: ignore [arg-type]


def test_get_language_strings_enum_unknown():
    class TestEnum(Enum):
        """Test enum."""

        TEST = "test"

    with pytest.raises(AttributeError):
        get_language_strings_enum(TestEnum)


@pytest.mark.parametrize(
    ("tab", "content"),
    [
        ("dataset", "Datasett detaljer"),
        ("variables", "Variabel detaljer"),
    ],
)
def test_render_tabs(tab, content):
    result = render_tabs(tab)
    assert isinstance(result, html.Article)
    assert result.children[0].children[0].children == content
