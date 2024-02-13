from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass

import bs4
import requests
from bs4 import BeautifulSoup
from bs4 import ResultSet

logger = logging.getLogger(__name__)


@dataclass
class SecondarySubject:
    """Data structure for secondary subjects or 'delemne'."""

    titles: dict[str, str]
    subject_code: str
    statistic_short_names: list[str]


@dataclass
class PrimarySubject:
    """Data structure for primary subjects or 'hovedemne'."""

    titles: dict[str, str]
    subject_code: str
    secondary_subjects: list[SecondarySubject]


class StatisticSubjectMapping:
    """Allow mapping between statistic short name and primary and secondary subject."""

    def __init__(self, source_url: str | None) -> None:
        """Retrieves the statistical structure document from the given URL.

        Initializes the mapping dicts. Based on the values in the statistical structure document.
        """
        self.source_url = source_url

        self._statistic_subject_structure_xml: ResultSet | None = None
        self.secondary_subject_primary_subject_mapping: dict[str, str] = {}

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.future = executor.submit(
            self._fetch_statistical_structure,
            self.source_url,
        )

        self._primary_subjects: list[PrimarySubject] | None

    def get_primary_subject(self, statistic_short_name: str) -> str | None:
        """Returns the primary subject for the given statistic short name by mapping it through the secondary subject.

        Looks up the secondary subject for the statistic short name, then uses that
        to look up the corresponding primary subject in the mapping dict.

        Returns the primary subject string if found, else None.
        """
        self._parse_xml_if_loaded()
        if secondary_subject := self.get_secondary_subject(statistic_short_name):
            return self.secondary_subject_primary_subject_mapping.get(
                secondary_subject,
                None,
            )

        return None

    def get_secondary_subject(self, statistic_short_name: str) -> str | None:
        """Looks up the secondary subject for the given statistic short name in the mapping dict.

        Returns the secondary subject string if found, else None.
        """
        if self.primary_subjects is not None:
            for p in self.primary_subjects:
                for s in p.secondary_subjects:
                    if statistic_short_name in s.statistic_short_names:
                        return s.subject_code
        return None

    @staticmethod
    def _extract_titles(titles_xml: bs4.element.Tag) -> dict[str, str]:
        titles = {}
        for title in titles_xml.find_all("tittel"):
            titles[title["sprak"]] = title.text
        return titles

    @staticmethod
    def _fetch_statistical_structure(source_url: str | None) -> ResultSet | None:
        """Fetch statistical structure document from source_url.

        Returns a BeautifulSoup ResultSet.
        """
        if source_url is not None:
            try:
                response = requests.get(source_url, timeout=30)
                soup = BeautifulSoup(response.text, features="xml")
                return soup.find_all("hovedemne")
            except requests.exceptions.RequestException:
                logger.debug("statistical structure file not avalable")
                return None
        return None

    def _parse_statistic_subject_structure_xml(
        self,
        statistical_structure_xml: ResultSet | None,
    ) -> list[PrimarySubject] | None:
        primary_subjects: list[PrimarySubject] = []
        if statistical_structure_xml is not None:
            for p in statistical_structure_xml:
                secondary_subjects: list[SecondarySubject] = [
                    SecondarySubject(
                        self._extract_titles(s.titler),
                        s["emnekode"],
                        [
                            statistikk["kortnavn"]
                            for statistikk in s.find_all("Statistikk")
                        ],
                    )
                    for s in p.find_all("delemne")
                ]

                primary_subjects.append(
                    PrimarySubject(
                        self._extract_titles(p.titler),
                        p["emnekode"],
                        secondary_subjects,
                    ),
                )
            return primary_subjects
        return None

    def wait_for_primary_subject(self) -> None:
        """Waits for the thread responsible for loading the xml to finish."""
        self.future.result()

    @property
    def primary_subjects(self) -> list[PrimarySubject] | None:
        """Getter for primary subjects."""
        self._parse_xml_if_loaded()
        return self._primary_subjects

    def _parse_xml_if_loaded(self) -> bool:
        """Checks if the xml is loaded, then parses the xml if it is loaded.

        Returns true if it is loaded and parsed.
        """
        if self.future.done():
            self._statistic_subject_structure_xml = self.future.result()

            self._primary_subjects = self._parse_statistic_subject_structure_xml(
                self._statistic_subject_structure_xml,
            )

            return True
        return False
