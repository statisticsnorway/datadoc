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
from datadoc.backend.constants import OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS
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
    """Set default values on variables.

    If variables attributes 'id' is None set a unique uuid4 value.
    If 'is personal data' is None set default value of 'not personal data'.

    Args:
        variables (list): A list of variables

    Returns:
        None
    """
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = model.IsPersonalData.NOT_PERSONAL_DATA


def set_variables_inherit_from_dataset(
    dataset: model.Dataset,
    variables: list,
) -> None:
    """Set dataset values on variables.

    Handles variable values for these fields:
        'contains data from',
        'contains data from',
        'contains data until',
        'temporality type',
        'data source'

    If either of values in list are None they will inherit from dataset value.

    Args:
        dataset (model.Dataset): the dataset to inherit from
        variables (list): list of variables which may inherit from dataset

    Returns:
        None
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
    """Evaluate date order of two dates.

    If 'date until' is before 'date from' it is incorrect date order.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True
        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False

    Args:
        date_from (datetime.date): start date
        date_until (datetime.date): end date
    Returns:
        bool: True if incorrect date order.
    """
    return date_from is not None and date_until is not None and date_until < date_from


def num_obligatory_dataset_fields_completed(dataset: model.Dataset) -> int:
    """Return the number of obligatory dataset fields with value."""
    return len(
        [
            k
            for k, v in dataset.model_dump().items()
            if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is not None
        ],
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Return the number of obligatory variable fields for one variable with value."""
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


def get_missing_obligatory_dataset_fields(dataset) -> list:  # noqa: ANN001
    """Get all obligatory dataset fields with no value.

    Args:
        dataset (Any): The dataset examined.

    Returns:
        list
    """
    return [
        k
        for k, v in dataset.model_dump().items()
        if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is None
    ]


def get_missing_obligatory_variables_fields(variables) -> list[dict]:  # noqa: ANN001
    """Get all obligatory variable fields for with no value for all variables.

    Each dict has variable shortname as key and a list of missing fields.

    Args:
        variables (list): All variables.

    Returns:
        list[dict]
    """
    return [
        {
            variable.short_name: [
                k
                for k, v in variable.model_dump().items()
                if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is None
            ],
        }
        for variable in variables
    ]
