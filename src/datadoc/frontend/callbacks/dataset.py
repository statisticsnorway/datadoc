"""Callbacks relating to datasets."""

from __future__ import annotations

import logging
import traceback
from typing import TYPE_CHECKING

from dash import no_update
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import get_dataset_path
from datadoc.frontend.callbacks.utils import parse_and_validate_dates
from datadoc.frontend.fields.display_dataset import (
    DROPDOWN_DATASET_METADATA_IDENTIFIERS,
)
from datadoc.frontend.fields.display_dataset import (
    MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
)
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.utils import METADATA_DOCUMENT_FILE_SUFFIX

if TYPE_CHECKING:
    from datadoc_model.model import LanguageStringType

logger = logging.getLogger(__name__)

VALIDATION_ERROR = "Validation error: "
DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}{DatasetIdentifiers.CONTAINS_DATA_FROM.value} must be the same or earlier date than {DatasetIdentifiers.CONTAINS_DATA_UNTIL.value}"


def open_file(file_path: str | None = None) -> DataDocMetadata:
    """Load the given dataset into a DataDocMetadata instance."""
    if file_path and file_path.endswith(METADATA_DOCUMENT_FILE_SUFFIX):
        logger.info("Opening existing metadata document %s", file_path)
        return DataDocMetadata(
            state.statistic_subject_mapping,
            metadata_document_path=file_path.strip(),
        )

    dataset = file_path or get_dataset_path()
    if dataset:
        logger.info("Opening dataset %s", dataset)
    return DataDocMetadata(
        state.statistic_subject_mapping,
        dataset_path=str(dataset).strip() if dataset else None,
    )


def open_dataset_handling(
    n_clicks: int,
    file_path: str,
    dataset_opened_counter: int,
) -> tuple[bool, bool, bool, str, int]:
    """Handle errors and other logic around opening a dataset file."""
    if file_path:
        file_path = file_path.strip()
    try:
        state.metadata = open_file(file_path)
    except FileNotFoundError:
        logger.exception("File %s not found", str(file_path))
        return (
            False,
            True,
            False,
            f"Filen '{file_path}' finnes ikke.",
            no_update,
        )
    except Exception as e:  # noqa: BLE001
        return (
            False,
            True,
            False,
            "\n".join(traceback.format_exception_only(type(e), e)),
            no_update,
        )
    dataset_opened_counter += 1
    if n_clicks and n_clicks > 0:
        dapla_dataset_path_info = DaplaDatasetPathInfo(file_path)
        if not dapla_dataset_path_info.path_complies_with_naming_standard():
            return (
                True,
                False,
                True,
                "",
                dataset_opened_counter,
            )
        return (
            True,
            False,
            False,
            "",
            dataset_opened_counter,
        )
    return (
        False,
        False,
        False,
        "",
        dataset_opened_counter,
    )


def process_keyword(value: str) -> list[str]:
    """Convert a comma separated string to a list of strings.

    e.g. 'a,b ,c' -> ['a', 'b', 'c']
    """
    return [item.strip() for item in value.split(",")]


def process_special_cases(
    value: MetadataInputTypes | LanguageStringType,
    metadata_identifier: str,
    language: str | None = None,
) -> MetadataInputTypes | LanguageStringType:
    """Pre-process metadata where needed.

    Some types of metadata need processing before being saved
    to the model. Handle these cases here, other values are
    returned unchanged.
    """
    updated_value: MetadataInputTypes | LanguageStringType
    if metadata_identifier == DatasetIdentifiers.KEYWORD.value and isinstance(
        value,
        str,
    ):
        updated_value = process_keyword(value)
    elif metadata_identifier == DatasetIdentifiers.VERSION.value:
        updated_value = str(value)
    elif metadata_identifier in MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS and isinstance(
        value,
        str,
    ):
        if language is not None:
            updated_value = find_existing_language_string(
                state.metadata.dataset,
                value,
                metadata_identifier,
                language,
            )
    elif metadata_identifier in DROPDOWN_DATASET_METADATA_IDENTIFIERS and value == "":
        updated_value = None
    else:
        updated_value = value

    # Other values get returned unchanged
    return updated_value


def accept_dataset_metadata_input(
    value: MetadataInputTypes | LanguageStringType,
    metadata_identifier: str,
    language: str | None = None,
) -> tuple[bool, str]:
    """Handle user inputs of dataset metadata values."""
    logger.debug(
        "Received updated value = %s for metadata_identifier = %s",
        value,
        metadata_identifier,
    )
    try:
        value = process_special_cases(value, metadata_identifier, language)
        # Update the value in the model
        setattr(
            state.metadata.dataset,
            metadata_identifier,
            value,
        )
    except (ValidationError, ValueError) as e:
        show_error = True
        error_explanation = str(e)
        logger.exception("Error while reading in value for %s", metadata_identifier)
    else:
        show_error = False
        error_explanation = ""
        logger.info(
            "Updated dataset %s with value %s",
            metadata_identifier,
            value,
        )

    return show_error, error_explanation


def accept_dataset_metadata_date_input(
    dataset_identifier: DatasetIdentifiers,
    contains_data_from: str | None,
    contains_data_until: str | None,
) -> tuple[bool, str, bool, str]:
    """Validate and save date range inputs."""
    try:
        (
            parsed_contains_data_from,
            parsed_contains_data_until,
        ) = parse_and_validate_dates(
            str(contains_data_from),
            str(contains_data_until),
        )

        if parsed_contains_data_from:
            state.metadata.dataset.contains_data_from = (
                parsed_contains_data_from.isoformat()
            )

        if parsed_contains_data_until:
            state.metadata.dataset.contains_data_until = (
                parsed_contains_data_until.isoformat()
            )

    except (ValidationError, ValueError) as e:
        logger.exception(
            "Validation failed for %s, %s, %s: %s, %s",
            dataset_identifier,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message: str | None = str(e)
    else:
        logger.debug(
            "Successfully updated %s, %s, %s: %s, %s",
            dataset_identifier,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message = None

    no_error = (False, "")
    if not message:
        # No error to display.
        return no_error + no_error

    error = (True, message)
    return (
        error + no_error
        if dataset_identifier == DatasetIdentifiers.CONTAINS_DATA_FROM
        else no_error + error
    )
