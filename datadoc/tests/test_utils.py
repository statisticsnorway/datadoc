"""Tests for the utils module."""

from datadoc_model.model import Variable

from datadoc.enums import SupportedLanguages
from datadoc.tests.test_callbacks import BOKMÅL_NAME, LANGUAGE_OBJECT
from datadoc.utils import calculate_percentage, get_display_values, running_in_notebook


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33  # noqa: PLR2004


def test_get_display_values():
    variable = Variable(name=LANGUAGE_OBJECT)
    values = get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    assert values["name"] == BOKMÅL_NAME
