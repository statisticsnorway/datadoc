"""Tests for the callbacks package."""

from __future__ import annotations

import datetime
import random
from copy import deepcopy
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

import pytest
from datadoc_model import model
from pydantic_core import Url

from datadoc import enums
from datadoc import state
from datadoc.enums import DataType
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.variables import (
    accept_variable_datatable_metadata_input,
)
from datadoc.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc.frontend.callbacks.variables import (
    update_variable_table_dropdown_options_for_language,
)
from datadoc.frontend.callbacks.variables import update_variable_table_language
from datadoc.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata

DATA_ORIGINAL = [
    {
        "short_name": "pers_id",
        "variable_role": None,
    },
]
DATA_VALID = [
    {
        "short_name": "pers_id",
        "variable_role": "IDENTIFIER",
    },
]
DATA_NONETYPE = [
    {"short_name": "pers_id", "variable_role": "IDENTIFIER", "name": None},
]
DATA_INVALID = [
    {
        "short_name": "pers_id",
        "variable_role": 3.1415,
    },
]
DATA_CLEAR_URI = [
    {"short_name": "pers_id", "variable_role": None, "definition_uri": ""},
]


@pytest.fixture()
def active_cell() -> dict[str, MetadataInputTypes]:
    return {"row": 1, "column": 1, "column_id": "short_name", "row_id": None}


