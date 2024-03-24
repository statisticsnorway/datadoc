from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import bs4
import requests
from bs4 import BeautifulSoup
from bs4 import ResultSet

from datadoc.backend.external_sources.external_sources import GetExternalSource
from datadoc.enums import SupportedLanguages

if TYPE_CHECKING:
    import concurrent

logger = logging.getLogger(__name__)


@dataclass
class Subject:
    """Base class for Primary and Secondary subjects."""

    titles: dict[str, str]
    subject_code: str

    def get_title(self, language: SupportedLanguages) -> str:
        """Get the title in the given language."""
        try:
            return self.titles[
                (
                    # Adjust to language codes in the StatisticSubjectMapping structure.
                    "no"
                    if language
                    in [
                        SupportedLanguages.NORSK_BOKMÅL,
                        SupportedLanguages.NORSK_NYNORSK,
                    ]
                    else "en"
                )
            ]
        except KeyError:
            logger.exception(
                "Could not find title for subject %s  and language: %s",
                self,
                language.name,
            )
            return ""


@dataclass
class SecondarySubject(Subject):
    """Data structure for secondary subjects or 'delemne'."""

    statistic_short_names: list[str]


@dataclass
class PrimarySubject(Subject):
    """Data structure for primary subjects or 'hovedemne'."""

    secondary_subjects: list[SecondarySubject]


class StatisticSubjectMapping(GetExternalSource):
    """Allow mapping between statistic short name and primary and secondary subject."""

    def __init__(
        self,
        executor: concurrent.futures.ThreadPoolExecutor,
        source_url: str | None,
    ) -> None:
        """Retrieves the statistical structure document from the given URL.

        Initializes the mapping dicts. Based on the values in the statistical structure document.
        """
        self.source_url = source_url

        self._statistic_subject_structure_xml: ResultSet | None = None

        self._primary_subjects: list[PrimarySubject] = []

        super().__init__(executor)

    def get_secondary_subject(self, statistic_short_name: str | None) -> str | None:
        """Looks up the secondary subject for the given statistic short name in the mapping dict.

        Returns the secondary subject string if found, else None.
        """
        for p in self.primary_subjects:
            for s in p.secondary_subjects:
                if statistic_short_name in s.statistic_short_names:
                    logger.debug("Got %s from %s", s, statistic_short_name)
                    return s.subject_code

        logger.debug("No secondary subject found for %s", statistic_short_name)
        return None

    @staticmethod
    def _extract_titles(titles_xml: bs4.element.Tag) -> dict[str, str]:
        titles = {}
        for title in titles_xml.find_all("tittel"):
            titles[title["sprak"]] = title.text
        return titles

    def _fetch_data_from_external_source(self) -> ResultSet | None:
        """Fetch statistical structure document from source_url.

        Returns a BeautifulSoup ResultSet.
        """
        try:
            url = str(self.source_url)
            response = requests.get(url, timeout=30)
            response.encoding = "utf-8"
            logger.debug("Got response %s from %s", response, url)
            soup = BeautifulSoup(response.text, features="xml")
            return soup.find_all("hovedemne")
        except requests.exceptions.RequestException:
            logger.exception(
                "Exception while fetching statistical structure ",
            )
            return None

    def _parse_statistic_subject_structure_xml(
        self,
        statistical_structure_xml: ResultSet,
    ) -> list[PrimarySubject]:
        primary_subjects: list[PrimarySubject] = []
        for p in statistical_structure_xml:
            secondary_subjects: list[SecondarySubject] = [
                SecondarySubject(
                    self._extract_titles(s.titler),
                    s["emnekode"],
                    [statistikk["kortnavn"] for statistikk in s.find_all("Statistikk")],
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

    @property
    def primary_subjects(self) -> list[PrimarySubject]:
        """Getter for primary subjects."""
        if not self._primary_subjects:
            self._parse_xml_if_loaded()
            logger.debug("Got %s primary subjects", len(self._primary_subjects))
        return self._primary_subjects

    def _parse_xml_if_loaded(self) -> bool:
        """Checks if the xml is loaded, then parses the xml if it is loaded.

        Returns true if it is loaded and parsed.
        """
        if self.check_if_external_data_is_loaded():
            self._statistic_subject_structure_xml = self.retrieve_external_data()

            if self._statistic_subject_structure_xml is not None:
                self._primary_subjects = self._parse_statistic_subject_structure_xml(
                    self._statistic_subject_structure_xml,
                )
                logger.debug(
                    "Thread finished. Parsed %s primary subjects",
                    len(self._primary_subjects),
                )
                return True
            logger.warning("Thread is not done. Cannot parse xml.")
        return False
