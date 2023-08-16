"""All decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""


from __future__ import annotations

from typing import TYPE_CHECKING

from dash import ALL, Dash, Input, Output, State, ctx
from datadoc_model.Enums import SupportedLanguages

from datadoc import state
from datadoc.frontend.callbacks.dataset import (
    accept_dataset_metadata_input,
    change_language_dataset_metadata,
    open_dataset_handling,
)
from datadoc.frontend.callbacks.variables import (
    accept_variable_metadata_input,
    update_variable_table_dropdown_options_for_language,
    update_variable_table_language,
)
from datadoc.frontend.components.dataset_tab import DATASET_METADATA_INPUT
from datadoc.frontend.fields.display_dataset import DISPLAYED_DROPDOWN_DATASET_METADATA

if TYPE_CHECKING:
    from datadoc.frontend.callbacks.utils import MetadataInputTypes


def register_callbacks(app: Dash) -> None:
    """Define and register callbacks."""

    @app.callback(
        Output("progress-bar", "value"),
        Output("progress-bar", "label"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        Input("variables-table", "data"),
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
            # Write the final completion percentage to the model
            state.metadata.meta.percentage_complete = state.metadata.percent_complete
            state.metadata.write_metadata_document()
            return True

        return False

    @app.callback(
        *[
            Output(
                {
                    "type": DATASET_METADATA_INPUT,
                    "id": m.identifier,
                },
                "options",
            )
            for m in DISPLAYED_DROPDOWN_DATASET_METADATA
        ],
        Output(
            {"type": DATASET_METADATA_INPUT, "id": ALL},
            "value",
        ),
        Input("language-dropdown", "value"),
    )
    def callback_change_language_dataset_metadata(
        language: str,
    ) -> tuple[tuple[list[dict[str, str]], ...], list]:
        """Update dataset metadata values upon change of language."""
        return change_language_dataset_metadata(SupportedLanguages(language))

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
        Output("variables-table", "data"),
        Output("variables-validation-error", "is_open"),
        Output("variables-validation-explanation", "children"),
        State("variables-table", "active_cell"),
        Input("variables-table", "data"),
        State("variables-table", "data_previous"),
        Input("language-dropdown", "value"),
        prevent_initial_call=True,
    )
    def callback_variable_table(
        active_cell: dict,
        data: list[dict],
        data_previous: list[dict],
        language: str,
    ) -> tuple[list[dict], bool, str]:
        """Update data in the variable table.

        Triggered upon:
        - New data enetered in the variable table.
        - Change of language.

        Will display an alert if validation fails.
        """
        if ctx.triggered_id == "language-dropdown":
            return update_variable_table_language(SupportedLanguages(language))

        return accept_variable_metadata_input(data, active_cell, data_previous)

    @app.callback(
        Output("variables-table", "dropdown"),
        Input("language-dropdown", "value"),
    )
    def callback_variable_table_dropdown_options(
        language: str,
    ) -> dict[str, dict[str, list[dict[str, str]]]]:
        """Update the options in variable table dropdowns when the language changes."""
        language = SupportedLanguages(language)
        return update_variable_table_dropdown_options_for_language(language)

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
    ) -> tuple[bool, bool, str, SupportedLanguages]:
        """Open a dataset.

        Shows an alert on success or failure.

        To trigger reload of data in the UI, we update the
        language dropdown. This is a hack and could be replaced
        by a more formal mechanism.
        """
        return open_dataset_handling(n_clicks, dataset_path)
