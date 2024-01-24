"""Extract info from an path following SSB`s naming convention."""
from __future__ import annotations

import contextlib
import pathlib
import re
from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    import datetime


class DaplaDatasetPathInfo:
    """Extract info from an path following SSB`s naming convention."""

    year_regex = re.compile(r"p(19|20|21)\d{2}")

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
        return [
            x[1:]
            for x in dataset_name_sections
            if re.match(self.year_regex, x) is not None
        ]

    @property
    def contains_data_from(self) -> datetime.date:
        """The earliest date from which data in the dataset is relevant for."""
        return arrow.get(self.first_period_string).date()
