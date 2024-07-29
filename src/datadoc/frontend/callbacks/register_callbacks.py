"""All decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING

from dash import ALL
from dash import MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx
from dash import html
from dash import no_update

from datadoc import state
from datadoc.backend.model_validation import ObligatoryDatasetWarning
from datadoc.backend.model_validation import ObligatoryVariableWarning
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc.frontend.callbacks.dataset import dataset_control
from datadoc.frontend.callbacks.dataset import open_dataset_handling
from datadoc.frontend.callbacks.utils import render_tabs
from datadoc.frontend.callbacks.variables import accept_variable_metadata_date_input
from datadoc.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc.frontend.callbacks.variables import populate_variables_workspace
from datadoc.frontend.callbacks.variables import variables_control
from datadoc.frontend.components.builders import AlertTypes
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.components.builders import build_ssb_alert
from datadoc.frontend.components.dataset_tab import SECTION_WRAPPER_ID
from datadoc.frontend.components.variables_tab import ACCORDION_WRAPPER_ID
from datadoc.frontend.components.variables_tab import VARIABLES_INFORMATION_ID
from datadoc.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc.frontend.fields.display_base import DATASET_METADATA_MULTILANGUAGE_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_MULTILANGUAGE_INPUT
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OBLIGATORY_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OPTIONAL_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
    """Define and register callbacks."""

    @app.callback(
        Output("progress-bar", "value"),
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
    ) -> str:
        """Update the progress bar when new data is entered."""
        return str(state.metadata.percent_complete)

    @app.callback(
        Output("progress-bar-label", "children"),
        Input("progress-bar", "value"),
    )
    def callback_update_progress_label(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> str:
        """Update the progress bar label when progress bar is updated."""
        return f"{state.metadata.percent_complete}%"

    @app.callback(
        Output("alerts-section", "children", allow_duplicate=True),
        Input("save-button", "n_clicks"),
        State("alerts-section", "children"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(
        n_clicks: int,
        alerts: list,  # argument required by Dash  # noqa: ARG001
    ) -> list:
        """Save the metadata document to disk and check obligatory metadata.

        Returns:
            List of alerts. Obligatory metadata alert warning if there is obligatory metadata missing.
            And success alert if metadata is saved correctly.
            If none return no_update.
        """
        missing_obligatory_dataset = ""
        missing_obligatory_variables = ""
        if n_clicks and n_clicks > 0:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                state.metadata.write_metadata_document()
                save = build_ssb_alert(
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
                save,
                dataset_control(missing_obligatory_dataset),
                variables_control(missing_obligatory_variables),
            ]

        return no_update

    @app.callback(
        Output(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "error",
        ),
        Output(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "errorMessage",
        ),
        Input(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
        )

    @app.callback(
        Output(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_multilanguage_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        # Get the ID of the input that changed. This MUST match the attribute name defined in DataDocDataSet
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
            ctx.triggered_id["language"],
        )

    @app.callback(
        Output("alerts-section", "children", allow_duplicate=True),
        Output("dataset-opened-counter", "data"),  # Used to force reload of metadata
        Input("open-button", "n_clicks"),
        State("dataset-path-input", "value"),
        State("dataset-opened-counter", "data"),
        prevent_initial_call=True,
    )
    def callback_open_dataset(
        n_clicks: int,
        dataset_path: str,
        dataset_opened_counter: int,
    ) -> tuple[dbc.Alert, int]:
        """Open a dataset.

        Shows an alert on success or failure.

        To trigger reload of data in the UI, we update the
        language dropdown. This is a hack and could be replaced
        by a more formal mechanism.
        """
        return open_dataset_handling(n_clicks, dataset_path, dataset_opened_counter)

    @app.callback(
        Output("display-tab", "children"),
        Input("tabs", "value"),
    )
    def callback_render_tabs(tab: html.Article) -> html.Article | None:
        """Return correct tab content."""
        return render_tabs(tab)

    @app.callback(
        Output(VARIABLES_INFORMATION_ID, "children"),
        Input("dataset-opened-counter", "data"),
        prevent_initial_call=True,
    )
    def callback_populate_variables_info_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
    ) -> str:
        return f"Datasettet inneholder {len(state.metadata.variables)} variabler."

    @app.callback(
        Output(ACCORDION_WRAPPER_ID, "children"),
        Input("dataset-opened-counter", "data"),
        Input("search-variables", "value"),
    )
    def callback_populate_variables_workspace(
        dataset_opened_counter: int,  # Dash requires arguments for all Inputs
        search_query: str,
    ) -> list:
        """Create variable workspace with accordions for variables.

        Allows for filtering which variables are displayed via the search box.
        """
        logger.debug("Populating variables workspace. Search query: %s", search_query)
        return populate_variables_workspace(
            state.metadata.variables,
            search_query,
            dataset_opened_counter,
        )

    @app.callback(
        Output(SECTION_WRAPPER_ID, "children"),
        Input("dataset-opened-counter", "data"),
    )
    def callback_populate_dataset_workspace(
        dataset_opened_counter: int,  # Dash requires arguments for all Inputs
    ) -> list:
        """Create dataset workspace with sections."""
        logger.debug("Populating dataset workspace")
        return [
            build_dataset_edit_section(
                "Obligatorisk",
                OBLIGATORY_EDITABLE_DATASET_METADATA,
                state.metadata.dataset,
                {
                    "type": "dataset-edit-section",
                    "id": f"obligatory-{dataset_opened_counter}",
                },
            ),
            build_dataset_edit_section(
                "Anbefalt",
                OPTIONAL_DATASET_METADATA,
                state.metadata.dataset,
                {
                    "type": "dataset-edit-section",
                    "id": f"recommended-{dataset_opened_counter}",
                },
            ),
            build_dataset_edit_section(
                "Maskingenerert",
                NON_EDITABLE_DATASET_METADATA,
                state.metadata.dataset,
                {
                    "type": "dataset-edit-section",
                    "id": f"machine-{dataset_opened_counter}",
                },
            ),
        ]

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
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_multilanguage_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> dbc.Alert:
        """Save updated variable metadata values."""
        message = accept_variable_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["variable_short_name"],
            ctx.triggered_id["id"],
            ctx.triggered_id["language"],
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
