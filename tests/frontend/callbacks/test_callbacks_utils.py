import random
from enum import Enum

import pytest
from datadoc_model import model

from datadoc import enums
from datadoc import state
from datadoc.enums import LanguageStringsEnum
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import get_language_strings_enum
from datadoc.frontend.callbacks.utils import get_options_for_language
from datadoc.frontend.callbacks.utils import update_global_language_state


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


def test_update_global_language_state():
    language: SupportedLanguages = (  # type: ignore[annotation-unchecked]
        random.choice(  # noqa: S311 not for cryptographic purposes
            list(SupportedLanguages),
        )
    )
    update_global_language_state(language)
    assert state.current_metadata_language == language


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
    "enum",
    [
        enums.Assessment,
        enums.DataSetState,
        enums.DataSetStatus,
        enums.TemporalityTypeType,
        enums.DataType,
        enums.VariableRole,
    ],
)
@pytest.mark.parametrize("language", list(SupportedLanguages))
def test_get_options_for_language(language: SupportedLanguages, enum: Enum):
    for o in get_options_for_language(language, enum):
        assert list(o.keys()) == ["label", "value"]
        assert isinstance(o["label"], str)
        assert isinstance(o["value"], str)
