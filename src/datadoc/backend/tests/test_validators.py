"""Tests for validators for DatadocMetadata class."""

from __future__ import annotations

import datetime
import re
import warnings
from typing import TYPE_CHECKING

import datadoc_model
import pytest
from datadoc_model import model
from pydantic import ValidationError

from datadoc import state
from datadoc.backend.src.constants import OBLIGATORY_METADATA_WARNING
from datadoc.backend.src.model_validation import ObligatoryDatasetWarning
from datadoc.backend.src.model_validation import ObligatoryVariableWarning
from datadoc.backend.src.utils import incorrect_date_order
from datadoc.enums import TemporalityTypeType

if TYPE_CHECKING:
    from datadoc.backend.src.core import Datadoc


@pytest.mark.parametrize(
    ("date_from", "date_until", "expected"),
    [
        (datetime.date(2024, 1, 1), datetime.date(1960, 1, 1), True),
        (datetime.date(1980, 1, 1), datetime.date(2000, 6, 5), False),
        (None, None, False),
        (datetime.date(2024, 1, 1), None, False),
        (None, datetime.date(2024, 1, 1), True),
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 1), False),
    ],
)
def test_incorrect_date_order(date_from, date_until, expected):
    result = incorrect_date_order(date_from, date_until)
    assert result == expected


@pytest.mark.parametrize(
    ("model_type", "date_from", "date_until", "raises_exception"),
    [
        ("dataset", datetime.date(2024, 1, 1), datetime.date(1980, 10, 1), True),
        ("dataset", datetime.date(1967, 1, 1), datetime.date(1980, 1, 1), False),
        ("variable", datetime.date(1999, 10, 5), datetime.date(1925, 3, 12), True),
        ("variable", datetime.date(2022, 7, 24), datetime.date(2023, 2, 19), False),
        ("dataset", datetime.date(1967, 1, 1), None, False),
        ("variable", datetime.date(1999, 2, 2), datetime.date(1999, 2, 2), False),
    ],
)
def test_write_metadata_document_validate_date_order(
    model_type,
    date_from,
    date_until,
    raises_exception,
    metadata: Datadoc,
):
    if model_type == "dataset":
        metadata.dataset.contains_data_from = date_from
        metadata.dataset.contains_data_until = date_until
    if model_type == "variable":
        for v in metadata.variables:
            v.contains_data_from = date_from
            v.contains_data_until = date_until
    if raises_exception:
        with pytest.raises(
            ValueError,
            match="contains_data_from must be the same or earlier date than contains_data_until",
        ):
            metadata.write_metadata_document()
    else:
        try:
            metadata.write_metadata_document()
        except ValidationError as exc:
            pytest.fail(str(exc))


def test_write_metadata_document_created_date(
    metadata: Datadoc,
):
    metadata.dataset.metadata_created_date = None
    metadata.write_metadata_document()
    assert metadata.dataset.metadata_created_date is not None


@pytest.mark.parametrize(
    ("variable_date", "date_from", "date_until"),
    [
        (None, datetime.date(1967, 1, 1), datetime.date(1980, 1, 1)),
        (
            datetime.date(2022, 2, 2),
            datetime.date(1999, 3, 3),
            datetime.date(2000, 1, 4),
        ),
    ],
)
def test_variables_inherit_dates(
    variable_date,
    date_from,
    date_until,
    metadata: Datadoc,
):
    state.metadata = metadata
    metadata.dataset.contains_data_from = date_from
    metadata.dataset.contains_data_until = date_until
    for v in metadata.variables:
        v.contains_data_from = variable_date
        v.contains_data_until = variable_date
    metadata.write_metadata_document()
    for v in metadata.variables:
        if variable_date is None:
            assert v.contains_data_from == metadata.dataset.contains_data_from
            assert v.contains_data_until == metadata.dataset.contains_data_until
        else:
            assert v.contains_data_from == variable_date
            assert v.contains_data_until == variable_date


