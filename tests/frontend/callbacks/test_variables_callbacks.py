"""Tests for the variables callbacks module."""

from __future__ import annotations

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
from datadoc.frontend.callbacks.variables import (
    set_variables_values_inherited_from_dataset,
)
from datadoc.frontend.fields.display_base import get_standard_metadata
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.frontend.text import INVALID_DATE_ORDER
from datadoc.frontend.text import INVALID_VALUE

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
            "Atlantis",
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
    assert message == INVALID_VALUE


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
                INVALID_DATE_ORDER.format(
                    contains_data_from_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_FROM
                    ].display_name,
                    contains_data_until_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_UNTIL
                    ].display_name,
                ),
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
                INVALID_DATE_ORDER.format(
                    contains_data_from_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_FROM
                    ].display_name,
                    contains_data_until_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_UNTIL
                    ].display_name,
                ),
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
        arrow.get(preset_value).date(),
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
        assert (
            metadata.variables[0].contains_data_from
            == arrow.get(
                contains_data_from,
            ).date()
        )
    if not expected_result[2]:
        assert (
            metadata.variables[0].contains_data_until
            == arrow.get(
                contains_data_until,
            ).date()
        )


@pytest.mark.usefixtures("_code_list_fake_classifications_variables")
@pytest.mark.parametrize(
    ("search_query", "expected_length"),
    [
        (
            "",
            8,
        ),
        (
            "a",
            4,
        ),
        (
            "pers_id",
            1,
        ),
    ],
)
def test_populate_variables_workspace_filter_variables(
    search_query: str,
    expected_length: int,
    metadata: DataDocMetadata,
):
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


def test_update_variables_values_from_dataset_values(metadata: DataDocMetadata):
    state.metadata = metadata
    dataset_temporality_type = "FIXED"
    dataset_data_source = None
    setattr(
        state.metadata.dataset,
        DatasetIdentifiers.TEMPORALITY_TYPE,
        dataset_temporality_type,
    )
    setattr(
        state.metadata.dataset,
        DatasetIdentifiers.DATA_SOURCE,
        dataset_data_source,
    )
    set_variables_values_inherited_from_dataset(
        dataset_temporality_type,
        DatasetIdentifiers.TEMPORALITY_TYPE,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.temporality_type == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.TEMPORALITY_TYPE.value,
        )
    set_variables_values_inherited_from_dataset(
        dataset_data_source,
        DatasetIdentifiers.DATA_SOURCE,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.data_source == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.DATA_SOURCE.value,
        )


def test_variables_value_can_be_changed_after_update_from_dataset_value(
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    dataset_temporality_type = "FIXED"
    setattr(
        state.metadata.dataset,
        DatasetIdentifiers.TEMPORALITY_TYPE,
        dataset_temporality_type,
    )
    set_variables_values_inherited_from_dataset(
        dataset_temporality_type,
        DatasetIdentifiers.TEMPORALITY_TYPE,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.temporality_type == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.TEMPORALITY_TYPE.value,
        )
    setattr(
        state.metadata.variables_lookup["pers_id"],
        VariableIdentifiers.TEMPORALITY_TYPE,
        enums.TemporalityTypeType.ACCUMULATED,
    )
    assert dataset_temporality_type == get_standard_metadata(
        metadata.variables_lookup["sivilstand"],
        VariableIdentifiers.TEMPORALITY_TYPE.value,
    )
    assert dataset_temporality_type != get_standard_metadata(
        metadata.variables_lookup["pers_id"],
        VariableIdentifiers.TEMPORALITY_TYPE.value,
    )
    assert (
        get_standard_metadata(
            metadata.variables_lookup["pers_id"],
            VariableIdentifiers.TEMPORALITY_TYPE.value,
        )
        == "ACCUMULATED"
    )
