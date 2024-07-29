from __future__ import annotations

import datetime  # noqa: TCH003 import is needed in xdoctest
import logging
import pathlib
import uuid

from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from dapla import AuthClient
from datadoc_model import model

from datadoc.backend.constants import OBLIGATORY_DATASET_METADATA_IDENTIFIERS
from datadoc.backend.constants import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
)
from datadoc.backend.constants import OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS
from datadoc.backend.constants import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
)
from datadoc.enums import Assessment
from datadoc.enums import DataSetState
from datadoc.enums import VariableRole

logger = logging.getLogger(__name__)


def normalize_path(path: str) -> pathlib.Path | CloudPath:
    """Obtain a pathlib compatible Path.

    Obtains a pathlib compatible Path regardless of whether the file is on a filesystem or in GCS.

    Args:
        path: Path on a filesystem or in cloud storage.

    Returns:
        Pathlib compatible object.
    """
    if path.startswith(GSPath.cloud_prefix):
        client = GSClient(credentials=AuthClient.fetch_google_credentials())
        return GSPath(path, client=client)
    return pathlib.Path(path)


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer.

    Args:
        completed: The number of completed items.
        total: The total number of items.

    Returns:
        The rounded percentage of completed items out of the total.
    """
    return round((completed / total) * 100)


def derive_assessment_from_state(state: DataSetState) -> Assessment:
    """Derive assessment from dataset state.

    Args:
        state: The state of the dataset.

    Returns:
        The derived assessment of the dataset.
    """
    match (state):
        case (
            DataSetState.INPUT_DATA
            | DataSetState.PROCESSED_DATA
            | DataSetState.STATISTICS
        ):
            return Assessment.PROTECTED
        case DataSetState.OUTPUT_DATA:
            return Assessment.OPEN
        case DataSetState.SOURCE_DATA:
            return Assessment.SENSITIVE


def set_default_values_variables(variables: list) -> None:
    """Set default values on variables.

    Args:
        variables: A list of variable objects to set default values on.

    Example:
        >>> variables = [model.Variable(short_name="pers",id=None, is_personal_data = None), model.Variable(short_name="fnr",id='9662875c-c245-41de-b667-12ad2091a1ee', is_personal_data='PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA')]
        >>> set_default_values_variables(variables)
        >>> isinstance(variables[0].id, uuid.UUID)
        True

        >>> variables[1].is_personal_data == 'PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA'
        True

        >>> variables[0].is_personal_data == 'NOT_PERSONAL_DATA'
        True
    """
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = model.IsPersonalData.NOT_PERSONAL_DATA
        if v.variable_role is None:
            v.variable_role = VariableRole.MEASURE


def set_default_values_dataset(dataset: model.Dataset) -> None:
    """Set default values on dataset.

    Args:
        dataset: The dataset object to set default values on.

    Example:
        >>> dataset = model.Dataset(id=None, contains_personal_data=None)
        >>> set_default_values_dataset(dataset)
        >>> dataset.id is not None
        True

        >>> dataset.contains_personal_data == False
        True
    """
    if not dataset.id:
        dataset.id = uuid.uuid4()
    if dataset.contains_personal_data is None:
        dataset.contains_personal_data = False


def set_variables_inherit_from_dataset(
    dataset: model.Dataset,
    variables: list,
) -> None:
    """Set specific dataset values on a list of variable objects.

    This function populates 'data source', 'temporality type', 'contains data from',
    and 'contains data until' fields in each variable if they are not set (None).
    The values are inherited from the corresponding fields in the dataset.

    Args:
        dataset: The dataset object from which to inherit values.
        variables: A list of variable objects to update with dataset values.

    Example:
        >>> dataset = model.Dataset(short_name='person_data_v1',data_source='01',temporality_type='STATUS',id='9662875c-c245-41de-b667-12ad2091a1ee',contains_data_from="2010-09-05",contains_data_until="2022-09-05")
        >>> variables = [model.Variable(short_name="pers",data_source =None,temporality_type = None, contains_data_from = None,contains_data_until = None)]
        >>> set_variables_inherit_from_dataset(dataset, variables)
        >>> variables[0].data_source == dataset.data_source
        True

        >>> variables[0].temporality_type is None
        False

        >>> variables[0].contains_data_from == dataset.contains_data_from
        True

        >>> variables[0].contains_data_until == dataset.contains_data_until
        True
    """
    for v in variables:
        v.contains_data_from = v.contains_data_from or dataset.contains_data_from
        v.contains_data_until = v.contains_data_until or dataset.contains_data_until
        v.temporality_type = v.temporality_type or dataset.temporality_type
        v.data_source = v.data_source or dataset.data_source


def incorrect_date_order(
    date_from: datetime.date | None,
    date_until: datetime.date | None,
) -> bool:
    """Evaluate the chronological order of two dates.

    This function checks if 'date until' is earlier than 'date from'. If so, it
    indicates an incorrect date order.

    Args:
        date_from: The start date of the time period.
        date_until: The end date of the time period.

    Returns:
        True if 'date_until' is earlier than 'date_from' or if only 'date_from' is None, False otherwise.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True

        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False

        >>> incorrect_date_order(None, datetime.date(2024,7,1))
        True
    """
    if date_from is None and date_until is not None:
        return True
    return date_from is not None and date_until is not None and date_until < date_from


def _has_metadata_value(
    metadata: model.Dataset | model.Variable,
    obligatory_list: list,
    obligatory_multilanguage_list: list,
) -> list:
    """Return metadata fields with value.

    Args:
        metadata: The metadata object to check.
        obligatory_list: A list of obligatory fields.
        obligatory_multilanguage_list: A list of obligatory multilanguage fields,

    Returns:
        List of metadata fields that have values.
    """
    return [
        k
        for k, v in metadata.model_dump().items()
        if k in obligatory_list
        and v is not None
        or _has_multilanguage_value(
            k,
            v,
            obligatory_multilanguage_list,
            # OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]


def _has_dataset_metadata_value(
    metadata: model.Dataset,
    obligatory_list: list,
) -> list:
    """Return metadata fields with value.

    Args:
        metadata: The metadata object to check.
        obligatory_list: A list of obligatory fields.

    Returns:
        List of metadata fields that have values.
    """
    return [
        k
        for k, v in metadata.model_dump().items()
        if k in obligatory_list
        and v is not None
        or _has_multilanguage_value(
            k,
            v,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]


def num_obligatory_dataset_fields_completed(dataset: model.Dataset) -> int:
    """Count the number of obligatory dataset fields completed for each variable.

    This function returns the total count of obligatory fields in the dataset that
    have values (are not None).

    Args:
        dataset: The dataset object for which to count the fields.

    Returns:
        The number of obligatory dataset fields that have been completed (not None).
    """
    return len(
        _has_dataset_metadata_value(dataset, OBLIGATORY_DATASET_METADATA_IDENTIFIERS),
    )


def num_obligatory_variable_fields_completed(variable: model.Variable) -> int:
    """Count the number of obligatory fields completed for one variable.

    This function calculates the total number of obligatory fields that have
    values (are not None) for one variable in the list.

    Args:
        variable: The variable to count obligatory fields for.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) for one variable.
    """
    return len(
        _has_metadata_value(
            variable,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
        ),
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Count the number of obligatory fields completed for all variables.

    This function calculates the total number of obligatory fields that have
    values (are not None) for all variables in the list.

    Args:
        variables: A list of variable objects to count obligatory fields for.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) across all variables.
    """
    num_variables = 0
    for variable in variables:
        num_variables += len(
            _has_metadata_value(
                variable,
                OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
                OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
            ),
        )
    return num_variables


