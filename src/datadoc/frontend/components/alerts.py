"""Components for different types of alerts are defined here."""

from __future__ import annotations

from datadoc.frontend.components.builders import AlertTypes
from datadoc.frontend.components.builders import build_ssb_alert

dataset_validation_error = build_ssb_alert(
    AlertTypes.WARNING,
    "dataset-validation-error",
    "Validering feilet",
    "dataset-validation-explanation",
)

variables_validation_error = build_ssb_alert(
    AlertTypes.WARNING,
    "variables-validation-error",
    "Validering feilet",
    "variables-validation-explanation",
)

opened_dataset_error = build_ssb_alert(
    AlertTypes.WARNING,
    "opened-dataset-error",
    "Kunne ikke åpne datasettet",
    "opened-dataset-error-explanation",
)

saved_metadata_success = build_ssb_alert(
    AlertTypes.SUCCESS,
    "saved-metadata-success",
    "Lagret metadata",
    "saved-metadata-success-explanation",
)

opened_dataset_success = build_ssb_alert(
    AlertTypes.SUCCESS,
    "opened-dataset-success",
    "Åpnet datasett",
    "opened-dataset-success-explanation",
)
