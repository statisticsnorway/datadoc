"""Tests for the utils module."""

from datadoc_model.model import Variable

from datadoc.enums import SupportedLanguages
from datadoc.utils import calculate_percentage
from datadoc.utils import get_display_values
from datadoc.utils import running_in_notebook
from tests.test_callbacks import BOKMÅL_NAME
from tests.test_callbacks import LANGUAGE_OBJECT


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33  # noqa: PLR2004


def test_get_display_values():
    variable = Variable(name=LANGUAGE_OBJECT)
    values = get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    assert values["name"] == BOKMÅL_NAME
