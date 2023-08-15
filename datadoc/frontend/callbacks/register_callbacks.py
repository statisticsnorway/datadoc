from __future__ import annotations

import traceback
import typing as t

from dash import ALL, Dash, Input, Output, State, ctx
from datadoc_model.Enums import SupportedLanguages

from datadoc import state
from datadoc.frontend.callbacks.dataset import (
    accept_dataset_metadata_input,
    change_language_dataset_metadata,
    open_dataset,
)
from datadoc.frontend.callbacks.variables import (
    accept_variable_metadata_input,
    update_variable_table_dropdown_options_for_language,
    update_variable_table_language,
)
from datadoc.frontend.components.DatasetTab import DATASET_METADATA_INPUT
from datadoc.frontend.fields.DisplayDataset import DISPLAYED_DROPDOWN_DATASET_METADATA

# Avoid implementing callbacks here.
#
# The Dash Inputs and Outputs etc. shall be defined here, but the
# implementations should be in other functions, to enable unit testing


def register_callbacks(app: Dash) -> None:
    @app.callback(
        Output("progress-bar", "value"),
        Output("progress-bar", "label"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        Input("variables-table", "data"),
    )
    def callback_update_progress(value, data) -> tuple[int, str]:
        completion = state.metadata.percent_complete
        return completion, f"{completion}%"

    @app.callback(
        Output("saved-metadata-success", "is_open"),
        Input("save-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(n_clicks):
        if n_clicks and n_clicks > 0:
            # Write the final completion percentage to the model
            state.metadata.meta.percentage_complete = state.metadata.percent_complete
            state.metadata.write_metadata_document()
            return True
        else:
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
    def callback_change_language_dataset_metadata(language: str):
        return change_language_dataset_metadata(SupportedLanguages(language))

    @app.callback(
        Output("dataset-validation-error", "is_open"),
        Output("dataset-validation-explanation", "children"),
        Input({"type": DATASET_METADATA_INPUT, "id": ALL}, "value"),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(value: t.Any) -> tuple[bool, str]:
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
        if ctx.triggered_id == "language-dropdown":
            return update_variable_table_language(SupportedLanguages(language))
        else:
            return accept_variable_metadata_input(data, active_cell, data_previous)

    @app.callback(
        Output("variables-table", "dropdown"),
        Input("language-dropdown", "value"),
    )
    def callback_variable_table_dropdown_options(language: str):
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
        try:
            open_dataset(dataset_path)
        except FileNotFoundError:
            return (
                False,
                True,
                f"Datasettet '{dataset_path}' finnes ikke.",
                state.current_metadata_language.value,
            )
        except Exception as e:
            return (
                False,
                True,
                "\n".join(traceback.format_exception_only(type(e), e)),
                state.current_metadata_language.value,
            )
        if n_clicks and n_clicks > 0:
            return True, False, "", state.current_metadata_language.value
        else:
            return False, False, "", state.current_metadata_language.value
