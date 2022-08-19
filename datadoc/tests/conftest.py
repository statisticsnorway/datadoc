import pytest
from datadoc_model.Enums import SupportedLanguages

from datadoc import state


@pytest.fixture()
def clear_state():
    state.metadata = None
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
