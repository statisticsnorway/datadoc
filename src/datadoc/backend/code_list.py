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
        """Return the title in the specified language.

        Args:
            language: The language code for which to get the title.

        Returns:
            The title in the specified language. It returns the title in Norwegian
            Bokmål ("nb") if the language is either Norwegian Bokmål or Norwegian
            Nynorsk, otherwise it returns the title in English ("en"). If none of
            these are available, it returns an empty string and logs an exception.
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

    This class fetches a classification given a classification ID
    and supports multiple languages.

    Attributes:
        supported_languages: A list of supported language codes.
        _classifications: A list to store classification items.
        classification_id: The ID of the classification to retrieve.
        classifications_dataframes: A dictionary to store dataframes of
            classifications.
    """

    def __init__(
        self,
        executor: concurrent.futures.ThreadPoolExecutor,
        classification_id: int | None,
    ) -> None:
        """Initialize the CodeList with the given classification ID and executor.

        Args:
            executor: An instance of ThreadPoolExecutor to manage the asynchronous
                execution of data fetching.
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
        """Fetch the classifications from Klass by classification ID.

        This method retrieves classification data for each supported language and
        stores it in a dictionary where the keys are language codes and the values
        are pandas DataFrames containing the classification data.

        Returns:
            A dictionary mapping language codes to pandas DataFrames containing the
            classification data for the given classification ID.
            If an exception occurs during the fetching process, logs the exception
            and returns None.
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
        """Extract titles from the dataframes for each supported language.

        This method processes the provided dataframes and extracts the title from
        each row for all supported languages, creating a list of dictionaries where
        each dictionary maps language codes to titles.

        Args:
            dataframes: A dictionary mapping language codes to pandas DataFrames
                containing classification data.

        Returns:
            A list of dictionaries, each mapping language codes to titles.
            If a title is not available in a dataframe, the corresponding dictionary
            value will be None.
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
        """Create a list of CodeListItem objects from the classification dataframes.

        This method extracts titles from the provided dataframes and pairs them
        with their corresponding classification codes to create a list of
        CodeListItem objects.

        Args:
            classifications_dataframes: A dictionary mapping language codes to
                pandas DataFrames containing classification data.

        Returns:
            A list of CodeListItem objects containing classification titles
            and codes.
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
        """Check if the classification data from Klass is loaded.

        This method verifies whether the classification data has been loaded.
        If not, it retrieves the data from an external source and populates the
        classifications. It logs the process and returns a boolean indicating the
        success of the operation.

        Returns:
            True if the data is loaded and classifications are successfully extracted,
            False otherwise.
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
        """Get the list of classifications.

        Returns:
            A list of CodeListItem objects.
        """
        self._get_classification_dataframe_if_loaded()
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
