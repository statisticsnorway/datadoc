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
    """Data structure for a code list item.

    Attributes:
        titles: A dictionary mapping language codes to titles.
        code: The code associated with the item.
    """

    titles: dict[str, str]
    code: str

    def get_title(self, language: SupportedLanguages) -> str:
        """Gets the title in the given language.

        Args:
            language: The language code for which to get the title.

        Returns:
            The title in the specified language. If the title is not available in the specified language.
            It defaults to Norwegian Bokmål ("nb") or English ("en").
        """
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
    """Class for retrieving classifications from Klass.

    This class fetches a list of classifications given a classification ID
    and supports multiple languages.
    """

    def __init__(
        self,
        executor: concurrent.futures.ThreadPoolExecutor,
        classification_id: int | None,
    ) -> None:
        """Initializes the CodeList with the given classification ID and executor.

        Args:
            executor: An instance of ThreadPoolExecutor to manage the asynchronous execution of data fetching.
            classification_id: The ID of the classification to retrieve.
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
        """Fetches the classifications from Klass by classification ID.

        Returns:
            A dictionary mapping language codes to pandas DataFrames containing the classification
            data for the given classification ID.
        """
        classifications_dataframes = {}
        for i in self.supported_languages:
            try:
                classifications_dataframes[i] = (
                    KlassClassification(
                        str(self.classification_id),
                        i,
                    )
                    .get_codes()
                    .data
                )
            except Exception:  # noqa: PERF203
                logger.exception(
                    "Exception while getting classifications from Klass",
                )
                return None
            else:
                return classifications_dataframes
        return None

    def _extract_titles(
        self,
        dataframes: dict[SupportedLanguages, pd.DataFrame],
    ) -> list[dict[str, str]]:
        """Extracts titles from the dataframes for each supported language.

        Args:
            dataframes: A dictionary mapping language codes to pandas DataFrames containing classification data.

        Returns:
            A list of dictionaries mapping language codes to titles.
        """
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
        """Method that finds the name column in the dataframe, and returns all values in a list.

        Args:
            classifications_dataframes: A dictionary mapping language codes to pandas DataFrames containing classification data.

        Returns:
            A list of CodeListItem objects.
        """
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
        classification_items = []
        for a, b in zip(classification_names, classification_codes):
            classification_items.append(
                CodeListItem(a, b),
            )
        return classification_items

    def _get_classification_dataframe_if_loaded(self) -> bool:
        """Checks if the data from Klass is loaded, then gets the classifications from the dataframe.

        Returns:
            True if the data is loaded and classifications are extracted, False otherwise.
        """
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
        """Gets the list of classifications.

        Returns:
            A list of CodeListItem objects.
        """
        self._get_classification_dataframe_if_loaded()
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
