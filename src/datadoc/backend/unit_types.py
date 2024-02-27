from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from datadoc.enums import SupportedLanguages

from klass import KlassClassification  # type: ignore [attr-defined]

logger = logging.getLogger(__name__)


@dataclass
class UnitType:
    """Data structure for the a unit type."""

    titles: dict[str, str]
    unit_code: str

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
class UnitTypes:
    """Class for retrieving classifications from Klass."""

    def __init__(self, classification_id: int) -> None:
        """Retrieves a list of classifications given a classification id.

        Initializes the classifications list and starts fetching the classifications.
        """
        self._classifications: list[UnitType] = []

        self.classifications_dataframe = self._fetch_data_from_external_source(
            classification_id,
        )

        self._parse_classification_dataframe_if_loaded()

    def _fetch_data_from_external_source(
        self,
        classification_id: int,
    ) -> pd.DataFrame | None:
        """Fetches the classifications from Klass by classification id.

        returns a pandas dataframe with the class data for the given classification id.
        """
        try:
            klass_dataframe = KlassClassification(classification_id)
            return klass_dataframe.get_codes()
        except Exception:
            logger.exception(
                "Exception while getting classifications from Klass",
            )
            return None

    def _parse_classification_dataframe(
        self,
        classifications_dataframe: pd.DataFrame,
    ) -> list[str]:
        """Method that finds the name column in the dataframe, and returns all values in a list."""
        if "name" in classifications_dataframe.columns:
            return classifications_dataframe.loc[:, "name"].to_list()
        return []

    def _parse_classification_dataframe_if_loaded(self) -> bool:
        """Checks if the data from Klass is loaded, then gets the classifications from the dataframe."""
        if self.classifications_dataframe is not None:
            self._classifications = self._parse_classification_dataframe(
                self.classifications_dataframe,
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
    def classifications(self) -> list[str]:
        """Getter for primary subjects."""
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
