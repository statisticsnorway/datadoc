import dash_bootstrap_components as dbc
from dash import html
from datadoc.frontend.Builders import make_ssb_warning_alert

dataset_validation_error = make_ssb_warning_alert(
    "dataset-validation-error",
    "Failed validation",
    "dataset-validation-explanation",
)

variables_validation_error = make_ssb_warning_alert(
    "variables-validation-error",
    "Failed validation",
    "variables-validation-explanation",
)

success_toast = dbc.Alert(
    id="success-message",
    is_open=False,
    dismissable=True,
    fade=True,
    class_name="ssb-dialog",
    children=[
        dbc.Row(
            [
                dbc.Col(
                    width=3,
                    children=[
                        html.Div(
                            className="ssb-dialog icon-panel",
                            children=[
                                html.I(
                                    className="bi bi-check-circle",
                                ),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    [
                        html.H5(
                            "Lagret metadata",
                        ),
                    ]
                ),
            ],
            align="center",
        )
    ],
    color="success",
)
