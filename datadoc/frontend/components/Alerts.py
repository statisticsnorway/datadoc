from datadoc.frontend.components.Builders import AlertTypes, make_ssb_alert

dataset_validation_error = make_ssb_alert(
    AlertTypes.WARNING,
    "dataset-validation-error",
    "Validering feilet",
    "dataset-validation-explanation",
)

variables_validation_error = make_ssb_alert(
    AlertTypes.WARNING,
    "variables-validation-error",
    "Validering feilet",
    "variables-validation-explanation",
)

saved_metadata_success = make_ssb_alert(
    AlertTypes.SUCCESS,
    "saved-metadata-success",
    "Lagret metadata",
    "saved-metadata-success-explanation",
)

opened_dataset_success = make_ssb_alert(
    AlertTypes.SUCCESS,
    "opened-dataset-success",
    "Åpnet datasett",
    "opened-dataset-success-explanation",
)