def test_variables_inherit_temporality_type_value(metadata: Datadoc):
    assert all(v.temporality_type is None for v in metadata.variables)
    metadata.dataset.temporality_type = datadoc_model.model.TemporalityTypeType(
        TemporalityTypeType.FIXED.value,
    )
    metadata.write_metadata_document()
    assert all(
        v.temporality_type == metadata.dataset.temporality_type
        for v in metadata.variables
    )


def test_obligatory_metadata_dataset_warning(metadata: Datadoc):
    state.metadata = metadata
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    all_obligatory_completed = 100
    num_warnings = 2
    if metadata.percent_complete != all_obligatory_completed:
        assert len(record) == num_warnings
        assert issubclass(record[0].category, ObligatoryDatasetWarning)
        assert OBLIGATORY_METADATA_WARNING in str(
            record[0].message,
        )


def test_obligatory_metadata_variables_warning(metadata: Datadoc):
    state.metadata = metadata
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    all_obligatory_completed = 100
    if metadata.percent_complete != all_obligatory_completed and len(record) > 1:
        assert issubclass(record[1].category, ObligatoryVariableWarning)
        if (
            metadata.variables_lookup["pers_id"]
            and metadata.variables_lookup["pers_id"].name is None
        ):
            assert "[{'pers_id': ['name']}," in str(
                record[1].message,
            )


def test_obligatory_metadata_dataset_warning_name(metadata: Datadoc):
    state.metadata = metadata
    metadata.dataset.name = None
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    assert "name" in str(
        record[0].message,
    )
    # Set value 'name' for first time, a Language object is created
    metadata.dataset.name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Navnet"),
        ],
    )
    metadata.dataset.description = None
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record2:
        metadata.write_metadata_document()
    assert "name" not in str(record2[0].message)

    # Remove value for 'name', value for 'name' is no longer 'None', but 'languageText' is None
    metadata.dataset.name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
        ],
    )
    with pytest.warns(
        ObligatoryDatasetWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record3:
        metadata.write_metadata_document()
    assert "name" in str(record3[0].message)


def test_obligatory_metadata_dataset_warning_description(metadata: Datadoc):
    """Field name 'description' is a special case because it can match other field names like 'version_description'."""
    state.metadata = metadata
    error_message: str
    missing_obligatory_dataset = ""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            error_message = str(w[0].message)
    assert re.search(r"\bdescription\b", error_message)

    # Check that field name is removed from warning when value
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Beskrivelse"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)


def test_obligatory_metadata_dataset_warning_multiple_languages(
    metadata: Datadoc,
):
    state.metadata = metadata
    missing_obligatory_dataset = ""

    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Beskrivelse"),
            model.LanguageStringTypeItem(languageCode="en", languageText="Description"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)

    # Remove value for one language
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
            model.LanguageStringTypeItem(languageCode="en", languageText="Description"),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert not re.search(r"\bdescription\b", missing_obligatory_dataset)

    # Remove value for all languages
    metadata.dataset.description = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText=""),
            model.LanguageStringTypeItem(languageCode="en", languageText=""),
        ],
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_obligatory_dataset = str(w[0].message)
    assert re.search(r"\bdescription\b", missing_obligatory_dataset)


def test_obligatory_metadata_variables_warning_name(metadata: Datadoc):
    state.metadata = metadata
    variable_with_name = "{'pers_id': ['name']}"
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record:
        metadata.write_metadata_document()
    assert metadata.variables_lookup["pers_id"] is not None
    assert metadata.variables_lookup["pers_id"].name is None
    assert variable_with_name in str(record[1].message)

    metadata.variables_lookup["pers_id"].name = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="nb", languageText="Navnet"),
        ],
    )
    with pytest.warns(
        ObligatoryVariableWarning,
        match=OBLIGATORY_METADATA_WARNING,
    ) as record2:
        metadata.write_metadata_document()
    assert variable_with_name not in str(record2[1].message)
    assert "pers_id" not in str(record2[1].message)
