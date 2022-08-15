import logging
from typing import Dict, List, Optional

from datadoc_model import Model
from datadoc_model.Enums import SupportedLanguages
from datadoc_model.LanguageStringsEnum import LanguageStringsEnum

import datadoc.state as state

logger = logging.getLogger(__name__)


def update_global_language_state(language: SupportedLanguages):
    logger.debug(f"Updating language: {language.name}")
    state.current_metadata_language = language


def get_options_for_language(
    language: SupportedLanguages, enum: LanguageStringsEnum
) -> List[Dict[str, str]]:
    """Generate the list of options based on the currently chosen language"""
    return [
        {
            "label": i.get_value_for_language(language),
            "value": i.name,
        }
        for i in enum
    ]


def find_existing_language_string(
    metadata_model_object: "Model.DataDocBaseModel",
    value: str,
    metadata_identifier: str,
) -> Optional[Model.LanguageStrings]:
    # In this case we need to set the string to the correct language code
    language_strings = getattr(metadata_model_object, metadata_identifier)
    if language_strings is None:
        # This means that no strings have been saved yet so we need to construct
        # a new LanguageStrings object
        language_strings = Model.LanguageStrings(
            **{state.current_metadata_language.value: value}
        )
    else:
        # In this case there's an existing object so we save this string
        # to the current language
        setattr(language_strings, state.current_metadata_language.value, value)
    return language_strings
