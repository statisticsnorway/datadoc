"""Global state.

DANGER: This global is safe when Datadoc is run as designed, with
an individual instance per user run within a Jupyter Notebook.

If Datadoc is redeployed as a multi-user web app then this storage
strategy must be modified, since users will modify each others data.
See here: https://dash.plotly.com/sharing-data-between-callbacks
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc import config
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping

if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata
    from datadoc.enums import SupportedLanguages


logger = logging.getLogger(__name__)

# Global metadata container
metadata: DataDocMetadata

current_metadata_language: SupportedLanguages

statistic_subject_mapping: StatisticSubjectMapping

if source_url := config.get_statistical_subject_source_url():
    statistic_subject_mapping = StatisticSubjectMapping(
        source_url,
    )
else:
    logger.warning(
        "No URL to fetch statistical subject structure supplied. Skipping fetching it. This may make it difficult to provide a value for the 'subject_field' metadata field.",
    )
