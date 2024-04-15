"""Tests for the utils module."""

import pathlib

import tomli
from datadoc_model import model

from datadoc.enums import SupportedLanguages
from datadoc.utils import calculate_percentage
from datadoc.utils import get_app_version
from datadoc.utils import get_display_values
from datadoc.utils import get_languagetext_from_languagestringtype
from datadoc.utils import running_in_notebook


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33  # noqa: PLR2004


def test_get_display_values(
    language_object: model.LanguageStringType,
    bokmål_name: str,
):
    variable = model.Variable(name=language_object)
    values = get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    assert values["name"] == bokmål_name


def test_get_app_version():
    with (pathlib.Path(__file__).parent.parent / "pyproject.toml").open("rb") as f:
        pyproject = tomli.load(f)

    assert get_app_version() == pyproject["tool"]["poetry"]["version"]


def test_get_languagetext_from_languagestringtype(
    language_dicts: list[dict[str, str]],
    bokmål_name: str,
):
    assert (
        get_languagetext_from_languagestringtype(
            language_dicts,
            SupportedLanguages.NORSK_BOKMÅL,
        )
        == bokmål_name
    )
