from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.Enums import SupportedLanguages

# DANGER: This global is safe when Datadoc is run as designed, with
# an individual instance per user run within a Jupyter Notebook.
#
# If Datadoc is redeployed as a multi-user web app then this storage
# strategy must be modified, since users will modify each others data.
# See here: https://dash.plotly.com/sharing-data-between-callbacks

# Global metadata container
metadata: DataDocMetadata

CURRENT_METADATA_LANGUAGE: SupportedLanguages = SupportedLanguages.NORSK_BOKMÅL
