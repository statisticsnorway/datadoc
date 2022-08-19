from typing import TYPE_CHECKING

from datadoc_model.Enums import SupportedLanguages

if TYPE_CHECKING:
    # This is only needed for a type hint so we put the import inside
    # this check to avoid circular imports
    from datadoc.backend.DataDocMetadata import DataDocMetadata

# DANGER: This global is safe when Datadoc is run as designed, with
# an individual instance per user run within a Jupyter Notebook.
#
# If Datadoc is redeployed as a multi-user web app then this storage
# strategy must be modified, since users will modify each others data.
# See here: https://dash.plotly.com/sharing-data-between-callbacks

# Global metadata container
metadata: "DataDocMetadata"

current_metadata_language: SupportedLanguages = SupportedLanguages.NORSK_BOKMÅL
