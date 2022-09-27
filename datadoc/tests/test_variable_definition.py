import re
from unittest.mock import Mock
from urllib.parse import urlparse

import pytest
from bs4 import BeautifulSoup

from datadoc.backend.VariableDefinition import search_vardok


@pytest.fixture()
def mock_valid_search(mocker):
    mock: Mock = mocker.patch(
        "datadoc.backend.VariableDefinition.get_search_results",
        return_value=[
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2931/nb">Produksjon av <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2928/nb">Import av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2929/nb">Eksport av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2930/nb">Nettoforbruk av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2649/nb">Nettoforbruk av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2645/nb">Bruttoforbruk av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2933/nb">Pris for <em>kraft</em> og nettleie i alt</a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/3440/nb">Total produksjon av elektrisk <em>kraft</em></a></th>'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2571/nb">Kraftforetak</a></th>,'
            ),
            BeautifulSoup(
                '<th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/308/nb">Arbeidskraftkostnader</a></th>'
            ),
        ],
    )
    return mock


@pytest.fixture()
def mock_invalid_search(mocker):
    mock: Mock = mocker.patch(
        "datadoc.backend.VariableDefinition.get_search_results", return_value=[]
    )
    return mock


def test_search_vardok(mock_valid_search):
    results = search_vardok("kraft")
    assert len(results) == 10
    for r in results:
        assert re.match(r"^[\d]{1,6}$", r.identifier)  # noqa W605
        assert urlparse(r.uri)


def test_search_vardok_no_results(mock_invalid_search):
    results = search_vardok("alwehfliwraubvr")
    assert len(results) == 0
