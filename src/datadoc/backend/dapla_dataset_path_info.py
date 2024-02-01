"""Extract info from a path following SSB's dataset naming convention."""
from __future__ import annotations

import pathlib
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Final
from typing import Literal

import arrow

from datadoc.enums import DatasetState
from datadoc.enums import SupportedLanguages

if TYPE_CHECKING:
    import datetime
    import os
    from datetime import date


@dataclass
class DateFormat(ABC):
    """A super class for date formats."""

    name: str
    regex_pattern: str
    arrow_pattern: str
    timeframe: Literal["year", "month", "day", "week"]

    @abstractmethod
    def get_floor(self, period_string: str) -> date | None:
        """Return first date of timeframe period."""

    @abstractmethod
    def get_ceil(self, period_string: str) -> date | None:
        """Return last date of timeframe period."""


@dataclass
class IsoDateFormat(DateFormat):
    """A subclass of Dateformat with relevant patterns for ISO dates."""

    def get_floor(self, period_string: str) -> date | None:
        """Method.

        >>> ISO_YEAR_MONTH.get_floor("1980-08")
        datetime.date(1980, 8, 1)

        >>> ISO_YEAR.get_floor("2021")
        datetime.date(2021, 1, 1)

        >>> SSB_BIMESTER.get_floor("2003B4")
        datetime.date(2003, 7, 1)

        """
        return arrow.get(period_string, self.arrow_pattern).floor(self.timeframe).date()

    def get_ceil(self, period_string: str) -> date | None:
        """Method.

        >>> ISO_YEAR.get_ceil("1921")
        datetime.date(1921, 12, 31)

        >>> ISO_YEAR_MONTH.get_ceil("2021-05")
        datetime.date(2021, 5, 31)

        >>> SSB_HALF_YEAR.get_ceil("2024H1")
        datetime.date(2024, 6, 30)

        """
        return arrow.get(period_string, self.arrow_pattern).ceil(self.timeframe).date()


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
    regex_pattern=r"^\d{4}\-{0,1}W\d{2}$",
    arrow_pattern="W",
    timeframe="week",
)


@dataclass
class SsbDateFormat(DateFormat):
    """A subclass of Dateformat with relevant patterns for SSB unique dates."""

    ssb_dates: dict

    def get_floor(self, period_string: str) -> date | None:
        """Convert SSB format to date-string and return first date.

        If not excisting SSB format, return None

        >>> SSB_BIMESTER.get_floor("2003B8")
        None

        """
        try:
            year = period_string[:4]
            month = self.ssb_dates[period_string[-2:]]["start"]
            period = year + month
            return arrow.get(period, self.arrow_pattern).floor(self.timeframe).date()
        except KeyError:
            return None

    def get_ceil(self, period_string: str) -> date | None:
        """Convert SSB format to date-string and return last date.

        If not excisting SSB format, return None

        >>> SSB_TRIANNUAL.get_ceil("1999T11")
        None

        """
        try:
            year = period_string[:4]
            month = self.ssb_dates[period_string[-2:]]["end"]
            period = year + month
            return arrow.get(period, self.arrow_pattern).ceil(self.timeframe).date()
        except KeyError:
            return None


SSB_BIMESTER = SsbDateFormat(
    name="SSB_BIMESTER",
    regex_pattern=r"\d{4}[B]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "B1": {
            "start": "01",
            "end": "02",
        },
        "B2": {
            "start": "03",
            "end": "04",
        },
        "B3": {
            "start": "05",
            "end": "06",
        },
        "B4": {
            "start": "07",
            "end": "08",
        },
        "B5": {
            "start": "09",
            "end": "10",
        },
        "B6": {
            "start": "11",
            "end": "12",
        },
    },
)

SSB_QUARTERLY = SsbDateFormat(
    name="SSB_QUARTERLY",
    regex_pattern=r"\d{4}[Q]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "Q1": {
            "start": "01",
            "end": "03",
        },
        "Q2": {
            "start": "04",
            "end": "06",
        },
        "Q3": {
            "start": "07",
            "end": "09",
        },
        "Q4": {
            "start": "10",
            "end": "12",
        },
    },
)

SSB_TRIANNUAL = SsbDateFormat(
    name="SSB_TRIANNUAL",
    regex_pattern=r"\d{4}[T]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "T1": {
            "start": "01",
            "end": "04",
        },
        "T2": {
            "start": "05",
            "end": "08",
        },
        "T3": {
            "start": "09",
            "end": "12",
        },
    },
)
SSB_HALF_YEAR = SsbDateFormat(
    name="SSB_HALF_YEAR",
    regex_pattern=r"\d{4}[H]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "H1": {
            "start": "01",
            "end": "06",
        },
        "H2": {
            "start": "07",
            "end": "12",
        },
    },
)

SUPPORTED_DATE_FORMATS: list[IsoDateFormat | SsbDateFormat] = [
    ISO_YEAR,
    ISO_YEAR_MONTH,
    ISO_YEAR_MONTH_DAY,
    ISO_YEAR_WEEK,
    SSB_BIMESTER,
    SSB_QUARTERLY,
    SSB_TRIANNUAL,
    SSB_HALF_YEAR,
]


