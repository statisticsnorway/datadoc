from __future__ import annotations

import concurrent.futures
import logging
from abc import ABC
from abc import abstractmethod

from requests import Request

logger = logging.getLogger(__name__)


class GetExternalSource(ABC):
    """Abstract base class for getting data from external sources."""

    def __init__(self, source_url: str | None) -> None:
        """Retrieves data from an external source asynchronusly.

        Initilizes the future object.
        """
        self.future: concurrent.futures.Future[None] | None = None

        if source_url:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self.future = executor.submit(
                self._fetch_data_from_external_source,
                source_url,
            )
            logger.debug("Thread started to fetch external resource.")
        else:
            logger.warning(
                "No URL to fetch external resource supplied. Skipping fetching it. This may make it difficult to provide a value for the 'subject_field' metadata field.",
            )

    def wait_external_result(self) -> None:
        """Waits for the thread responsible for loading the external request to finish."""
        if not self.future:
            logger.warning("No future to wait for.")
            # Nothing to wait for in this case, just return immediately
            return
        self.future.result()

    def check_if_external_data_is_loaded(self) -> bool:
        """Method to check if the thread getting the extarnal data has finished running."""
        if self.future:
            return self.future.done()
        return False

    def get_external_data(self) -> Request:
        """Method that returns the result of the thread."""
        return self.future.result()

    @abstractmethod
    def _fetch_data_from_external_source(self) -> None:
        """Abstract method implemented in the child class to handle the external data."""
