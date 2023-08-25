"""Top-level entrypoint, configuration and layout for the datadoc app.

Members of this module should not be imported into any sub-modules, this will cause circular imports.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import Dash
from datadoc_model.Enums import SupportedLanguages
from flask_healthz import healthz

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.frontend.callbacks.register_callbacks import register_callbacks
from datadoc.frontend.components.alerts import (
    dataset_validation_error,
    opened_dataset_error,
    opened_dataset_success,
    saved_metadata_success,
    variables_validation_error,
)
from datadoc.frontend.components.control_bars import (
    build_controls_bar,
    build_language_dropdown,
    header,
    progress_bar,
)
from datadoc.frontend.components.dataset_tab import build_dataset_tab
from datadoc.frontend.components.variables_tab import build_variables_tab
from datadoc.utils import get_app_version, pick_random_port, running_in_notebook

logger = logging.getLogger(__name__)

NAME = "Datadoc"
DEFAULT_PORT: int = 7002
JUPYTERHUB_SERVICE_PREFIX_ENV = "JUPYTERHUB_SERVICE_PREFIX"


def build_app(app: type[Dash]) -> Dash:
    """Define the layout, register callbacks."""
    app.layout = dbc.Container(
        style={"padding": "4px"},
        children=[
            header,
            progress_bar,
            build_controls_bar(),
            variables_validation_error,
            dataset_validation_error,
            opened_dataset_error,
            saved_metadata_success,
            opened_dataset_success,
            dbc.CardBody(
                style={"padding": "4px"},
                children=[
                    dbc.Tabs(
                        id="tabs",
                        class_name="ssb-tabs",
                        children=[
                            build_dataset_tab(),
                            build_variables_tab(),
                        ],
                    ),
                ],
            ),
            build_language_dropdown(),
        ],
    )

    register_callbacks(app)

    return app


def get_app(dataset_path: str | None = None) -> tuple[Dash, int]:
    """Centralize all the ugliness around initializing the app."""
    logging.basicConfig(level=logging.INFO, force=True)
    logger.info("Datadoc version v%s", get_app_version())
    state.current_metadata_language = SupportedLanguages.NORSK_BOKMÅL
    state.metadata = DataDocMetadata(dataset_path)

    # This must be set to run correctly on Dapla Jupyter
    if JUPYTERHUB_SERVICE_PREFIX_ENV in os.environ:
        port = pick_random_port()
        requests_pathname_prefix = (
            f"{os.getenv(JUPYTERHUB_SERVICE_PREFIX_ENV, '/')}proxy/{port}/"
        )
    else:
        port = DEFAULT_PORT
        requests_pathname_prefix = "/"

    app = Dash(
        name=NAME,
        title=NAME,
        assets_folder=f"{Path(__file__).parent}/assets",
        requests_pathname_prefix=requests_pathname_prefix,
    )
    app = build_app(app)
    app.server.register_blueprint(healthz, url_prefix="/healthz")
    app.server.config["HEALTHZ"] = {
        "live": lambda: True,
        "ready": lambda: True,
        "startup": lambda: True,
    }
    logger.info("Built app with endpoints configured on /healthz")

    return app, port


def main(dataset_path: str | None = None) -> None:
    """Entrypoint when running as a script."""
    logging.basicConfig(level=logging.DEBUG, force=True)
    logger.info("Starting app with dataset_path = %s", dataset_path)
    app, port = get_app(dataset_path)
    if running_in_notebook():
        logger.info("Running in notebook")
        app.run(
            jupyter_mode="tab",
            jupyter_server_url=os.getenv("JUPYTERHUB_HTTP_REFERER", None),
            jupyter_height=1000,
            port=port,
        )
    else:
        # Assume running in server mode is better (largely for development purposes)
        logging.basicConfig(level=logging.DEBUG, force=True)
        logger.debug("Starting in development mode")
        app.run(debug=True, port=port)


if __name__ == "__main__":
    main()
