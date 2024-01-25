"""Extract info from a path following SSB's dataset naming convention."""
from __future__ import annotations

import contextlib
import pathlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Literal

import arrow

if TYPE_CHECKING:
    import datetime


@dataclass
class IsoDateFormat:
    """An ISO date format with relevant patterns."""

    name: str
    regex_pattern: str
    arrow_pattern: str
    timeframe: Literal["year", "month", "day", "week"]


ISO_YEAR = IsoDateFormat(
    name="ISO_YEAR",
    regex_pattern=r"^\d{4}$",
    arrow_pattern="YYYY",
    timeframe="year",
)
ISO_YEAR_MONTH = IsoDateFormat(
    name="ISO_YEAR_MONTH",
    regex_pattern=r"^\d{4}\-\d{2}$",
    arrow_pattern="YYYY-MM",
    timeframe="month",
)
ISO_YEAR_MONTH_DAY = IsoDateFormat(
    name="ISO_YEAR_MONTH_DAY",
    regex_pattern=r"^\d{4}\-\d{2}\-\d{2}$",
    arrow_pattern="YYYY-MM-DD",
    timeframe="day",
)
ISO_YEAR_WEEK = IsoDateFormat(
    name="ISO_YEAR_WEEK",
    regex_pattern=r"^\d{4}\-W\d{2}$",
    arrow_pattern="YYYY-Wnn",
    timeframe="week",
)

SUPPORTED_DATE_FORMATS = [
    ISO_YEAR,
    ISO_YEAR_MONTH,
    ISO_YEAR_MONTH_DAY,
    ISO_YEAR_WEEK,
]


def categorize_period_string(period: str) -> IsoDateFormat | None:
    """A naive string validator."""
    for date_format in reversed(SUPPORTED_DATE_FORMATS):
        if re.match(date_format.regex_pattern, period):
            return date_format

    return None


class DaplaDatasetPathInfo:
    """Extract info from a path following SSB's dataset naming convention."""

    def __init__(self, dataset_path: str) -> None:
        """Read info from an path following SSB`s naming convention."""
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")
        _period_strings = self._extract_period_strings(self.dataset_name_sections)
        self.first_period_string = _period_strings[0]
        self.second_period_string: str | None = None

        with contextlib.suppress(IndexError):
            self.second_period_string = _period_strings[1]

    def _extract_period_strings(self, dataset_name_sections: list[str]) -> list[str]:
        """Extract period strings from dataset name sections.

        Iterates over the dataset name sections and returns a list of strings
        that match the year regex, stripping the first character. This extracts
        the year periods from the dataset name.
        """
        date_format_regex = re.compile(
            r"^p\d{4}(?:-\d{2}-\d{2}|-\d{2}|-[QTHWB]\d{1,2})?$",
        )

        return [
            x[1:]
            for x in dataset_name_sections
            if re.match(date_format_regex, x) is not None
        ]

    @property
    def contains_data_from(self) -> datetime.date:
        """The earliest date from which data in the dataset is relevant for."""
        if date_format := categorize_period_string(self.first_period_string):
            return (
                arrow.get(self.first_period_string, date_format.arrow_pattern)
                .floor(date_format.timeframe)
                .date()
            )

        msg = f"Period format {self.first_period_string} is not supported"
        raise NotImplementedError(
            msg,
        )

    @property
    def contains_data_until(self) -> datetime.date:
        """The latest date until which data in the dataset is relevant for."""
        period_string = self.second_period_string or self.first_period_string
        if date_format := categorize_period_string(self.first_period_string):
            return (
                arrow.get(period_string, date_format.arrow_pattern)
                .ceil(date_format.timeframe)
                .date()
            )

        msg = f"Period format {period_string} is not supported"
        raise NotImplementedError(
            msg,
        )
