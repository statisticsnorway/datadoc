"""Functions which can't be placed in utils.py because of circular imports."""

import logging
import warnings

from dapla_metadata.datasets import ObligatoryDatasetWarning
from dapla_metadata.datasets import ObligatoryVariableWarning

from datadoc import state
from datadoc.frontend.callbacks.dataset import dataset_control
from datadoc.frontend.callbacks.variables import variables_control
from datadoc.frontend.components.builders import AlertTypes
from datadoc.frontend.components.builders import build_ssb_alert

logger = logging.getLogger(__name__)


def save_metadata_and_generate_alerts() -> list:
    """Save the metadata document to disk and check obligatory metadata.

    Returns:
        List of alerts including obligatory metadata warnings if missing,
        and success alert if metadata is saved correctly.
    """
    missing_obligatory_dataset = ""
    missing_obligatory_variables = ""

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.metadata.write_metadata_document()
        success_alert = build_ssb_alert(
            AlertTypes.SUCCESS,
            "Lagret metadata",
        )

        for warning in w:
            if issubclass(warning.category, ObligatoryDatasetWarning):
                missing_obligatory_dataset = str(warning.message)
            elif issubclass(warning.category, ObligatoryVariableWarning):
                missing_obligatory_variables = str(warning.message)
            else:
                logger.warning(
                    "An unexpected warning was caught: %s",
                    warning.message,
                )

    return [
        success_alert,
        dataset_control(missing_obligatory_dataset),
        variables_control(missing_obligatory_variables),
    ]
