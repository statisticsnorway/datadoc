from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc.backend.external_sources.external_sources import GetExternalSource

if TYPE_CHECKING:
    import pandas as pd

from klass import KlassClassification  # type: ignore [attr-defined]

logger = logging.getLogger(__name__)


class UnitTypes(GetExternalSource):
    """Class for retrieving classifications from Klass."""

    def __init__(self, classification_id: int) -> None:
        """Retrieves a list of classifications given a classification id.

        Initializes the classifications list and starts fetching the classifications.
        """
        self._classifications: list[str] = []

        self.classification_id = classification_id

        self.classifications_dataframe: pd.DataFrame | None = None

        super().__init__()

    def _fetch_data_from_external_source(
        self,
    ) -> pd.DataFrame | None:
        """Fetches the classifications from Klass by classification id.

        returns a pandas dataframe with the class data for the given classification id.
        """
        try:
            klass_dataframe = KlassClassification(self.classification_id)
            return klass_dataframe.get_codes()
        except Exception:
            logger.exception(
                "Exception while getting classifications from Klass",
            )
            return None

    def _extract_unit_types_from_dataframe(
        self,
        classifications_dataframe: pd.DataFrame,
    ) -> list[str]:
        """Method that finds the name column in the dataframe, and returns all values in a list."""
        if "name" in classifications_dataframe.columns:
            return classifications_dataframe.loc[:, "name"].to_list()
        return []

    def _get_classification_dataframe_if_loaded(self) -> bool:
        """Checks if the data from Klass is loaded, then gets the classifications from the dataframe."""
        if self.check_if_external_data_is_loaded():
            self.classifications_dataframe = self.retrieve_external_data()
            if self.classifications_dataframe is not None:
                self._classifications = self._extract_unit_types_from_dataframe(
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
        self._get_classification_dataframe_if_loaded()
        logger.debug("Got %s classifications subjects", len(self._classifications))
        return self._classifications
