"""Functions which aren't directly called from a decorated callback."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import cast

import arrow
from datadoc_model import model

from datadoc import config
from datadoc import enums
from datadoc import state

if TYPE_CHECKING:
    import pathlib
    from enum import Enum

    import pydantic
    from cloudpathlib import CloudPath

    from datadoc.enums import SupportedLanguages

logger = logging.getLogger(__name__)


MetadataInputTypes: TypeAlias = (
    str | list[str] | int | float | bool | datetime.date | None
)


def update_global_language_state(language: SupportedLanguages) -> None:
    """Update global language state."""
    if state.current_metadata_language != language:
        logger.debug("Updating language: %s", language.name)
        state.current_metadata_language = language


def get_language_strings_enum(
    enum: Enum | type[enums.LanguageStringsEnum],
) -> enums.LanguageStringsEnum:
    """Get the correct language strings enum for the given enum.

    We need multiple languages to display in the front end, but the model only defines a single language in the enums.
    """
    language_strings_enum: enums.LanguageStringsEnum = getattr(
        enums,
        cast(type[enums.LanguageStringsEnum], enum).__name__,
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
        for i in get_language_strings_enum(enum)  # type: ignore [arg-type, attr-defined]
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


def get_dataset_path() -> pathlib.Path | CloudPath | str | None:
    """Extract the path to the dataset from the potential sources."""
    if state.metadata.dataset_path is not None:
        return state.metadata.dataset_path
    path_from_env = config.get_datadoc_dataset_path()
    logger.info(
        "Dataset path from env var: '%s'",
        path_from_env,
    )
    return path_from_env


ISO_DATE_FORMAT = "YYYY-MM-DD"

VALIDATION_ERROR = "Validation error: "
DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}contains_data_from must be the same or earlier date than contains_data_until"


def parse_and_validate_dates(
    start_date: str | datetime.datetime | None,
    end_date: str | datetime.datetime | None,
) -> tuple[datetime.datetime | None, datetime.datetime | None]:
    """Parse and validate the given dates.

     Validate that:
         - The dates are in YYYY-MM-DD format
         - The start date is earlier or identical to the end date.

    Examples:
    >>> parse_and_validate_dates("2021-01-01", "2021-01-01")
    (datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

    >>> parse_and_validate_dates("1990-01-01", "2050-01-01")
    (datetime.datetime(1990, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2050, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

    >>> parse_and_validate_dates(None, None)
    (None, None)

    >>> parse_and_validate_dates("1st January 2021", "1st January 2021")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: Expected an ISO 8601-like string, but was given '1st January 2021'. Try passing in a format string to resolve this.

    >>> parse_and_validate_dates(datetime.datetime(2050, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "1990-01-01")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: contains_data_from must be the same or earlier date than contains_data_until

    >>> parse_and_validate_dates("2050-01-01", "1990-01-01")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: contains_data_from must be the same or earlier date than contains_data_until
    """
    parsed_start = None
    parsed_end = None
    try:
        if start_date and start_date != "None":
            parsed_start = arrow.get(start_date)
        if end_date and end_date != "None":
            parsed_end = arrow.get(end_date)
    except arrow.parser.ParserError as e:
        raise ValueError(VALIDATION_ERROR + str(e)) from e

    if parsed_start and parsed_end and (parsed_start > parsed_end):
        raise ValueError(DATE_VALIDATION_MESSAGE)

    start_output = (
        parsed_start.astimezone(tz=datetime.timezone.utc) if parsed_start else None
    )
    end_output = parsed_end.astimezone(tz=datetime.timezone.utc) if parsed_end else None

    return start_output, end_output
