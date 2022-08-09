import argparse
import logging
import os
from typing import Type

import dash_bootstrap_components as dbc
from dash import Dash

from datadoc.Enums import SupportedLanguages
from datadoc.frontend.components.DatasetTab import get_dataset_tab
from datadoc.frontend.components.VariablesTab import get_variables_tab
from datadoc.frontend.components.Alerts import (
    dataset_validation_error,
    variables_validation_error,
    success_toast,
)
from datadoc.frontend.components.HeaderBars import (
    header,
    progress_bar,
    get_controls_bar,
)
import datadoc.state as state
from datadoc.frontend.callbacks.Callbacks import register_callbacks
from datadoc.DataDocMetadata import DataDocMetadata
from datadoc.utils import running_in_notebook

logger = logging.getLogger(__name__)

NAME = "Datadoc"


def build_app(dash_class: Type[Dash]) -> Dash:

    app = dash_class(
        name=NAME,
        title=NAME,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
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
    if dataset_path is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--dataset-path", help="Specify the path to a dataset")
        args = parser.parse_args()
        # Use example dataset if nothing specified
        dataset = args.dataset_path or "./klargjorte_data/person_data_v1.parquet"
    else:
        dataset = dataset_path

    state.metadata = DataDocMetadata(dataset)

    if running_in_notebook():
        logging.basicConfig(level=logging.WARNING)
        from jupyter_dash import JupyterDash

        JupyterDash.infer_jupyter_proxy_config()
        app = build_app(JupyterDash)
        app.run_server(mode="inline")
    else:
        logging.basicConfig(level=logging.DEBUG)
        # Assume running in server mode is better (largely for development purposes)
        logger.debug("Starting in development mode")
        app = build_app(Dash)
        app.run_server(debug=True)


if __name__ == "__main__":
    main()
