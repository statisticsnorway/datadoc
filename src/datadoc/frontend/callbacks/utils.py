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
from datadoc.frontend.components.dataset_tab import build_dataset_tab
from datadoc.frontend.components.variables_tab import build_variables_tab

if TYPE_CHECKING:
    import pathlib
    from enum import Enum

    import pydantic
    from cloudpathlib import CloudPath
    from dash import html


logger = logging.getLogger(__name__)


MetadataInputTypes: TypeAlias = (
    str | list[str] | int | float | bool | datetime.date | None
)


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


def _check_if_language_string_item_exists(
    language_strings: model.LanguageStringType,
    language_code: str,
) -> bool:
    if language_strings.root is None:
        return False
    return any(i.languageCode == language_code for i in language_strings.root)


def _update_language_string_item(
    language_strings: model.LanguageStringType,
    language_code: str,
    new_value: str,
) -> None:
    if language_strings.root is not None:
        for i in language_strings.root:
            if i.languageCode == language_code:
                i.languageText = new_value


def _add_language_string_item(
    language_strings: model.LanguageStringType,
    language_code: str,
    language_text: str,
) -> None:
    if language_strings.root is not None:
        language_strings.root.append(
            model.LanguageStringTypeItem(
                languageCode=language_code,
                languageText=language_text,
            ),
        )


def find_existing_language_string(
    metadata_model_object: pydantic.BaseModel,
    value: str,
    metadata_identifier: str,
    language: str,
) -> model.LanguageStringType | None:
    """Get or create a LanguageStrings object and return it."""
    language_strings = getattr(metadata_model_object, metadata_identifier)

    if language_strings is not None:
        if _check_if_language_string_item_exists(
            language_strings,
            language,
        ):
            _update_language_string_item(
                language_strings,
                language,
                value,
            )
        elif value != "":
            _add_language_string_item(
                language_strings,
                language,
                value,
            )
        else:
            return None
    elif value != "":
        language_strings = model.LanguageStringType(
            root=[
                model.LanguageStringTypeItem(
                    languageCode=language,
                    languageText=value,
                ),
            ],
        )
    else:
        # Don't create an item if the value is empty
        return None
    return language_strings


def get_dataset_path() -> pathlib.Path | CloudPath | str:
    """Extract the path to the dataset from the potential sources."""
    if state.metadata.dataset_path is not None:
        return state.metadata.dataset_path
    path_from_env = config.get_datadoc_dataset_path()
    if path_from_env:
        logger.info(
            "Dataset path from env var: '%s'",
            path_from_env,
        )
    if path_from_env is None:
        path_from_env = ""
    return path_from_env


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


def render_tabs(tab: str) -> html.Article | None:
    """Render tab content."""
    if tab == "dataset":
        return build_dataset_tab()
    if tab == "variables":
        return build_variables_tab()
    return None


def get_metadata_field_display_name(field: str | tuple, filter_list: list) -> str:
    """Return field display name if tuple in list."""
    output = tuple(tup for tup in filter_list if any(field[0] == i for i in tup))
    tuple_result: tuple = _check_tuple_length(output)
    return _get_display_name_value(tuple_result)


def _check_tuple_length(input_value: tuple) -> tuple:
    """Filter single tuple."""
    return input_value[0] if len(input_value) == 1 else input_value


def _get_display_name_value(field: tuple) -> str:
    """Get display name from tuple.

    Tuple contains identifier and display name.
    """
    return field[1]


def obligatory_metadata(metadata: tuple, obligatory_metadata: list) -> bool:
    """Hard check metadata field.

    Tuple contains identifier and value.
    """
    if metadata[0] in obligatory_metadata and metadata[1] is None:
        return False
    return True
