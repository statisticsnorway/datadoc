import pytest
from bs4 import BeautifulSoup

from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping

SOURCE_URL = "https://www.ssb.no/xp/_/service/mimir/subjectStructurStatistics"


@pytest.fixture()
def subject_mapping() -> StatisticSubjectMapping:
    return StatisticSubjectMapping(SOURCE_URL)


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_primary_subject"),
    [("nav_statres", "al"), ("unknown_name", None)],
)
def test_get_primary_subject(
    subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_primary_subject: str,
) -> None:
    assert (
        subject_mapping.get_primary_subject(statistic_short_name)
        == expected_primary_subject
    )


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_secondary_subject"),
    [("nav_statres", "al03"), ("unknown_name", None)],
)
def test_get_secondary_subject(
    subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_secondary_subject: str,
) -> None:
    assert (
        subject_mapping.get_secondary_subject(statistic_short_name)
        == expected_secondary_subject
    )


def test_extract_titles():
    xml_string = '<titler><tittel sprak="no">Partifinansiering</tittel><tittel sprak="en">Funding of political parties</tittel></titler>'
    soup = BeautifulSoup(xml_string, features="xml")
    assert StatisticSubjectMapping._extract_titles(soup) == {  # noqa: SLF001
        "no": "Partifinansiering",
        "en": "Funding of political parties",
    }