def num_variables_obligatory_fields(variables: list) -> int:
    """."""
    num_fields = 0
    for _i in range(len(variables)):
        num_fields += len(OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS)
    logger.info("Prosent issue: %s", num_fields)
    return num_fields


def _is_missing_metadata(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint because method '_is_missing_multilanguage_value'
    obligatory_list: list,
    obligatory_multi_language_list: list,
) -> bool:
    """Check obligatory fields without value.

    Args:
        field_name: The field name.
        field_value: The field value. Can be of type str, or LanguageStringType for
            multilanguage fields.
        obligatory_list: List of obligatory fields.
        obligatory_multi_language_list: List of obligatory fields with multilanguage
            values.

    Returns:
        True if field doesn't have value, False otherwise.
    """
    if (
        field_name in obligatory_list
        and field_value is None
        or _is_missing_multilanguage_value(
            field_name,
            field_value,
            obligatory_multi_language_list,
        )
    ):
        return True
    return False


def _is_missing_multilanguage_value(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint to enable dynamically handling value for LanguageStringType not indexable
    obligatory_list: list,
) -> bool:
    """Check obligatory fields with multilanguage value.

    Args:
        field_name: The field name.
        field_value: The field value. LanguageStringType.
        obligatory_list: List of obligatory fields with multilanguage values.

    Returns:
        True if no value in any of languages for one field, False otherwise.
    """
    if (
        field_name in obligatory_list
        and field_value
        and (
            len(field_value[0]) > 0
            and not field_value[0]["languageText"]
            and (len(field_value) <= 1 or not field_value[1]["languageText"])
            and (
                len(field_value) <= 2  # noqa: PLR2004 approve magic value
                or not field_value[2]["languageText"]
            )
        )
    ):
        return True
    return False


def _has_multilanguage_value(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint to enable dynamically handling value for LanguageStringType not indexable
    obligatory_list: list,
) -> bool:
    """Check obligatory fields with multilanguage value.

    Args:
        field_name: The field name.
        field_value: The field value. LanguageStringType.
        obligatory_list: List of obligatory fields with multilanguage values.

    Returns:
        True if no value in any of languages for one field, False otherwise.
    """
    if (
        field_name in obligatory_list
        and field_value
        and (
            len(field_value[0]) > 0
            and field_value[0]["languageText"]
            or (len(field_value) == 1 and field_value[1]["languageText"])
            or (
                len(field_value) == 2  # noqa: PLR2004 approve magic value
                and field_value[2]["languageText"]
            )
        )
    ):
        return True
    return False


def get_missing_obligatory_dataset_fields(dataset: model.Dataset) -> list:
    """Identify all obligatory dataset fields that are missing values.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        dataset: The dataset object to examine. This object must support the
            `model_dump()` method which returns a dictionary of field names and
            values.

    Returns:
        A list of field names (as strings) that are missing values. This includes:
            - Fields that are directly `None` and are listed as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata`) where
            the value exists but the primary language text is empty.
    """
    return [
        key
        for key, value in dataset.model_dump().items()
        if _is_missing_metadata(
            key,
            value,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]


def get_missing_obligatory_variables_fields(variables: list) -> list[dict]:
    """Identify obligatory variable fields that are missing values for each variable.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        variables: A list of variable objects to check for missing obligatory fields.

    Returns:
        A list of dictionaries with variable short names as keys and list of missing
        obligatory variable fields as values. This includes:
            - Fields that are directly `None` and are llisted as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata) where the value
            exists but the primary language text is empty.
    """
    missing_variables_fields = [
        {
            variable.short_name: [
                key
                for key, value in variable.model_dump().items()
                if _is_missing_metadata(
                    key,
                    value,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
                )
            ],
        }
        for variable in variables
    ]
    # Filtering out variable keys with empty values list
    return [item for item in missing_variables_fields if next(iter(item.values()))]
