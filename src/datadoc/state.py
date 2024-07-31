"""Global state.

DANGER: This global is safe when Datadoc is run as designed, with
an individual instance per user run within a Jupyter Notebook.

If Datadoc is redeployed as a multi-user web app then this storage
strategy must be modified, since users will modify each others data.
See here: https://dash.plotly.com/sharing-data-between-callbacks
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datadoc.backend.src.code_list import CodeList
    from datadoc.backend.src.core import Datadoc
    from datadoc.backend.src.statistic_subject_mapping import StatisticSubjectMapping


# Global metadata container
metadata: Datadoc

statistic_subject_mapping: StatisticSubjectMapping

unit_types: CodeList

organisational_units: CodeList

data_sources: CodeList

measurement_units: CodeList
