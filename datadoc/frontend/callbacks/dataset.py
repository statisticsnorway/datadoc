import logging
from typing import Any, List, Tuple

from pydantic import ValidationError

import datadoc.state as state
from datadoc.frontend.callbacks.utils import (
    find_existing_language_string,
    get_options_for_language,
    update_global_language_state,
)
from datadoc.frontend.fields.DisplayDataset import (
    DISPLAYED_DATASET_METADATA,
    DISPLAYED_DROPDOWN_DATASET_ENUMS,
    MULTIPLE_LANGUAGE_DATASET_METADATA,
)

logger = logging.getLogger(__name__)


def accept_dataset_metadata_input(
    value: Any, metadata_identifier: str
) -> Tuple[bool, str]:
    logger.debug(f"Received update {value = } for {metadata_identifier = }")
    try:
        if (
            metadata_identifier in MULTIPLE_LANGUAGE_DATASET_METADATA
            and type(value) is str
        ):
            value = find_existing_language_string(
                state.metadata.meta.dataset, value, metadata_identifier
            )

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


def change_language_dataset_metadata(language):
    update_global_language_state(language)
    return (
        *(
            get_options_for_language(language, e)
            for e in DISPLAYED_DROPDOWN_DATASET_ENUMS
        ),
        update_dataset_metadata_language(),
    )
