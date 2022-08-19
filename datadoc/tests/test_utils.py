from datadoc.tests.test_callbacks import BOKMÅL_NAME, LANGUAGE_OBJECT
from datadoc.utils import calculate_percentage, get_display_values, running_in_notebook
from datadoc_model.Enums import SupportedLanguages
from datadoc_model.Model import DataDocVariable


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33


def test_get_display_values():
    variable = DataDocVariable(name=LANGUAGE_OBJECT)
    values = get_display_values(variable, SupportedLanguages.NORSK_BOKMÅL)
    assert values["name"] == BOKMÅL_NAME
