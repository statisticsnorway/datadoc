import functools
import pathlib

import pytest
from bs4 import BeautifulSoup
from bs4 import ResultSet

from datadoc.backend.statistic_subject_mapping import PrimarySubject
from datadoc.backend.statistic_subject_mapping import SecondarySubject
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from tests.utils import TEST_RESOURCES_DIRECTORY

SOURCE_URL = "https://www.ssb.no/xp/_/service/mimir/subjectStructurStatistics"


@pytest.fixture()
def _mock_fetch_statistical_structure(mocker, file_path: pathlib.Path) -> None:
    def fake_statistical_structure(file_path, _) -> ResultSet:
        with file_path.open() as f:
            return BeautifulSoup(f.read(), features="xml").find_all("hovedemne")

    mocker.patch(
        "datadoc.backend.statistic_subject_mapping.StatisticSubjectMapping._fetch_statistical_structure",
        functools.partial(fake_statistical_structure, file_path),
    )


@pytest.fixture()
def subject_mapping() -> StatisticSubjectMapping:
    return StatisticSubjectMapping(SOURCE_URL)


@pytest.fixture()
def file_path() -> pathlib.Path:
    return pathlib.Path(
        "tests/resources/statistical_subject_structure/extract_secondary_subject.xml",
    )


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_primary_subject"),
    [("nav_statres", "al"), ("unknown_name", None)],
)
def test_get_primary_subject(
    subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_primary_subject: str,
) -> None:
    subject_mapping.wait_for_primary_subject()
    assert (
        subject_mapping.get_primary_subject(statistic_short_name)
        == expected_primary_subject
    )


def test_extract_titles():
    xml_string = '<titler><tittel sprak="no">Partifinansiering</tittel><tittel sprak="en">Funding of political parties</tittel></titler>'
    soup = BeautifulSoup(xml_string, features="xml")
    assert StatisticSubjectMapping._extract_titles(soup) == {  # noqa: SLF001
        "no": "Partifinansiering",
        "en": "Funding of political parties",
    }


STATISTICAL_SUBJECT_STRUCTURE_DIR = "statistical_subject_structure"


@pytest.mark.parametrize(
    ("file_path", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / STATISTICAL_SUBJECT_STRUCTURE_DIR / "simple.xml",
            [
                PrimarySubject(
                    titles={"en": "aa english", "no": "aa norwegian"},
                    subject_code="aa",
                    secondary_subjects=[
                        SecondarySubject(
                            titles={"en": "aa00 english", "no": "aa00 norwegian"},
                            subject_code="aa00",
                            statistic_short_names=["aa_kortnvan"],
                        ),
                    ],
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / STATISTICAL_SUBJECT_STRUCTURE_DIR / "empty.xml",
            [],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_statistical_structure")
def test_read_in_statistical_structure(
    subject_mapping: StatisticSubjectMapping,
    expected: list[PrimarySubject],
) -> None:
    subject_mapping.wait_for_primary_subject()
    assert subject_mapping.primary_subjects == expected


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_secondary_subject"),
    [
        ("ab_kortnvan", "ab00"),
        ("aa_kortnvan", "aa00"),
        ("ab_kortnvan_01", "ab01"),
        ("aa_kortnvan_01", "aa01"),
        ("unknown_name", None),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_statistical_structure")
def test_get_secondary_subject(
    subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_secondary_subject: str,
) -> None:
    subject_mapping.wait_for_primary_subject()
    assert (
        subject_mapping.get_secondary_subject(statistic_short_name)
        == expected_secondary_subject
    )
