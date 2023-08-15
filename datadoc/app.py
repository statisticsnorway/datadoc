import logging
import os

import dash_bootstrap_components as dbc
from dash import Dash
from datadoc_model.Enums import SupportedLanguages

from datadoc import state
from datadoc.backend.DataDocMetadata import DataDocMetadata
from datadoc.frontend.callbacks.register import register_callbacks
from datadoc.frontend.components.Alerts import (
    dataset_validation_error,
    success_toast,
    variables_validation_error,
)
from datadoc.frontend.components.DatasetTab import get_dataset_tab
from datadoc.frontend.components.HeaderBars import (
    get_controls_bar,
    header,
    progress_bar,
)
from datadoc.frontend.components.VariablesTab import get_variables_tab
from datadoc.utils import get_app_version, pick_random_port, running_in_notebook

logger = logging.getLogger(__name__)

NAME = "Datadoc"
DATADOC_DATASET_PATH_ENV_VAR = "DATADOC_DATASET_PATH"


def build_app(dash_class: type[Dash]) -> Dash:
    app = dash_class(
        name=NAME,
        title=NAME,
        assets_folder=f"{os.path.dirname(__file__)}/assets",
    )

    app.layout = dbc.Container(
        style={"padding": "4px"},
        children=[
            header,
            progress_bar,
            get_controls_bar(),
            dbc.CardBody(
                style={"padding": "4px"},
                children=[
                    dbc.Tabs(
                        id="tabs",
                        class_name="ssb-tabs",
                        children=[
                            get_dataset_tab(),
                            get_variables_tab(),
                        ],
                    ),
                ],
            ),
            variables_validation_error,
            dataset_validation_error,
            success_toast,
        ],
    )

    register_callbacks(app)

    return app


def get_app(dataset_path: str | None = None) -> Dash:
    logging.basicConfig(level=logging.INFO)
    if dataset_path is not None:
        dataset = dataset_path
    elif path_from_env := os.getenv(DATADOC_DATASET_PATH_ENV_VAR):
        logger.info(
            f"Dataset path from {DATADOC_DATASET_PATH_ENV_VAR}: '{path_from_env}'",
        )
        dataset = path_from_env

    logger.info(f"Datadoc version v{get_app_version()}")
    state.metadata = DataDocMetadata(dataset)
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL

    if running_in_notebook():
        from jupyter_dash import JupyterDash

        JupyterDash.infer_jupyter_proxy_config()
        app = build_app(JupyterDash)
    else:
        app = build_app(Dash)

    return app


def main(dataset_path: str | None = None):
    app = get_app(dataset_path)
    if running_in_notebook():
        port = pick_random_port()
        app.run_server(mode="jupyterlab", port=port)
        logger.info(f"Server running on port {port}")
    else:
        # Assume running in server mode is better (largely for development purposes)
        logging.basicConfig(level=logging.DEBUG, force=True)
        logger.debug("Starting in development mode")
        app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
