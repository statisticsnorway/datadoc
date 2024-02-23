from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

from klass import KlassClassification

logger = logging.getLogger(__name__)


class UnitTypes:
    """Allow mapping between statistic short name and primary and secondary subject."""

    def __init__(self, classification_id: int) -> None:
        """Retrieves the statistical structure document from the given URL.

        Initializes the mapping dicts. Based on the values in the statistical structure document.
        """
        self._classifications: list[str] = []

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
            nus = KlassClassification(classification_id)
            return nus.get_codes()
        except Exception:
            logger.exception(
                "Exception while getting classifications from klass",
            )
            return None

    def _parse_classification_dataframe(
        self,
        classifications_dataframe: pd.DataFrame,
    ) -> list[str]:
        """Method that finds the name column in the dataframe, and returns all values in a list."""
        return classifications_dataframe.loc[:, "name"].tolist()

    def _parse_classification_dataframe_if_loaded(self) -> bool:
        """Checks if the data from klass is loaded, then gets the classifications from the dataframe."""
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
    def classifications(self) -> list[classifications]:
        """Getter for primary subjects."""
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
