from __future__ import annotations

import datetime  # noqa: TCH003 import is needed in xdoctest
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


def normalize_path(path: str) -> pathlib.Path | CloudPath:
    """Obtain a pathlib compatible Path regardless of whether the file is on a filesystem or in GCS.

    Args:
        path (str): Path on a filesystem or in cloud storage

    Returns:
        pathlib.Path | CloudPath: Pathlib compatible object
    """
    if path.startswith(GSPath.cloud_prefix):
        client = GSClient(credentials=AuthClient.fetch_google_credentials())
        return GSPath(path, client=client)
    return pathlib.Path(path)


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer."""
    return round((completed / total) * 100)


def derive_assessment_from_state(state: DataSetState) -> Assessment:
    """Derive assessment from dataset state.

    Args:
        state (DataSetState): The state of the dataset.

    Returns:
        Assessment: The derived assessment of the dataset.
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
    """Set default values on variables for variable fields 'id' and 'is personal data'.

    This function assigns default values to the 'id' and 'is personal data' fields of each variable.
    If a variable's 'id' is None, it will be set to a new UUID. If 'is personal data' is None,
    it will be set to NOT_PERSONAL_DATA.

    Args:
        variables (list): A list of variable objects to set default values on.

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


def set_default_values_dataset(dataset: model.Dataset) -> None:
    """Set default values on dataset for dataset fields 'id' and 'contains personal data'.

    This function assigns default values to the 'id' and 'contains personal data' fields of the dataset.
    If the dataset's 'id' is None, it will be set to a new UUID. If 'contains personal data' is None,
    it will be set to False.

    Args:
        dataset (model.Dataset): The dataset object to set default values on.

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

    This function populates 'data source', 'temporality type', 'contains data from', and
    'contains data until' fields in each variable if they are not set (None). The values
    are inherited from the corresponding fields in the dataset.

    Args:
        dataset (model.Dataset): The dataset object from which to inherit values.
        variables (list): A list of variable objects to update with dataset values.


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

    This function checks if 'date until' is earlier than 'date from'. If so, it indicates
    an incorrect date order.

    Args:
        date_from (datetime.date | None): The start date of the time period.
        date_until (datetime.date | None): The end date of the time period.

    Returns:
        bool: True if 'date until' is earlier than 'date from'; False otherwise.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True

        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False
    """
    return date_from is not None and date_until is not None and date_until < date_from


def num_obligatory_dataset_fields_completed(dataset: model.Dataset) -> int:
    """Count the number of obligatory dataset fields that have values.

    This function returns the total count of obligatory fields in the dataset that are not None.

    Args:
        dataset (model.Dataset): The dataset object for which to count the fields.

    Returns:
        int: The number of obligatory dataset fields that have been completed (not None).
    """
    return len(
        [
            k
            for k, v in dataset.model_dump().items()
            if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is not None
        ],
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Count the number of obligatory fields completed for each variable.

    This function calculates the total number of obligatory fields that have values
    for each variable in the list.

    Args:
        variables (list): A list of variable objects to count obligatory fields for.

    Returns:
        int: The total number of obligatory variable fields that have been completed
        (not None) across all variables.
    """
    num_variables = 0
    for variable in variables:
        num_variables = len(
            [
                k
                for k, v in variable.model_dump().items()
                if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is not None
            ],
        )
    return num_variables


def get_missing_obligatory_dataset_fields(dataset: model.Dataset) -> list:
    """Identify all obligatory dataset fields that are missing values.

    This function checks for obligatory fields that are either directly missing (i.e., set to `None`) or have
    multilanguage values with empty content.

    Args:
        dataset (model.Dataset): The dataset object to examine. This object must support the `model_dump()` method which returns a dictionary of field names and values.

    Returns:
        list: A list of field names (as strings) that are missing values. This includes:
            - Fields that are directly `None` and are listed in `OBLIGATORY_DATASET_METADATA_IDENTIFIERS`.
            - Multilanguage fields (identified by `OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE`) where
                the value exists but the primary language text is empty.
    """
    missing_dataset_fields = [
        k
        for k, v in dataset.model_dump().items()
        if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is None
    ]
    missing_multilanguage_fields = [
        k
        for k, value in dataset.model_dump().items()
        if (
            k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE
            and value
            and value[0]
            and len(value[0]) > 0
            and not value[0]["languageText"]
        )
    ]
    return missing_dataset_fields + missing_multilanguage_fields


def get_missing_obligatory_variables_fields(variables: list) -> list[dict]:
    """Identify obligatory variable fields that are missing values for each variable.

    This function checks for obligatory fields that are either directly missing (i.e., set to `None`) or have
    multilanguage values with empty content.

    Args:
        variables (list): A list of variable objects to check for missing obligatory fields.

    Returns:
        list: A list of dictionaries with variable short names as keys and lists of missing
        obligatory variable fields as values. This includes:OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS`.
            - Multilanguage fields (identified by `OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE`) where
            the value exists but the primary language text is empty.
    """
    missing_variables_fields = [
        {
            variable.short_name: [
                k
                for k, v in variable.model_dump().items()
                if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is None
            ],
        }
        for variable in variables
    ]
    missing_variables_fields = [
        item for item in missing_variables_fields if next(iter(item.values()))
    ]
    missing_variables_multi_language_fields = [
        {
            variable.short_name: [
                k
                for k, value in variable.model_dump().items()
                if (
                    k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE
                    and value
                    and value[0]
                    and len(value[0]) > 0
                    and not value[0]["languageText"]
                )
            ],
        }
        for variable in variables
    ]
    missing_variables_multi_language_fields = [
        item
        for item in missing_variables_multi_language_fields
        if next(iter(item.values()))
    ]
    return missing_variables_fields + missing_variables_multi_language_fields
