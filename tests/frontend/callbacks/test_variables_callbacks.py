"""Tests for the variables callbacks module."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

import arrow
import pytest
from pydantic_core import Url

from datadoc import enums
from datadoc import state
from datadoc.frontend.callbacks.variables import accept_variable_metadata_date_input
from datadoc.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc.frontend.callbacks.variables import populate_variables_workspace
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from tests.backend.test_code_list import CODE_LIST_DIR
from tests.utils import TEST_RESOURCES_DIRECTORY

if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata
    from datadoc.frontend.callbacks.utils import MetadataInputTypes


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            VariableIdentifiers.NAME,
            "Variable name",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Variable name",
                    ),
                ],
            ),
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
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Atlantis",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.POPULATION_DESCRIPTION,
            "Population description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Population description",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.COMMENT,
            "Comment",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Comment",
                    ),
                ],
            ),
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
            VariableIdentifiers.INVALID_VALUE_DESCRIPTION,
            "Invalid value",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Invalid value",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.IDENTIFIER,
            "2f72477a-f051-43ee-bf8b-0d8f47b5e0a7",
            UUID("2f72477a-f051-43ee-bf8b-0d8f47b5e0a7"),
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
    assert (
        accept_variable_metadata_input(
            value,
            metadata.variables[0].short_name,
            metadata_field=metadata_field.value,
            language="nb",
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


@pytest.mark.parametrize(
    (
        "variable_identifier",
        "contains_data_from",
        "contains_data_until",
        "expected_result",
    ),
    [
        (
            VariableIdentifiers.CONTAINS_DATA_FROM.value,
            "1950-01-01",
            "2020-01-01",
            (False, "", False, ""),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_FROM.value,
            "2020-01-01",
            "1950-01-01",
            (
                True,
                "Validation error: contains_data_from must be the same or earlier date than contains_data_until",
                False,
                "",
            ),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            "1950-01-01",
            "2020-01-01",
            (False, "", False, ""),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            "2020-01-01",
            "1950-01-01",
            (
                False,
                "",
                True,
                "Validation error: contains_data_from must be the same or earlier date than contains_data_until",
            ),
        ),
    ],
)
def test_accept_variable_metadata_date_input(
    variable_identifier,
    contains_data_from: str,
    contains_data_until: str,
    expected_result: tuple[bool, str, bool, str],
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    chosen_short_name = metadata.variables[0].short_name
    preset_identifier = (
        VariableIdentifiers.CONTAINS_DATA_UNTIL.value
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM.value
        else VariableIdentifiers.CONTAINS_DATA_FROM.value
    )
    preset_value = (
        contains_data_until
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM.value
        else contains_data_from
    )
    setattr(
        state.metadata.variables_lookup[chosen_short_name],
        preset_identifier,
        arrow.get(preset_value).astimezone(tz=datetime.timezone.utc),
    )
    assert (
        accept_variable_metadata_date_input(
            VariableIdentifiers(variable_identifier),
            chosen_short_name,
            contains_data_from,
            contains_data_until,
        )
        == expected_result
    )
    if not expected_result[0]:
        assert metadata.variables[0].contains_data_from == arrow.get(
            contains_data_from,
        ).to("utc")
    if not expected_result[2]:
        assert metadata.variables[0].contains_data_until == arrow.get(
            contains_data_until,
        ).to("utc")


@pytest.mark.parametrize(
    ("search_query", "expected_length", "code_list_csv_filepath_nb"),
    [
        (
            "",
            8,
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
        (
            "a",
            4,
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
        (
            "pers_id",
            1,
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_measurement_unit.csv",
        ),
    ],
)
def test_populate_variables_workspace_filter_variables(
    search_query: str,
    expected_length: int,
    metadata: DataDocMetadata,
    code_list_fake_structure,
):
    state.measurement_units = code_list_fake_structure
    state.measurement_units.wait_for_external_result()
    assert (
        len(
            populate_variables_workspace(
                metadata.variables,
                search_query,
                0,
            ),
        )
        == expected_length
    )
