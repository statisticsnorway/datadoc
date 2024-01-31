"""Extract info from a path following SSB's dataset naming convention."""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Literal

import arrow

if TYPE_CHECKING:
    import datetime
    import os


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
    regex_pattern=r"^\d{4}\-{0,1}W\d{2}$",
    arrow_pattern="W",
    timeframe="week",
)


@dataclass
class SsbDateFormat:
    """An date format with relevant patterns for SSB special date formats."""

    name: str
    regex_pattern: str
    arrow_pattern: str
    time_frame: dict


SSB_BIMESTER = SsbDateFormat(
    name="SSB_BIMESTER",
    regex_pattern=r"\d{4}[B]\d{1}$",
    arrow_pattern="YYYYMM",
    time_frame={
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
    time_frame={
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
    time_frame={
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
    time_frame={
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
    >>> date_format = categorize_period_string('2022')
    >>> date_format.name
    ISO_YEAR

    >>> date_format = categorize_period_string('2022-W01')
    >>> date_format.name
    ISO_YEAR_WEEK

    >>> date_format = categorize_period_string('2022B1')
    >>> date_format.name
    SSB_BIMESTER

    >>> date_format = categorize_period_string('1980Q3')
    >>> date_format.name
    SSB_QUARTERLY

    >>> date_format = categorize_period_string('1954T2')
    >>> date_format.name
    SSB_TRIANNUAL

    >>> date_format = categorize_period_string('1876H1')
    >>> date_format.name
    SSB_HALF_YEAR

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


def convert_ssb_period(
    period_string: str,
    period_type: str,
    date_format: SsbDateFormat,
) -> str:
    """Convert ssb-format for bimester, quarterly, triannual and half year to start and end months.

    Usage-examples:
    >>> ssb_bimester_period_start = convert_ssb_period("2022B1","start",SSB_BIMESTER)
    >>> ssb_bimester_period_start
    202201

    >>> ssb_bimester_period_end = convert_ssb_period("2022B1","end",SSB_BIMESTER)
    >>> ssb_bimester_period_end
    202202

    >>> ssb_quarterly_period_start = convert_ssb_period("2015Q3","start",SSB_QUARTERLY)
    >>> ssb_quarterly_period_start
    201507

    >>> ssb_quarterly_period_end = convert_ssb_period("2015Q3","end",SSB_QUARTERLY)
    >>> ssb_quarterly_period_end
    201509

    >>> ssb_triannual_period_start = convert_ssb_period("1998T2","start",SSB_TRIANNUAL)
    >>> ssb_triannual_period_start
    199805

    >>> ssb_quarterly_period_end = convert_ssb_period("1998T2","end",SSB_TRIANNUAL)
    >>> ssb_quarterly_period_end
    199808

    >>> ssb_half_year_period_start = convert_ssb_period("1898H2","start",SSB_HALF_YEAR)
    >>> ssb_half_year_period_start
    189807

    >>> ssb_half_year_period_end = convert_ssb_period("1898H2","end",SSB_HALF_YEAR)
    >>> ssb_half_year_period_end
    189812

    """
    return period_string[:4] + date_format.time_frame[period_string[-2:]][period_type]


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
        first_period_string = self._extract_period_string_from_index(0)
        if first_period_string is not None:
            date_format = categorize_period_string(first_period_string)
            if isinstance(date_format, SsbDateFormat):
                """If dateformat is SSB date format return start month of ssb period."""
                period = convert_ssb_period(
                    first_period_string,
                    "start",
                    date_format,
                )
                return (
                    arrow.get(period, date_format.arrow_pattern).floor("month").date()
                )

            return (
                arrow.get(first_period_string, date_format.arrow_pattern)
                .floor(date_format.timeframe)
                .date()
            )
        return None

    @property
    def contains_data_until(self) -> datetime.date | None:
        """The latest date until which data in the dataset is relevant for."""
        first_period_string = self._extract_period_string_from_index(0)
        second_period_string = self._extract_period_string_from_index(1)
        period_string = second_period_string or first_period_string
        if period_string is not None:
            date_format = categorize_period_string(period_string)
            if isinstance(date_format, SsbDateFormat):
                """If dateformat is SSB date format return end month of ssb period."""
                period = convert_ssb_period(period_string, "end", date_format)
                return arrow.get(period, date_format.arrow_pattern).ceil("month").date()
            return (
                arrow.get(period_string, date_format.arrow_pattern)
                .ceil(date_format.timeframe)
                .date()
            )
        return None
