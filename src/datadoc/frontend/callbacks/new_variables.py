"""New variables tab."""

from __future__ import annotations

import logging

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.fields.display_new_variables import (
    DISPLAYED_DROPDOWN_VARIABLES_METADATA,
)
from datadoc.utils import get_display_values

logger = logging.getLogger(__name__)


def get_variables_in_dataset() -> list:
    """Get variable objects in dataset."""
    response = {}
    respons_list = []
    for v in state.metadata.meta.variables:
        response = get_display_values(v, state.current_metadata_language)
        respons_list.append(response)
    return respons_list


def get_variable_in_dataset(short_name: str) -> object:
    """Get one variable."""
    variables = get_variables_in_dataset()
    variable = {}
    for v in variables:
        if v.short_name == short_name:
            variable = v
    return variable


def get_variables_short_names() -> list[str]:
    """Get list of variables short_names."""
    return [response["short_name"] for response in get_variables_in_dataset()]


# temp move for testing another solution
"""@app.callback(
        *[
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "pers_id",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "tidspunkt",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "sivilstand",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "alm_inntekt",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "sykepenger",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "ber_bruttoformue",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "fullf_utdanning",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
            [
                Output(
                    {
                        "type": VARIABLES_METADATA_INPUT,
                        "variable_short_name": "hoveddiagnose",
                        "id": m.identifier,
                    },
                    "items",
                )
                for m in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ],
        ],
        State({"type": "variables-accordion", "id": ALL}, "id"),
        Input("language-dropdown", "value"),
    )"""


def callback_change_language_variable_metadata_new_input(
    accordions: list,
    language: str,
) -> tuple[object, ...]:
    """Update dataset metadata values upon change of language."""
    variables_short_names = get_variables_short_names()
    logger.info(
        "Variables info: %s %s",
        [
            *(
                e.options_getter(SupportedLanguages(language))
                for e in DISPLAYED_DROPDOWN_VARIABLES_METADATA
            ),
        ],
        *(accordion for accordion in accordions),
    )
    return (
        *(
            e.options_getter(SupportedLanguages(language))
            for e in DISPLAYED_DROPDOWN_VARIABLES_METADATA
        ),
    ) * len(variables_short_names)


""" return [
            (
                build_edit_section(
                    OBLIGATORY_VARIABLES_METADATA,
                    "Obligatorisk",
                    short_name,
                    language,
                ),
                build_edit_section(
                    OPTIONAL_VARIABLES_METADATA,
                    "Anbefalt",
                    short_name,
                    language,
                ),
            )
            for short_name in short_names
        ]
"""
