"""Tests for validators for DatadocMetadata class."""

from __future__ import annotations

import datetime
import json
import pathlib
from typing import TYPE_CHECKING

import datadoc_model
import pytest
from datadoc_model.model import Dataset
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.datadoc_subclass import ValidationWarning
from datadoc.enums import TemporalityTypeType
from tests.utils import TEST_EXISTING_METADATA_FILE_NAME

if TYPE_CHECKING:
    from datadoc.backend.core import Datadoc


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


def test_write_metadata_document_created_date_is_none(
    metadata: Datadoc,
):
    assert metadata.dataset.metadata_created_date is None
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date is not None


def test_write_metadata_document_created_date_is_set(
    metadata: Datadoc,
):
    metadata.dataset.metadata_created_date = datetime.datetime(
        2022,
        1,
        1,
        tzinfo=datetime.timezone.utc,
    )
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date == datetime.datetime(
        2022,
        1,
        1,
        tzinfo=datetime.timezone.utc,
    )


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


def test_temporality_type_value(metadata: Datadoc):
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


def test_value(metadata: Datadoc, tmp_path: pathlib.Path):
    assert all(v.temporality_type is None for v in metadata.variables)
    metadata.dataset.temporality_type = datadoc_model.model.TemporalityTypeType(
        TemporalityTypeType.FIXED.value,
    )
    assert metadata.dataset.temporality_type is not None
    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME
    assert pathlib.Path.exists(written_document)
    with pathlib.Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["dataset"]
    assert (
        # Use our pydantic model to read in the datetime string so we get the correct format
        Dataset(
            temporality_type=datadoc_metadata["temporality_type"],
        ).temporality_type
        == TemporalityTypeType.FIXED.value
    )


# TODO(@tilen1976): In progress  # noqa: TD003
def test_obligatory_metadata_warning(metadata: Datadoc):
    state.metadata = metadata
    with pytest.warns(
        ValidationWarning,
        match="All obligatory metadata is not filled in",
    ) as record:
        metadata.write_metadata_document()
    assert metadata.percent_complete != 100  # noqa: PLR2004
    assert len(record) == 2  # noqa: PLR2004
    assert issubclass(record[0].category, ValidationWarning)
    assert "All obligatory metadata is not filled in for variables" in str(
        record[1].message,
    )
