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
    from datadoc.backend.datadoc_metadata import DataDocMetadata
    from datadoc.enums import SupportedLanguages


# Global metadata container
metadata: DataDocMetadata

current_metadata_language: SupportedLanguages
