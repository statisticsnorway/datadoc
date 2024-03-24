from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    import concurrent.futures

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GetExternalSource(ABC, Generic[T]):
    """Abstract base class for getting data from external sources."""

    def __init__(self, executor: concurrent.futures.ThreadPoolExecutor) -> None:
        """Retrieves data from an external source asynchronously.

        Initializes the future object.
        """
        self.future = executor.submit(
            self._fetch_data_from_external_source,
        )

    def wait_for_external_result(self) -> None:
        """Waits for the thread responsible for loading the external request to finish."""
        if not self.future:
            logger.warning("No future to wait for.")
            # Nothing to wait for in this case, just return immediately
            return
        self.future.result()

    def check_if_external_data_is_loaded(self) -> bool:
        """Method to check if the thread getting the external data has finished running."""
        if self.future:
            return self.future.done()
        return False

    def retrieve_external_data(self) -> T | None:
        """Method that returns the result of the thread."""
        if self.future:
            return self.future.result()
        return None

    @abstractmethod
    def _fetch_data_from_external_source(self) -> T | None:
        """Abstract method implemented in the child class to handle the external data."""
        raise NotImplementedError
