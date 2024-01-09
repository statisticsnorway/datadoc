"""Callbacks relating to datasets."""

from __future__ import annotations

import logging
import os
import traceback
import typing as t

from pydantic import ValidationError

from datadoc import state
from datadoc.backend.datadoc_metadata import (
    METADATA_DOCUMENT_FILE_SUFFIX,
    DataDocMetadata,
)
from datadoc.frontend.callbacks.utils import (
    MetadataInputTypes,
    find_existing_language_string,
    get_options_for_language,
    update_global_language_state,
)
from datadoc.frontend.fields.display_dataset import (
    DISPLAYED_DATASET_METADATA,
    DISPLAYED_DROPDOWN_DATASET_ENUMS,
    MULTIPLE_LANGUAGE_DATASET_METADATA,
    DatasetIdentifiers,
)

if t.TYPE_CHECKING:
    from pathlib import Path

    from datadoc_model import model

    from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)

DATADOC_DATASET_PATH_ENV_VAR = "DATADOC_DATASET_PATH"


def get_dataset_path() -> str | Path | None:
    """Extract the path to the dataset from the potential sources."""
    if state.metadata.dataset is not None:
        return state.metadata.dataset
    path_from_env = os.getenv(DATADOC_DATASET_PATH_ENV_VAR)
    logger.info(
        "Dataset path from %s: '%s'",
        DATADOC_DATASET_PATH_ENV_VAR,
        path_from_env,
    )
    return path_from_env


def open_file(file_path: str | Path | None = None) -> None:
    """Load the given dataset into an DataDocMetadata instance."""
    if file_path and file_path.endswith(METADATA_DOCUMENT_FILE_SUFFIX):
        state.metadata = DataDocMetadata(metadata_document_path=file_path)
        logger.info("Opened existing metadata document %s", file_path)
    else:
        dataset = file_path or get_dataset_path()
        state.metadata = DataDocMetadata(dataset_path=dataset)
        logger.info("Opened dataset %s", dataset)


def open_dataset_handling(
    n_clicks: int,
    file_path: str,
) -> tuple[bool, bool, str, SupportedLanguages]:
    """Handle errors and other logic around opening a dataset file."""
    try:
        open_file(file_path)
    except FileNotFoundError:
        return (
            False,
            True,
            f"Filen '{file_path}' finnes ikke.",
            state.current_metadata_language.value,
        )
    except Exception as e:  # noqa: BLE001
        return (
            False,
            True,
            "\n".join(traceback.format_exception_only(type(e), e)),
            state.current_metadata_language.value,
        )
    if n_clicks and n_clicks > 0:
        return True, False, "", state.current_metadata_language.value

    return False, False, "", state.current_metadata_language.value


def process_keyword(value: str) -> list[str] | None:
    """Convert a comma separated string to a list of strings.

    e.g. 'a,b ,c' -> ['a', 'b', 'c']
    """
    if value is None:
        return None
    return [item.strip() for item in value.split(",")]


def process_special_cases(
    value: str,
    metadata_identifier: str,
) -> list[str] | model.LanguageStringType | None:
    """Pre-process metadata where needed.

    Some types of metadata need processing before being saved
    to the model. Handle these cases here, other values are
    returned unchanged.
    """
    if metadata_identifier == DatasetIdentifiers.KEYWORD.value:
        value = process_keyword(value)
    if metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA:
        value = find_existing_language_string(
            state.metadata.meta.dataset,
            value,
            metadata_identifier,
        )

    # Other values get returned unchanged
    return value


def accept_dataset_metadata_input(
    value: MetadataInputTypes,
    metadata_identifier: str,
) -> tuple[bool, str]:
    """Handle user inputs of dataset metadata values."""
    logger.debug(
        "Received updated value = %s for metadata_identifier = %s",
        value,
        metadata_identifier,
    )
    try:
        value = process_special_cases(value, metadata_identifier)
        # Update the value in the model
        setattr(
            state.metadata.meta.dataset,
            metadata_identifier,
            value,
        )
    except ValidationError as e:
        show_error = True
        error_explanation = f"`{e}`"
        logger.debug("Caught ValidationError:", exc_info=True)
    else:
        show_error = False
        error_explanation = ""
        logger.debug(
            "Successfully updated value = %s for metadata_identifier = %s",
            value,
            metadata_identifier,
        )

    return show_error, error_explanation


def update_dataset_metadata_language() -> list[MetadataInputTypes]:
    """Return new values for ALL the dataset metadata inputs.

    This allows editing of strings in the chosen language.
    """
    return [
        m.value_getter(state.metadata.meta.dataset, m.identifier)
        for m in DISPLAYED_DATASET_METADATA
    ]


def change_language_dataset_metadata(
    language: SupportedLanguages,
) -> tuple[tuple[list[dict[str, str]], ...], list]:
    """Change the language for the displayed dataset metadata.

    This is done in three steps:
    - Update the chosen language globally.
    - Update the language for dropdown options.
    - Update the language of all the metadata values.
    """
    update_global_language_state(language)
    return (
        *(
            get_options_for_language(language, e)
            for e in DISPLAYED_DROPDOWN_DATASET_ENUMS
        ),
        update_dataset_metadata_language(),
    )