def test_accept_variable_table_metadata_input_no_change_in_data(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = metadata
    output = accept_variable_datatable_metadata_input(
        DATA_ORIGINAL,
        active_cell,
        DATA_ORIGINAL,
    )
    assert output[0] == DATA_ORIGINAL
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_table_metadata_input_new_data(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = metadata
    output = accept_variable_datatable_metadata_input(
        DATA_VALID,
        active_cell,
        DATA_ORIGINAL,
    )

    assert state.metadata.variables_lookup["pers_id"].variable_role == "IDENTIFIER"
    assert output[0] == DATA_VALID
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_table_metadata_clear_string(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = metadata
    output = accept_variable_datatable_metadata_input(
        DATA_CLEAR_URI,
        active_cell,
        DATA_ORIGINAL,
    )

    assert state.metadata.variables_lookup["pers_id"].definition_uri is None
    assert output[0] == DATA_CLEAR_URI
    assert output[1] is False
    assert output[2] == ""


def test_accept_variable_table_metadata_input_incorrect_data_type(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
):
    state.metadata = metadata
    previous_metadata = deepcopy(state.metadata.variables)
    output = accept_variable_datatable_metadata_input(
        DATA_INVALID,
        active_cell,
        DATA_ORIGINAL,
    )

    assert output[0] == DATA_ORIGINAL
    assert output[1] is True
    assert "validation error for Variable" in output[2]
    assert state.metadata.variables == previous_metadata


def test_find_existing_language_string_pre_existing_strings(
    english_name: str,
    bokmål_name: str,
    nynorsk_name: str,
    language_object: model.LanguageStringType,
):
    dataset_metadata = model.Dataset()
    dataset_metadata.name = language_object
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    language_strings = find_existing_language_string(
        dataset_metadata,
        nynorsk_name,
        "name",
    )
    assert language_strings == model.LanguageStringType(
        nb=bokmål_name,
        en=english_name,
        nn=nynorsk_name,
    )


def test_update_variable_table_language(
    metadata: DataDocMetadata,
    bokmål_name: str,
    language_object: model.LanguageStringType,
):
    state.metadata = metadata
    test_variable = random.choice(  # noqa: S311 not for cryptographic purposes
        [v.short_name for v in state.metadata.variables],
    )
    state.metadata.variables_lookup[test_variable].name = language_object
    output = update_variable_table_language(
        SupportedLanguages.NORSK_BOKMÅL,
    )
    try:
        name = next(
            d[VariableIdentifiers.NAME.value]
            for d in output[0]
            if d[VariableIdentifiers.SHORT_NAME.value] == test_variable
        )
    except StopIteration as e:
        msg = f"Could not find name for {test_variable = } in {output = }"
        raise AssertionError(msg) from e
    assert name == bokmål_name


def test_nonetype_value_for_language_string(
    metadata: DataDocMetadata,
    active_cell: dict[str, MetadataInputTypes],
    language_object: model.LanguageStringType,
):
    state.metadata = metadata
    state.metadata.variables_lookup["pers_id"].name = language_object
    state.current_metadata_language = SupportedLanguages.NORSK_NYNORSK
    accept_variable_datatable_metadata_input(DATA_NONETYPE, active_cell, DATA_ORIGINAL)

    assert state.metadata.variables_lookup["pers_id"].name == language_object


def test_update_variable_table_dropdown_options_for_language():
    options = update_variable_table_dropdown_options_for_language(
        SupportedLanguages.NORSK_BOKMÅL,
    )
    assert all(k in model.Variable.model_fields for k in options)
    assert all(list(v.keys()) == ["options"] for v in options.values())
    try:
        assert all(
            list(d.keys()) == ["label", "value"]
            for v in options.values()
            for d in next(iter(v.values()))
        )
    except StopIteration as e:
        msg = f"Could not extract actual value from {options.values() = }"
        raise AssertionError(msg) from e
    assert [d["label"] for d in options["data_type"]["options"]] == [
        i.get_value_for_language(SupportedLanguages.NORSK_BOKMÅL) for i in DataType
    ]


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            VariableIdentifiers.NAME,
            "Variable name",
            enums.LanguageStringType(nb="Variable name"),
        ),
        (
            VariableIdentifiers.DATA_TYPE,
            enums.DataType.STRING,
            enums.DataType.STRING.value,
        ),
        (
            VariableIdentifiers.VARIABLE_ROLE,
            enums.VariableRole.MEASURE,
            enums.VariableRole.MEASURE.value,
        ),
        (
            VariableIdentifiers.DEFINITION_URI,
            "https://www.example.com",
            Url("https://www.example.com"),
        ),
        (
            VariableIdentifiers.DIRECT_PERSON_IDENTIFYING,
            True,
            True,
        ),
        (
            VariableIdentifiers.DATA_SOURCE,
            "Atlantis",
            enums.LanguageStringType(nb="Atlantis"),
        ),
        (
            VariableIdentifiers.POPULATION_DESCRIPTION,
            "Population description",
            enums.LanguageStringType(nb="Population description"),
        ),
        (
            VariableIdentifiers.COMMENT,
            "Comment",
            enums.LanguageStringType(nb="Comment"),
        ),
        (
            VariableIdentifiers.TEMPORALITY_TYPE,
            enums.TemporalityTypeType.ACCUMULATED,
            enums.TemporalityTypeType.ACCUMULATED.value,
        ),
        (
            VariableIdentifiers.MEASUREMENT_UNIT,
            "Kilograms",
            "Kilograms",
        ),
        (
            VariableIdentifiers.FORMAT,
            "Regex",
            "Regex",
        ),
        (
            VariableIdentifiers.CLASSIFICATION_URI,
            "https://www.example.com",
            Url("https://www.example.com"),
        ),
        (
            VariableIdentifiers.SENTINEL_VALUE_URI,
            "https://www.example.com",
            Url("https://www.example.com"),
        ),
        (
            VariableIdentifiers.INVALID_VALUE_DESCRIPTION,
            "Invalid value",
            enums.LanguageStringType(nb="Invalid value"),
        ),
        (
            VariableIdentifiers.IDENTIFIER,
            "2f72477a-f051-43ee-bf8b-0d8f47b5e0a7",
            UUID("2f72477a-f051-43ee-bf8b-0d8f47b5e0a7"),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_FROM,
            "2024-02-28",
            datetime.datetime(2024, 2, 28, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_UNTIL,
            "2024-02-28",
            datetime.datetime(2024, 2, 28, 0, 0, tzinfo=datetime.timezone.utc),
        ),
    ],
)
def test_accept_variable_metadata_input_valid(
    metadata: DataDocMetadata,
    metadata_field: VariableIdentifiers,
    value: MetadataInputTypes,
    expected_model_value: Any,  # noqa: ANN401
):
    state.metadata = metadata
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    assert (
        accept_variable_metadata_input(
            value,
            metadata.variables[0].short_name,
            metadata_field=metadata_field.value,
        )
        is None
    )
    assert (
        getattr(state.metadata.variables[0], metadata_field.value)
        == expected_model_value
    )


def test_accept_variable_metadata_input_invalid(
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    message = accept_variable_metadata_input(
        "not a url",
        metadata.variables[0].short_name,
        metadata_field=VariableIdentifiers.DEFINITION_URI.value,
    )
    assert message is not None
    assert "validation error for Variable" in message