def categorize_period_string(period: str) -> IsoDateFormat | SsbDateFormat:
    """Categorize a period string into one of the supported date formats.

    If the period string is not recognized, a NotImplementedError is raised.

    Examples:
    >>> date_format = categorize_period_string('2022-W01')
    >>> date_format.name
    ISO_YEAR_WEEK

    >>> date_format = categorize_period_string('1954T2')
    >>> date_format.name
    SSB_TRIANNUAL

    >>> categorize_period_string('unknown format')
    Traceback (most recent call last):
     ...
    NotImplementedError: Period format unknown format is not supported
    """
    for date_format in SUPPORTED_DATE_FORMATS:
        if re.match(date_format.regex_pattern, period):
            return date_format

    msg = f"Period format {period} is not supported"
    raise NotImplementedError(
        msg,
    )


class DaplaDatasetPathInfo:
    """Extract info from a path following SSB's dataset naming convention."""

    def __init__(self, dataset_path: str | os.PathLike[str]) -> None:
        """Digest the path so that it's ready for further parsing."""
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")
        self._period_strings = self._extract_period_strings(self.dataset_name_sections)

    @staticmethod
    def _extract_period_strings(dataset_name_sections: list[str]) -> list[str]:
        """Extract period strings from dataset name sections.

        Iterates over the dataset name sections and returns a list of strings
        that match the year regex, stripping the first character. This extracts
        the year periods from the dataset name.

        Examples:
        >>> DaplaDatasetPathInfo._extract_period_strings(['p2022', 'kommune', 'v1'])
        ['2022']

        >>> DaplaDatasetPathInfo._extract_period_strings(['p2022-01', 'p2023-06', 'kommune', 'v1'])
        ['2022-01', '2023-06']

        >>> DaplaDatasetPathInfo._extract_period_strings(['p1990Q1', 'kommune', 'v1'])
        ['1990Q1']

        >>> DaplaDatasetPathInfo._extract_period_strings(['varehandel','v1']) # No date will return empty string
        []

        """
        date_format_regex = re.compile(
            r"^p\d{4}(?:-\d{2}-\d{2}|-\d{2}|-{0,1}[QTHWB]\d{1,2})?$",
        )

        return [
            x[1:]
            for x in dataset_name_sections
            if re.match(date_format_regex, x) is not None
        ]

    def _extract_period_string_from_index(self, index: int) -> str | None:
        try:
            return self._period_strings[index]
        except IndexError:
            return None

    @property
    def contains_data_from(self) -> datetime.date | None:
        """The earliest date from which data in the dataset is relevant for."""
        period_string = self._extract_period_string_from_index(0)
        if not period_string or (
            len(self._period_strings) > 1 and period_string > self._period_strings[1]
        ):
            return None
        date_format = categorize_period_string(period_string)
        return date_format.get_floor(period_string)

    @property
    def contains_data_until(self) -> datetime.date | None:
        """The latest date until which data in the dataset is relevant for."""
        first_period_string = self._extract_period_string_from_index(0)
        second_period_string = self._extract_period_string_from_index(1)
        period_string = second_period_string or first_period_string
        if not period_string or (
            second_period_string
            and first_period_string is not None
            and second_period_string < first_period_string
        ):
            return None
        date_format = categorize_period_string(period_string)
        return date_format.get_ceil(period_string)

    @property
    def dataset_state(
        self,
    ) -> DatasetState | None:
        """Extract the dataset state from the path.

        Examples:
        >>> DaplaDatasetPathInfo('klargjorte_data/person_data_v1.parquet').dataset_state
        <DatasetState.PROCESSED_DATA: 'PROCESSED_DATA'>
        >>> DaplaDatasetPathInfo('utdata/min_statistikk/person_data_v1.parquet').dataset_state
        <DatasetState.OUTPUT_DATA: 'OUTPUT_DATA'>
        >>> DaplaDatasetPathInfo('my_special_data/person_data_v1.parquet').dataset_state
        None
        """
        dataset_path_parts = set(self.dataset_path.parts)
        for s in DatasetState:
            # We assume that files are saved in the Norwegian language as specified by SSB.
            norwegian_dataset_state_path_part = s.get_value_for_language(
                SupportedLanguages.NORSK_BOKMÅL,
            ).lower()
            norwegian_dataset_state_path_part_variations = {
                norwegian_dataset_state_path_part.replace(" ", x) for x in ["-", "_"]
            }
            # Match on any of the variations anywhere in the path.
            if norwegian_dataset_state_path_part_variations.intersection(
                dataset_path_parts,
            ):
                return s

        return None

    @property
    def dataset_version(
        self,
    ) -> str | None:
        """Extract version information if exists in filename.

        Examples:
        >>> DaplaDatasetPathInfo('person_data_v1.parquet').dataset_version
        '1'
        >>> DaplaDatasetPathInfo('person_data_v20.parquet').dataset_version
        '20'
        >>> DaplaDatasetPathInfo('person_data.parquet').dataset_version
        None
        """
        minimum_elements_in_file_name: Final[int] = 2
        minimum_characters_in_version_string: Final[int] = 2
        if len(self.dataset_name_sections) >= minimum_elements_in_file_name:
            last_filename_element = str(self.dataset_name_sections[-1])
            if (
                len(last_filename_element) >= minimum_characters_in_version_string
                and last_filename_element[0:1] == "v"
                and last_filename_element[1:].isdigit()
            ):
                return last_filename_element[1:]
        return None
