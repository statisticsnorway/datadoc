"""Extract info from a path following SSB's dataset naming convention."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

import arrow
import contextlib
import pathlib
import re


class SupportedDateFormats(Enum):
    """The Date formats supported by the naming convention."""

    ISO_YEAR = "YYYY"  # String format YYYY
    ISO_YEAR_MONTH = "YYYY-MM"  # String format YYYY-MM
    ISO_YEAR_MONTH_DAY = "YYYY-MM-DD"  # String format YYYY-MM-DD
    SSB_YEAR_SEMESTER = "YYYY-Hn"  # String format YYYY-Hn
    SSB_YEAR_TRIMESTER = "YYYY-Tn"  # String format YYYY-Tn
    SSB_YEAR_QUARTER = "YYYY-Qn"  # String format YYYY-Qn
    SSB_YEAR_BIMESTER = "YYYY-Bn"  # String format YYYY-Bn
    SSB_YEAR_WEEK = "YYYY-Wnn"  # String format YYYY-Wnn
    UNKNOWN = "UNKNOWN"


def categorize_period_string(period: str) -> SupportedDateFormats:
    """A naive string validator."""
    match RegexEqualCompiler(period):
        case r"\d{4}\-H\d":
            return SupportedDateFormats.SSB_YEAR_SEMESTER
        case r"\d{4}\-T\d":
            return SupportedDateFormats.SSB_YEAR_TRIMESTER
        case r"\d{4}\-Q\d":
            return SupportedDateFormats.SSB_YEAR_QUARTER
        case r"\d{4}\-B\d":
            return SupportedDateFormats.SSB_YEAR_BIMESTER
        case r"\d{4}\-W\d\d":
            return SupportedDateFormats.SSB_YEAR_WEEK
        case r"\d{4}\-\d{2}\-\d{2}":
            return SupportedDateFormats.ISO_YEAR_MONTH_DAY
        case r"\d{4}\-\d{2}":
            return SupportedDateFormats.ISO_YEAR_MONTH
        case r"\d{4}":
            return SupportedDateFormats.ISO_YEAR
        case _:
            return SupportedDateFormats.UNKNOWN


class RegexEqualCompiler(str):
    """Handler class for checking regex patterns."""

    def __init__(self, pattern) -> None:
        self.pattern = re.compile(pattern)

    def __eq__(self, pattern: object) -> bool:
        """Returns true on match with tested pattern."""
        return bool(re.search(str(pattern), self))


class DaplaDatasetPathInfo:
    """Extract info from a path following SSB's dataset naming convention."""

    def __init__(self, dataset_path: str) -> None:
        """Read info from an path following SSB`s naming convention."""
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")
        _period_strings = self._extract_period_strings(self.dataset_name_sections)
        self.first_period_string = _period_strings[0]
        self.second_period_string = _period_strings[0]
        self.date_format = categorize_period_string(self.first_period_string)

        with contextlib.suppress(IndexError):
            self.second_period_string = _period_strings[1]

    def _extract_period_strings(self, dataset_name_sections: list[str]) -> list[str]:
        """Extract period strings from dataset name sections.

        Iterates over the dataset name sections and returns a list of strings
        that match the year regex, stripping the first character. This extracts
        the year periods from the dataset name.
        """
        date_format_regex = re.compile(
            r"^p\d{4}(?:-\d{2}-\d{2}|-\d{2}|[QTHWB]\d{1,2})?$"
        )

        return [
            x[1:]
            for x in dataset_name_sections
            if re.match(date_format_regex, x) is not None
        ]

    @property
    def contains_data_from(self) -> datetime.date:
        """The earliest date from which data in the dataset is relevant for."""
        match (self.date_format):
            case SupportedDateFormats.ISO_YEAR:
                return (
                    arrow.get(self.first_period_string, self.date_format.value)
                    .floor("year")
                    .date()
                )
            case _:
                return datetime.now(timezone.utc).astimezone()

    @property
    def contains_data_until(self) -> datetime.date:
        """The latest date until which data in the dataset is relevant for."""
        year = self.second_period_string
        return arrow.get(year, "YYYY").ceil("year").date()
