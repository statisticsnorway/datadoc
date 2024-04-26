"""Top-level entrypoint, configuration and layout for the datadoc app.

Members of this module should not be imported into any sub-modules, this will cause circular imports.
"""

from __future__ import annotations

import concurrent
import logging
from pathlib import Path

from dash import Dash
from dash import dcc
from dash import html
from flask_healthz import healthz

from datadoc import config
from datadoc import state
from datadoc.backend.code_list import CodeList
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.frontend.callbacks.register_callbacks import register_callbacks
from datadoc.frontend.components.control_bars import build_controls_bar
from datadoc.frontend.components.control_bars import build_footer_control_bar
from datadoc.frontend.components.control_bars import header
from datadoc.frontend.components.control_bars import progress_bar
from datadoc.logging_configuration.logging_config import configure_logging
from datadoc.utils import get_app_version
from datadoc.utils import pick_random_port
from datadoc.utils import running_in_notebook

configure_logging()
logger = logging.getLogger(__name__)


def build_app(app: type[Dash]) -> Dash:
    """Define the layout, register callbacks."""
    app.layout = html.Div(
        children=[
            html.Header(
                [
                    header,
                ],
                className="header-wrapper",
            ),
            html.Main(
                [
                    dcc.Store(
                        id="dataset-opened-counter",
                        data=0,
                        storage_type="session",
                    ),
                    progress_bar,
                    build_controls_bar(),
                    html.Div(id="alerts-section"),
                    dcc.Tabs(
                        id="tabs",
                        className="ssb-tabs",
                        value="dataset",
                        children=[
                            dcc.Tab(
                                label="Datasett",
                                value="dataset",
                                className="workspace-tab",
                            ),
                            dcc.Tab(
                                label="Variabler",
                                value="variables",
                                className="workspace-tab",
                            ),
                        ],
                    ),
                    html.Div(id="display-tab"),
                ],
                className="main-content-app",
            ),
            build_footer_control_bar(),
        ],
        className="app-wrapper",
    )

    register_callbacks(app)

    return app


def get_app(
    executor: concurrent.futures.ThreadPoolExecutor,
    dataset_path: str | None = None,
) -> tuple[Dash, int]:
    """Centralize all the ugliness around initializing the app."""
    logger.info("Datadoc version v%s", get_app_version())
    collect_data_from_external_sources(executor)
    state.metadata = DataDocMetadata(
        state.statistic_subject_mapping,
        dataset_path=dataset_path,
    )

    # The service prefix must be set to run correctly on Dapla Jupyter
    if prefix := config.get_jupyterhub_service_prefix():
        port = pick_random_port()
        requests_pathname_prefix = f"{prefix}proxy/{port}/"
    else:
        port = config.get_port()
        requests_pathname_prefix = "/"

    name = config.get_app_name()

    app = Dash(
        name=name,
        title=name,
        assets_folder=f"{Path(__file__).parent}/assets",
        requests_pathname_prefix=requests_pathname_prefix,
        suppress_callback_exceptions=True,
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


def collect_data_from_external_sources(
    executor: concurrent.futures.ThreadPoolExecutor,
) -> None:
    """Call classes and methods which collect data from external sources.

    Must be non-blocking to prevent delays in app startup.
    """
    logger.debug("Start threads - Collecting data from external sources")
    state.statistic_subject_mapping = StatisticSubjectMapping(
        executor,
        config.get_statistical_subject_source_url(),
    )

    state.unit_types = CodeList(
        executor,
        config.get_unit_code(),
    )

    state.measurement_units = CodeList(
        executor,
        config.get_measurement_unit_code(),
    )

    state.organisational_units = CodeList(
        executor,
        config.get_organisational_unit_code(),
    )

    state.data_sources = CodeList(
        executor,
        config.get_data_source_code(),
    )
    logger.debug("Finished blocking - Collecting data from external sources")


def main(dataset_path: str | None = None) -> None:
    """Entrypoint when running as a script."""
    if dataset_path:
        logger.info("Starting app with dataset_path = %s", dataset_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        app, port = get_app(executor, dataset_path)
        if running_in_notebook():
            logger.info("Running in notebook")
            app.run(
                jupyter_mode="tab",
                jupyter_server_url=config.get_jupyterhub_http_referrer(),
                jupyter_height=1000,
                port=port,
            )
        else:
            if dev_mode := config.get_dash_development_mode():
                logger.warning(
                    "Starting in Development Mode. NOT SUITABLE FOR PRODUCTION.",
                )
            app.run(debug=dev_mode, port=port)


if __name__ == "__main__":
    main()
