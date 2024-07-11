from __future__ import annotations

import datetime

import arrow
from pydantic import field_validator


@field_validator("data from")
# @classmethod
def check_valid_date(
    start_date: str | datetime.datetime | None,
) -> datetime.datetime | None:
    """."""
    parsed_start = None
    try:
        if start_date is not None:
            parsed_start = arrow.get(start_date)
    except arrow.parser.ParserError as e:
        raise ValueError(str(e)) from e
    return parsed_start.astimezone(tz=datetime.timezone.utc) if parsed_start else None
