from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup, PageElement, ResultSet

VARDOK_SEARCH_URI = "https://www.ssb.no/a/metadata/definisjoner/variabler/solr.cgi"
VARDOK_METADATA_URI_BASE = "https://www.ssb.no/a/xml"


@dataclass
class VariableDefinition:
    title: str
    uri: str
    identifier: str


def get_vardok_uri(title: PageElement) -> str:
    """Extract the href from search result HTML
    Example HTML: <th class="header" colspan="2"><a href="/metadata/conceptvariable/vardok/2571/nb">Kraftforetak</a></th>
    """
    return VARDOK_METADATA_URI_BASE + title.find_all("a", href=True)[0]["href"]


def get_vardok_identifier(title: PageElement) -> str:
    """Extract the vardok identifier from the URI
    Example: /metadata/conceptvariable/vardok/2571/nb -> 2571"""
    uri = get_vardok_uri(title)
    return uri.split("/")[-2]


def get_search_results(search_text: str) -> ResultSet:
    """Make the call to the Vardok search page. Return a list of up to 10 results (the first page) as HTML elements"""
    response = requests.get(
        VARDOK_SEARCH_URI,
        params=f"q='{search_text}'&ref=conceptvariable&sort=score+desc",
    )
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find_all("th", "header")


def search_vardok(search_text: str) -> List[VariableDefinition]:
    """Find a search term in Vardok. Returns a list of up to 10 possibly matching definitions."""
    definitions: List[VariableDefinition] = []
    for title in get_search_results(search_text):
        definitions.append(
            VariableDefinition(
                title=title.get_text(),
                uri=get_vardok_uri(title),
                identifier=get_vardok_identifier(title),
            )
        )
    return definitions
