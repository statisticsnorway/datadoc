"""Callbacks relating to datasets."""

from __future__ import annotations

import logging
import traceback

import arrow
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.enums import (
    SupportedLanguages,  # noqa: TCH001 import is needed for docs build
)
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import get_dataset_path
from datadoc.frontend.callbacks.utils import update_global_language_state
from datadoc.frontend.fields.display_dataset import DISPLAYED_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DISPLAYED_DROPDOWN_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import MULTIPLE_LANGUAGE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.utils import METADATA_DOCUMENT_FILE_SUFFIX

logger = logging.getLogger(__name__)

VALIDATION_ERROR = "Validation error: "
DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}{DatasetIdentifiers.CONTAINS_DATA_FROM.value} must be the same or earlier date than {DatasetIdentifiers.CONTAINS_DATA_UNTIL.value}"


def open_file(file_path: str | None = None) -> DataDocMetadata:
    """Load the given dataset into a DataDocMetadata instance."""
    if file_path and file_path.endswith(METADATA_DOCUMENT_FILE_SUFFIX):
        logger.info("Opening existing metadata document %s", file_path)
        return DataDocMetadata(
            state.statistic_subject_mapping,
            metadata_document_path=file_path,
        )

    dataset = file_path or get_dataset_path()
    logger.info("Opening dataset %s", dataset)
    return DataDocMetadata(state.statistic_subject_mapping, dataset_path=dataset)


def open_dataset_handling(
    n_clicks: int,
    file_path: str,
) -> tuple[bool, bool, str, str]:
    """Handle errors and other logic around opening a dataset file."""
    try:
        state.metadata = open_file(file_path)
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


def process_keyword(value: str) -> list[str]:
    """Convert a comma separated string to a list of strings.

    e.g. 'a,b ,c' -> ['a', 'b', 'c']
    """
    return [item.strip() for item in value.split(",")]


def _validate_dates(
    metadata_identifier: str,
    value: MetadataInputTypes,
) -> MetadataInputTypes:
    """Validate that CONTAINS_DATA_FROM is earlier or identical to CONTAINS_DATA_UNTIL."""
    if not value:
        return value
    try:
        parsed_value = arrow.get(str(value), "YYYY-MM-DD")
    except arrow.parser.ParserMatchError as e:
        raise ValueError(VALIDATION_ERROR + str(e)) from e
    if (
        metadata_identifier == DatasetIdentifiers.CONTAINS_DATA_FROM.value
        and state.metadata.meta.dataset.contains_data_until
        and state.metadata.meta.dataset.contains_data_until != "None"
    ):
        if parsed_value > arrow.get(
            state.metadata.meta.dataset.contains_data_until,
        ):
            raise ValueError(DATE_VALIDATION_MESSAGE)
    elif (
        metadata_identifier == DatasetIdentifiers.CONTAINS_DATA_UNTIL.value
        and state.metadata.meta.dataset.contains_data_from
        and state.metadata.meta.dataset.contains_data_from != "None"
    ) and arrow.get(state.metadata.meta.dataset.contains_data_from) > parsed_value:
        raise ValueError(DATE_VALIDATION_MESSAGE)

    return parsed_value.format("YYYY-MM-DD")


def process_special_cases(
    value: MetadataInputTypes,
    metadata_identifier: str,
) -> MetadataInputTypes:
    """Pre-process metadata where needed.

    Some types of metadata need processing before being saved
    to the model. Handle these cases here, other values are
    returned unchanged.
    """
    updated_value: MetadataInputTypes
    if metadata_identifier == DatasetIdentifiers.KEYWORD.value and isinstance(
        value,
        str,
    ):
        updated_value = process_keyword(value)
    elif metadata_identifier in [
        DatasetIdentifiers.CONTAINS_DATA_FROM.value,
        DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
    ]:
        updated_value = _validate_dates(metadata_identifier, value)
    elif metadata_identifier == DatasetIdentifiers.VERSION.value:
        updated_value = str(value)
    elif metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA and isinstance(
        value,
        str,
    ):
        updated_value = find_existing_language_string(
            state.metadata.meta.dataset,
            value,
            metadata_identifier,
        )
    else:
        updated_value = value

    # Other values get returned unchanged
    return updated_value


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
    except (ValidationError, ValueError) as e:
        show_error = True
        error_explanation = f"{e}"
        logger.exception("Error while reading in value for %s", metadata_identifier)
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
) -> tuple[object, ...]:
    """Change the language for the displayed dataset metadata.

    This is done in three steps:
    - Update the chosen language globally.
    - Update the language for dropdown options.
    - Update the language of all the metadata values.
    """
    update_global_language_state(language)
    return (
        *(e.options_getter(language) for e in DISPLAYED_DROPDOWN_DATASET_METADATA),
        update_dataset_metadata_language(),
    )
