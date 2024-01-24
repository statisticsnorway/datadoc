"""Extract info from a path following SSB's dataset naming convention."""
from __future__ import annotations

import contextlib
import pathlib
import re
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    import datetime


class SupportedDateFormats(Enum):
    """The Date formats supported by the naming convention."""
    ISO_YEAR = auto() # String format YYYY
    ISO_YEAR_MONTH = auto() # String format YYYY-MM
    ISO_YEAR_MONTH_DAY = auto() # String format YYYY-MM-DD
    SSB_YEAR_SEMESTER = auto()    SSB_YEAR_TRIMESTER = auto() # String format YYYY-Tn
    SSB_YEAR_QUARTER = auto() # String format YYYY-Qn
    SSB_YEAR_BIMESTER = auto() # String format YYYY-Bn
    SSB_YEAR_WEEK = auto() # String format YYYY-Wnn


class RegexEqual(str):
    """Helper class for structual pattern matching using regex."""
    def __eq__(self, pattern:str)->bool:
        return bool(re.search(pattern, self))


class DaplaDatasetPathInfo:
    """Extract info from a path following SSB's dataset naming convention."""

    date_format_regex = re.compile(r"^p\d{4}(?:-\d{2}|-\d{2}-\d{2}|[QTHWB]\d{1,2})?$")

    def __init__(self, dataset_path: str) -> None:
        """Read info from an path following SSB`s naming convention."""
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")
        _period_strings = self._extract_period_strings(self.dataset_name_sections)
        self.first_period_string = _period_strings[0]
        self.second_period_string: str | None = None

        with contextlib.suppress(IndexError):
            self.second_period_string = _period_strings[1]


    def _categorize_period_string(self,period: str) -> SupportedDateFormats:
        """A naive string validator."""
        match RegexEqual(period):
            case r"\d+":
                return SupportedDateFormats.ISO_YEAR


    def _extract_period_strings(self, dataset_name_sections: list[str]) -> list[str]:
        """Extract period strings from dataset name sections.

        Iterates over the dataset name sections and returns a list of strings
        that match the year regex, stripping the first character. This extracts
        the year periods from the dataset name.
        """
        return [
            x[1:]
            for x in dataset_name_sections
            if re.match(self.date_format_regex, x) is not None
        ]

    @property
    def contains_data_from(self) -> datetime.date:
        """The earliest date from which data in the dataset is relevant for."""
        return arrow.get(self.first_period_string, "YYYY").floor("year").date()

    @property
    def contains_data_until(self) -> datetime.date:
        """The latest date until which data in the dataset is relevant for."""
        year = self.second_period_string or self.first_period_string
        return arrow.get(year, "YYYY").ceil("year").date()
