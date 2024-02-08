"""Global state.

DANGER: This global is safe when Datadoc is run as designed, with
an individual instance per user run within a Jupyter Notebook.

If Datadoc is redeployed as a multi-user web app then this storage
strategy must be modified, since users will modify each others data.
See here: https://dash.plotly.com/sharing-data-between-callbacks
"""

from __future__ import annotations

import logging
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata
    from datadoc.enums import SupportedLanguages


# Global metadata container
metadata: DataDocMetadata

current_metadata_language: SupportedLanguages

SOURCE_URL = "https://www.ssb.no/xp/_/service/mimir/subjectStructurStatistics"


def get_intatiate_statistic_subjec_mapping(source_url: str) -> StatisticSubjectMapping:
    """Threaded function to handle a non blocking initialization of StatisticSubjectMapping."""
    return StatisticSubjectMapping(source_url)


def when_thread_is_finished(future: Future) -> StatisticSubjectMapping:
    """This funcion function is attached to the Future object in the thread pool. The function called whenever the Future object is finished executed."""
    return future.result()


executor = ThreadPoolExecutor(max_workers=1)
future = executor.submit(get_intatiate_statistic_subjec_mapping, SOURCE_URL)
statistic_subjec_mapping = future.add_done_callback(when_thread_is_finished)


statistic_subjec_mapping: StatisticSubjectMapping
