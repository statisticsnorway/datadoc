import re
from typing import List
import dash_bootstrap_components as dbc
from dash import html, dcc

from datadoc.frontend.DisplayDataset import DisplayDatasetMetadata

DATASET_METADATA_INPUT = "dataset-metadata-input"


def make_dataset_metadata_accordion_item(
    title: str,
    metadata_inputs: List[DisplayDatasetMetadata],
) -> dbc.AccordionItem:
    return dbc.AccordionItem(
        title=title,
        children=[
            dbc.Row(
                [
                    dbc.Col(html.Label(i.display_name)),
                    dbc.Col(
                        i.component(
                            placeholder=i.description,
                            disabled=not i.editable,
                            id={
                                "type": DATASET_METADATA_INPUT,
                                "id": i.identifier,
                            },
                            **i.extra_kwargs,
                            **(i.options or {}),
                        ),
                        width=5,
                    ),
                    dbc.Col(width=4),
                ]
            )
            for i in metadata_inputs
        ],
    )


def make_ssb_styled_tab(label: str, content: dbc.Container) -> dbc.Tab:
    return dbc.Tab(
        label=label,
        # Replace all whitespace with dashes
        tab_id=re.sub(r"\s+", "-", label.lower()),
        label_class_name="ssb-tabs navigation-item",
        label_style={"margin-left": "10px", "margin-right": "10px"},
        style={"padding": "4px"},
        children=content,
    )


def make_ssb_warning_alert(
    alert_identifier: str, title: str, content_identifier: str
) -> dbc.Alert:
    return dbc.Alert(
        id=alert_identifier,
        is_open=False,
        dismissable=True,
        fade=True,
        class_name="ssb-dialog warning",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        width=1,
                        children=[
                            html.Div(
                                className="ssb-dialog warning icon-panel",
                                children=[
                                    html.I(
                                        className="bi bi-exclamation-triangle",
                                    ),
                                ],
                            )
                        ],
                    ),
                    dbc.Col(
                        [
                            html.H5(
                                title,
                            ),
                            dcc.Markdown(
                                id=content_identifier,
                            ),
                        ]
                    ),
                ],
            )
        ],
        color="danger",
    )
