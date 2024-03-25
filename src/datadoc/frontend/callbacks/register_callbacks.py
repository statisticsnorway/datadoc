"""All decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dash import ALL
from dash import MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx
from dash import no_update

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc.frontend.callbacks.dataset import open_dataset_handling
from datadoc.frontend.callbacks.utils import update_global_language_state
from datadoc.frontend.callbacks.variables import accept_variable_metadata_date_input
from datadoc.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.components.dataset_tab import SECTION_WRAPPER_ID
from datadoc.frontend.components.variables_tab import ACCORDION_WRAPPER_ID
from datadoc.frontend.components.variables_tab import VARIABLES_INFORMATION_ID
from datadoc.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OBLIGATORY_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OPTIONAL_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
    """Define and register callbacks."""

    @app.callback(
        Output("progress-bar", "value"),
        Output("progress-bar", "label"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        Input(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": ALL,
                "id": ALL,
            },
            "value",
        ),
    )
    def callback_update_progress(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
        data: list[dict],  # noqa: ARG001 argument required by Dash
    ) -> tuple[int, str]:
        """Update the progress bar when new data is entered."""
        completion = state.metadata.percent_complete
        return completion, f"{completion}%"

    @app.callback(
        Output("saved-metadata-success", "is_open"),
        Input("save-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(n_clicks: int) -> bool:
        """Save the metadata document to disk."""
        if n_clicks and n_clicks > 0:
            state.metadata.write_metadata_document()
            return True

        return False

    @app.callback(
        Output("dataset-validation-error", "is_open"),
        Output("dataset-validation-explanation", "children"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        # Get the ID of the input that changed. This MUST match the attribute name defined in DataDocDataSet
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
        )

    @app.callback(
        Output("opened-dataset-success", "is_open"),
        Output("opened-dataset-error", "is_open"),
        Output("opened-dataset-error-explanation", "children"),
        Output("language-dropdown", "value"),  # Used to force reload of metadata
        Input("open-button", "n_clicks"),
        State("dataset-path-input", "value"),
    )
    def callback_open_dataset(
        n_clicks: int,
        dataset_path: str,
    ) -> tuple[bool, bool, str, str]:
        """Open a dataset.

        Shows an alert on success or failure.

        To trigger reload of data in the UI, we update the
        language dropdown. This is a hack and could be replaced
        by a more formal mechanism.
        """
        return open_dataset_handling(n_clicks, dataset_path)

    @app.callback(
        Output(VARIABLES_INFORMATION_ID, "children"),
        Input("language-dropdown", "value"),
        prevent_initial_call=True,
    )
    def callback_populate_variables_info_section(
        language: str,  # noqa: ARG001 Dash requires arguments for all Inputs
    ) -> str:
        return f"Datasettet inneholder {len(state.metadata.variables)} variabler."

    @app.callback(
        Output(ACCORDION_WRAPPER_ID, "children"),
        Input("language-dropdown", "value"),
        prevent_initial_call=True,
    )
    def callback_populate_variables_workspace(
        language: str,
    ) -> list:
        """Create variable workspace with accordions for variables."""
        update_global_language_state(SupportedLanguages(language))
        logger.info("Populating new variables workspace")
        return [
            build_ssb_accordion(
                variable.short_name,
                {
                    "type": "variables-accordion",
                    "id": f"{variable.short_name}-{language}",  # Insert language into the ID to invalidate browser caches
                },
                variable.short_name,
                children=[
                    build_edit_section(
                        OBLIGATORY_VARIABLES_METADATA,
                        "Obligatorisk",
                        variable,
                        state.current_metadata_language.value,
                    ),
                    build_edit_section(
                        OPTIONAL_VARIABLES_METADATA,
                        "Anbefalt",
                        variable,
                        state.current_metadata_language.value,
                    ),
                ],
            )
            for variable in list(state.metadata.variables)
        ]

    @app.callback(
        Output(SECTION_WRAPPER_ID, "children"),
        Input("language-dropdown", "value"),
        Input("open-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def callback_populate_dataset_workspace(
        language: str,
        n_clicks: int,
    ) -> list:
        """Create dataset workspace with sections."""
        update_global_language_state(SupportedLanguages(language))
        logger.info("Populating new dataset workspace")
        if n_clicks:
            return [
                build_dataset_edit_section(
                    "Obligatorisk",
                    OBLIGATORY_EDITABLE_DATASET_METADATA,
                    state.current_metadata_language,
                    state.metadata.dataset,
                    {"type": "dataset-edit-section", "id": f"obligatory-{language}"},
                ),
                build_dataset_edit_section(
                    "Anbefalt",
                    OPTIONAL_DATASET_METADATA,
                    state.current_metadata_language,
                    state.metadata.dataset,
                    {"type": "dataset-edit-section", "id": f"recommended-{language}"},
                ),
                build_dataset_edit_section(
                    "Maskingenerert",
                    NON_EDITABLE_DATASET_METADATA,
                    state.current_metadata_language,
                    state.metadata.dataset,
                    {"type": "dataset-edit-section", "id": f"machine-{language}"},
                ),
            ]
        return no_update

    @app.callback(
        Output(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> dbc.Alert:
        """Save updated variable metadata values."""
        message = accept_variable_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["variable_short_name"],
            ctx.triggered_id["id"],
        )
        if not message:
            # No error to display.
            return False, ""

        return True, message

    @app.callback(
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "errorMessage",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "value",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_date_input(
        contains_data_from: str,
        contains_data_until: str,
    ) -> dbc.Alert:
        """Special case handling for date fields which have a relationship to one another."""
        return accept_variable_metadata_date_input(
            VariableIdentifiers(ctx.triggered_id["id"]),
            ctx.triggered_id["variable_short_name"],
            contains_data_from,
            contains_data_until,
        )

    @app.callback(
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "errorMessage",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "value",
        ),
        Input(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_date_input(
        contains_data_from: str,
        contains_data_until: str,
    ) -> dbc.Alert:
        """Special case handling for date fields which have a relationship to one another."""
        return accept_dataset_metadata_date_input(
            DatasetIdentifiers(ctx.triggered_id["id"]),
            contains_data_from,
            contains_data_until,
        )
