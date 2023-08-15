import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from datadoc_model.Enums import SupportedLanguages
from pydantic import ValidationError

import datadoc.state as state
from datadoc.backend.DataDocMetadata import DataDocMetadata
from datadoc.frontend.callbacks.utils import (
    find_existing_language_string,
    get_options_for_language,
    update_global_language_state,
)
from datadoc.frontend.fields.DisplayDataset import (
    DISPLAYED_DATASET_METADATA,
    DISPLAYED_DROPDOWN_DATASET_ENUMS,
    MULTIPLE_LANGUAGE_DATASET_METADATA,
    DatasetIdentifiers,
)

logger = logging.getLogger(__name__)

DATADOC_DATASET_PATH_ENV_VAR = "DATADOC_DATASET_PATH"


def get_dataset_path() -> str | Path | None:
    if state.metadata.dataset is not None:
        return state.metadata.dataset
    elif path_from_env := os.getenv(DATADOC_DATASET_PATH_ENV_VAR):
        logger.info(
            f"Dataset path from {DATADOC_DATASET_PATH_ENV_VAR}: '{path_from_env}'"
        )
        dataset = path_from_env
    else:
        dataset = None

    return dataset


def open_dataset(dataset_path: str | Path | None = None) -> None:
    dataset = dataset_path or get_dataset_path()
    state.metadata = DataDocMetadata(dataset)
    logger.info(f"Opened dataset {dataset}")


def process_keyword(value: str) -> Optional[List[str]]:
    if value is None:
        return None
    return [item.strip() for item in value.split(",")]


def process_special_cases(value: Any, metadata_identifier: str):
    """
    docstring
    """
    if metadata_identifier == DatasetIdentifiers.KEYWORD.value:
        value = process_keyword(value)
    if metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA:
        value = find_existing_language_string(
            state.metadata.meta.dataset, value, metadata_identifier
        )

    return value


def accept_dataset_metadata_input(
    value: Any, metadata_identifier: str
) -> Tuple[bool, str]:
    logger.debug(f"Received update {value = } for {metadata_identifier = }")
    try:
        value = process_special_cases(value, metadata_identifier)

        logger.debug(f"Updating {value = } for {metadata_identifier = }")
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
        logger.debug(f"Successfully updated {metadata_identifier} with {value}")

    return show_error, error_explanation


def update_dataset_metadata_language() -> List[Any]:
    """Return new values for ALL the dataset metadata inputs to allow
    editing of strings in the chosen language"""
    return [
        m.value_getter(state.metadata.meta.dataset, m.identifier)
        for m in DISPLAYED_DATASET_METADATA
    ]


def change_language_dataset_metadata(
    language: SupportedLanguages,
) -> tuple[tuple[List[Dict[str, str]], ...], List]:
    update_global_language_state(language)
    return (
        *(
            get_options_for_language(language, e)
            for e in DISPLAYED_DROPDOWN_DATASET_ENUMS
        ),
        update_dataset_metadata_language(),
    )
