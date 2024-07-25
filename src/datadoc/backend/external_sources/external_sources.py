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
    """Abstract base class for retrieving data from external sources asynchronously.

    This class provides methods to initiate an asynchronous data retrieval
    operation, check its status, and retrieve the result once the operation
    completes. Subclasses must implement the `_fetch_data_from_external_source`
    method to define how data is fetched from the specific external source.
    """

    def __init__(self, executor: concurrent.futures.ThreadPoolExecutor) -> None:
        """Initialize the GetExternalSource with an executor to manage asynchronous tasks.

        This constructor initializes a future object that will hold the result of the
        asynchronous data fetching operation from an external source.

        Args:
            executor: An instance of ThreadPoolExecutor to manage the asynchronous
                execution of data fetching.
        """
        self.future = executor.submit(
            self._fetch_data_from_external_source,
        )

    def wait_for_external_result(self) -> None:
        """Wait for the thread responsible for loading the external request to finish.

        If there is no future to wait for, it logs a warning and returns immediately.
        """
        if not self.future:
            logger.warning("No future to wait for.")
            return
        self.future.result()

    def check_if_external_data_is_loaded(self) -> bool:
        """Check if the thread getting the external data has finished running.

        Returns:
            True if the data fetching operation is complete, False otherwise.
        """
        if self.future:
            return self.future.done()
        return False

    def retrieve_external_data(self) -> T | None:
        """Retrieve the result of the data fetching operation.

        This method checks if the asynchronous data fetching operation has
        completed. If the operation is finished, it returns the result.
        Otherwise, it returns None.

        Returns:
            The result of the data fetching operation if it is complete or None
            if the operation has not yet finished.
        """
        if self.future:
            return self.future.result()
        return None

    @abstractmethod
    def _fetch_data_from_external_source(self) -> T | None:
        """Handle external data retrieval.

        Abstract method to be implemented in the subclass.
        This method should define the logic for retrieving data from the specific
        external source.

        Returns:
            The data retrieved from the external source.
        """
        raise NotImplementedError
