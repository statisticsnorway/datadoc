"""Tests for validators for DatadocMetadata class."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.datadoc_subclass import DatasetInherit
from datadoc.backend.utils import validate_date
from datadoc.backend.utils import validate_date_order

if TYPE_CHECKING:
    from datadoc.backend.core import Datadoc


def test_contains_data_until(metadata: Datadoc):
    state.metadata = metadata
    assert metadata.dataset.contains_data_until is None


@validate_date
def set_date(value):
    return value


@validate_date_order
def set_dates(value1, value2):
    date_from = value1
    date_until = value2
    return date_from, date_until


def test_validation():
    date2 = None
    with pytest.raises(ValueError, match="Date is null"):
        set_date(date2)


def test_validation2():
    date_from = datetime.date(2024, 1, 1)
    date_until = datetime.date(2022, 1, 1)
    with pytest.raises(
        ValueError,
        match="Date until must be equal or later than date from",
    ):
        set_dates(date_from, date_until)


def test_dataset_inherit():
    date_from = datetime.date(2024, 1, 1)
    date_until = datetime.date(2022, 1, 1)
    dataset = DatasetInherit()
    dataset.contains_data_from = date_from
    with pytest.raises(
        ValueError,
        match="contains_data_from must be the same or earlier date than contains_data_until",
    ):
        dataset.contains_data_until = date_until


def test_dataset_inherit2():
    date_from = datetime.date(2018, 1, 1)
    date_until = datetime.date(2022, 1, 1)
    dataset = DatasetInherit()
    dataset.contains_data_from = date_from
    dataset.contains_data_until = date_until
    assert dataset is not None
    assert dataset.contains_data_until == date_until


def test_write_metadata_document_invalid_date(
    metadata: Datadoc,
):
    metadata.dataset.contains_data_from = datetime.date(2024, 1, 1)
    metadata.dataset.contains_data_until = datetime.date(1980, 1, 1)
    with pytest.raises(
        ValueError,
        match="contains_data_from must be the same or earlier date than contains_data_until",
    ):
        metadata.write_metadata_document()


def test_write_metadata_document_valid_date(
    metadata: Datadoc,
):
    metadata.dataset.contains_data_from = datetime.date(1967, 1, 1)
    metadata.dataset.contains_data_until = datetime.date(1980, 1, 1)
    try:
        metadata.write_metadata_document()
    except ValidationError as exc:
        pytest.fail(str(exc))
