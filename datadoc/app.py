import argparse
import logging
import os
from typing import Type

import dash_bootstrap_components as dbc
from dash import Dash

import datadoc.state as state
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
from datadoc.utils import running_in_notebook, pick_random_port

logger = logging.getLogger(__name__)

NAME = "Datadoc"


def build_app(dash_class: Type[Dash]) -> Dash:

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


def main(dataset_path: str = None):
    logging.basicConfig(level=logging.DEBUG)
    if dataset_path is None:
        # Get the supplied command line argument
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "dataset_path",
            help="Specify the path to a dataset",
            nargs="?",
            default=f"{os.path.dirname(__file__)}/../klargjorte_data/person_data_v1.parquet",
        )
        dataset = parser.parse_args().dataset_path
    else:
        dataset = dataset_path

    state.metadata = DataDocMetadata(dataset)

    if running_in_notebook():
        logging.basicConfig(level=logging.INFO)
        from jupyter_dash import JupyterDash

        JupyterDash.infer_jupyter_proxy_config()
        app = build_app(JupyterDash)
        app.run_server(mode="jupyterlab", port=pick_random_port())
    else:
        # Assume running in server mode is better (largely for development purposes)
        logger.debug("Starting in development mode")
        app = build_app(Dash)
        app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
