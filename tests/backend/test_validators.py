"""Tests for validators for DatadocMetadata class."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import datadoc_model
import pytest
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.datadoc_subclass import ValidationWarning
from datadoc.backend.utils import incorrect_date_order
from datadoc.enums import TemporalityTypeType

if TYPE_CHECKING:
    from datadoc.backend.core import Datadoc


def test_incorrect_date_order(metadata: Datadoc):
    variables = metadata.variables
    dataset = metadata.dataset
    assert variables is not None
    variables[0].contains_data_from = datetime.date(2024, 1, 1)
    variables[0].contains_data_until = datetime.date(1960, 1, 1)
    result_incorrect_dates = incorrect_date_order(
        variables[0].contains_data_from,
        variables[0].contains_data_until,
    )
    assert result_incorrect_dates is True
    dataset.contains_data_from = datetime.date(1980, 1, 1)
    dataset.contains_data_until = datetime.date(2000, 6, 5)
    result_correct_dates = incorrect_date_order(
        dataset.contains_data_from,
        dataset.contains_data_until,
    )
    assert result_correct_dates is False


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


def test_write_metadata_document_invalid_date_variables(
    metadata: Datadoc,
):
    for v in metadata.variables:
        v.contains_data_from = datetime.date(2024, 1, 1)
        v.contains_data_until = datetime.date(1980, 1, 1)
    assert all(v.contains_data_from is not None for v in metadata.variables)
    assert all(v.contains_data_until is not None for v in metadata.variables)
    with pytest.raises(
        ValueError,
        match="contains_data_from must be the same or earlier date than contains_data_until",
    ):
        metadata.write_metadata_document()


def test_write_metadata_document_variables_valid_date(
    metadata: Datadoc,
):
    metadata.variables_lookup["pers_id"].contains_data_from = datetime.date(1967, 1, 1)
    metadata.variables_lookup["pers_id"].contains_data_until = datetime.date(1980, 1, 1)
    try:
        metadata.write_metadata_document()
    except ValidationError as exc:
        pytest.fail(str(exc))


def test_write_metadata_document_created_date(
    metadata: Datadoc,
):
    assert metadata.dataset.metadata_created_date is None
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date is not None


# TODO(@tilen1976): remove??  # noqa: TD003
"""def test_write_metadata_document_created_date_is_set(
    metadata: Datadoc,
):
    created_date = datetime.datetime(
        2022,
        1,
        1,
        tzinfo=datetime.timezone.utc,
    )
    metadata.dataset.metadata_created_date = created_date
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date == created_date
"""


def test_variables_inherit_dates(
    metadata: Datadoc,
):
    state.metadata = metadata
    metadata.dataset.contains_data_from = datetime.date(1967, 1, 1)
    metadata.dataset.contains_data_until = datetime.date(1980, 1, 1)
    for v in metadata.variables:
        assert v.contains_data_from is None
        assert v.contains_data_until is None
    metadata.write_metadata_document()
    for v in metadata.variables:
        assert v.contains_data_from == metadata.dataset.contains_data_from
        assert v.contains_data_until == metadata.dataset.contains_data_until


def test_variables_inherit_temporality_type_value(metadata: Datadoc):
    assert all(v.temporality_type is None for v in metadata.variables)
    metadata.dataset.temporality_type = datadoc_model.model.TemporalityTypeType(
        TemporalityTypeType.FIXED.value,
    )
    assert metadata.dataset.temporality_type is not None
    metadata.write_metadata_document()
    assert all(
        v.temporality_type == metadata.dataset.temporality_type
        for v in metadata.variables
    )


def test_obligatory_metadata_warning(metadata: Datadoc):
    state.metadata = metadata
    with pytest.warns(
        ValidationWarning,
        match="All obligatory metadata is not filled in",
    ) as record:
        metadata.write_metadata_document()
    all_obligatory_completed = 100
    num_warnings = 2
    if metadata.percent_complete != all_obligatory_completed:
        assert len(record) == num_warnings
        assert issubclass(record[0].category, ValidationWarning)
        if metadata.variables_lookup["pers_id"]:
            assert (
                "All obligatory metadata is not filled in for variables [{'pers_id': ['name']},"
                in str(
                    record[1].message,
                )
            )