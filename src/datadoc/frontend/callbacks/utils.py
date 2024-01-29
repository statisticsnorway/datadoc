"""Functions which aren't directly called from a decorated callback."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import TypeAlias

from datadoc_model import model

from datadoc import config
from datadoc import enums
from datadoc import state
from datadoc.backend.datadoc_metadata import METADATA_DOCUMENT_FILE_SUFFIX
from datadoc.backend.datadoc_metadata import DataDocMetadata

if TYPE_CHECKING:
    from enum import Enum
    from pathlib import Path

    import pydantic

    from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)


MetadataInputTypes: TypeAlias = str | list[str] | int | float | bool | None


def update_global_language_state(language: SupportedLanguages) -> None:
    """Update global language state."""
    logger.debug("Updating language: %s", language.name)
    state.current_metadata_language = language


def get_language_strings_enum(enum: Enum) -> enums.LanguageStringsEnum:
    """Get the correct language strings enum for the given enum.

    We need multiple languages to display in the front end, but the model only defines a single language in the enums.
    """
    language_strings_enum: enums.LanguageStringsEnum = getattr(enums, enum.__name__)  # type: ignore [attr-defined]
    if not issubclass(language_strings_enum, enums.LanguageStringsEnum):  # type: ignore [arg-type]
        message = f"Expected {language_strings_enum} to be a subclass of LanguageStringsEnum, but is {type(language_strings_enum)}"
        raise TypeError(
            message,
        )
    return language_strings_enum


def get_options_for_language(
    language: SupportedLanguages,
    enum: Enum,
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    return [
        {
            "label": i.get_value_for_language(language),
            "value": i.name,
        }
        for i in get_language_strings_enum(enum)  # type: ignore [attr-defined]
    ]


def find_existing_language_string(
    metadata_model_object: pydantic.BaseModel,
    value: str,
    metadata_identifier: str,
) -> model.LanguageStringType:
    """Get or create a LanguageStrings object and return it."""
    # In this case we need to set the string to the correct language code
    language_strings = getattr(metadata_model_object, metadata_identifier)
    if language_strings is None:
        # This means that no strings have been saved yet so we need to construct
        # a new LanguageStrings object
        language_strings = model.LanguageStringType(
            **{state.current_metadata_language.value: value},
        )
    else:
        # In this case there's an existing object so we save this string
        # to the current language
        setattr(language_strings, state.current_metadata_language.value, value)
    return language_strings


def get_dataset_path() -> str | Path | None:
    """Extract the path to the dataset from the potential sources."""
    if state.metadata.dataset is not None:
        return state.metadata.dataset
    path_from_env = config.get_datadoc_dataset_path()
    logger.info(
        "Dataset path from env var: '%s'",
        path_from_env,
    )
    return path_from_env


def open_file(file_path: str | Path | None = None) -> DataDocMetadata:
    """Load the given dataset into a DataDocMetadata instance."""
    if file_path and str(file_path).endswith(METADATA_DOCUMENT_FILE_SUFFIX):
        logger.info("Opening existing metadata document %s", file_path)
        return DataDocMetadata(metadata_document_path=file_path)

    dataset = file_path or get_dataset_path()
    logger.info("Opening dataset %s", dataset)
    return DataDocMetadata(dataset_path=dataset)
