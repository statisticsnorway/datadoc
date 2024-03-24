from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from datadoc.backend.external_sources.external_sources import GetExternalSource
from datadoc.enums import SupportedLanguages

if TYPE_CHECKING:
    import concurrent

    import pandas as pd

from klass.classes.classification import KlassClassification

logger = logging.getLogger(__name__)


@dataclass
class CodeListItem:
    """Data structure for a code list item."""

    titles: dict[str, str]
    code: str

    def get_title(self, language: SupportedLanguages) -> str:
        """Get the title in the given language."""
        try:
            return self.titles[language]
        except KeyError:
            try:
                return self.titles[
                    (
                        "nb"
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


class CodeList(GetExternalSource):
    """Class for retrieving classifications from Klass."""

    def __init__(
        self,
        executor: concurrent.futures.ThreadPoolExecutor,
        classification_id: int | None,
    ) -> None:
        """Retrieves a list of classifications given a classification id.

        Initializes the classifications list and starts fetching the classifications.
        """
        self.supported_languages = [
            SupportedLanguages.NORSK_BOKMÅL.value,
            SupportedLanguages.ENGLISH.value,
        ]
        self._classifications: list[CodeListItem] = []
        self.classification_id = classification_id
        self.classifications_dataframes: dict[str, pd.DataFrame] | None = None
        super().__init__(executor)

    def _fetch_data_from_external_source(
        self,
    ) -> dict[str, pd.DataFrame] | None:
        """Fetches the classifications from Klass by classification id.

        returns a pandas dataframe with the class data for the given classification id.
        """
        try:
            classifications_dataframes = {}
            for i in self.supported_languages:
                classifications_dataframes[i] = (
                    KlassClassification(
                        str(self.classification_id),
                        i,
                    )
                    .get_codes()
                    .data
                )
        except Exception:
            logger.exception(
                "Exception while getting classifications from Klass",
            )
            return None
        else:
            return classifications_dataframes

    def _extract_titles(
        self,
        dataframes: dict[SupportedLanguages, pd.DataFrame],
    ) -> list[dict[str, str]]:
        list_of_titles = []
        languages = list(dataframes)
        for i in range(len(dataframes[SupportedLanguages.NORSK_BOKMÅL])):
            titles = {}
            for j in languages:
                if "name" in dataframes[j]:
                    titles[str(j)] = dataframes[j].loc[:, "name"][i]
                else:
                    titles[str(j)] = None
            list_of_titles.append(titles)
        return list_of_titles

    def _create_code_list_from_dataframe(
        self,
        classifications_dataframes: dict[SupportedLanguages, pd.DataFrame],
    ) -> list[CodeListItem]:
        """Method that finds the name column in the dataframe, and returns all values in a list."""
        classification_names = self._extract_titles(classifications_dataframes)
        classification_codes: list
        if "code" in classifications_dataframes[SupportedLanguages.NORSK_BOKMÅL]:
            classification_codes = (
                classifications_dataframes[SupportedLanguages.NORSK_BOKMÅL]
                .loc[:, "code"]
                .to_list()
            )
        else:
            classification_codes = [None] * len(classification_names)
        unit_types = []
        for a, b in zip(classification_names, classification_codes):
            unit_types.append(
                CodeListItem(a, b),
            )
        return unit_types

    def _get_classification_dataframe_if_loaded(self) -> bool:
        """Checks if the data from Klass is loaded, then gets the classifications from the dataframe."""
        if not self._classifications:
            self.classifications_dataframes = self.retrieve_external_data()
            if self.classifications_dataframes is not None:
                self._classifications = self._create_code_list_from_dataframe(
                    self.classifications_dataframes,
                )
                logger.debug(
                    "Thread finished. found %s classifications",
                    len(self._classifications),
                )
                return True
            logger.warning(
                "Thread is not done. Cannot get classifications from the dataframe.",
            )
        return False

    @property
    def classifications(self) -> list[CodeListItem]:
        """Getter for primary subjects."""
        self._get_classification_dataframe_if_loaded()
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
