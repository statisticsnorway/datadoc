from __future__ import annotations

import concurrent.futures
import logging
from abc import ABC
from abc import abstractmethod

import requests

logger = logging.getLogger(__name__)


class GetExternalSource(ABC):
    """Abstract base class for getting data from external sources."""

    def __init__(self, source_url: str | None) -> None:
        """Retrieves data from an external source asynchronusly.

        Initilizes the future object.
        """
        self.future: concurrent.futures.Future[None] | None = None

        self.source_url = source_url

        if self.source_url:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self.future = executor.submit(
                self._fetch_external_source,
                self.source_url,
            )
            logger.debug("Thread started to fetch external resource.")
        else:
            logger.warning(
                "No URL to fetch external resource supplied. Skipping fetching it. This may make it difficult to provide a value for the 'subject_field' metadata field.",
            )

    def _fetch_external_source(self, source_url: str) -> None:
        try:
            return requests.get(source_url, timeout=30)
        except requests.exceptions.RequestException:
            logger.exception(
                "Exception while fetching statistical structure ",
            )
            return None

    def wait_external_result(self) -> None:
        """Waits for the thread responsible for loading the xml to finish."""
        if not self.future:
            logger.warning("No future to wait for.")
            # Nothing to wait for in this case, just return immediately
            return
        self.future.result()

    @abstractmethod
    def map_data_from_external_source(self):
        """Abstract method implemented in the child class to handle the external data."""
