from __future__ import annotations

import pathlib
import uuid

from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from dapla import AuthClient
from datadoc_model import model

from datadoc.enums import Assessment
from datadoc.enums import DataSetState
from datadoc.enums import LanguageStringType
from datadoc.enums import LanguageStringTypeItem

DEFAULT_SPATIAL_COVERAGE_DESCRIPTION = LanguageStringType(
    [
        LanguageStringTypeItem(
            languageCode="nb",
            languageText="Norge",
        ),
        LanguageStringTypeItem(
            languageCode="nn",
            languageText="Noreg",
        ),
        LanguageStringTypeItem(
            languageCode="en",
            languageText="Norway",
        ),
    ],
)


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
    """Set default values on variables."""
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = model.IsPersonalData.NOT_PERSONAL_DATA


# error messages
VALIDATION_ERROR = "Validation error: "
DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}contains_data_from must be the same or earlier date than contains_data_until"
