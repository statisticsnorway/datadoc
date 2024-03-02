"""New variables tab.

Some attemps to get values from state, in use in some callbacks right now
"""

from __future__ import annotations

import logging

from datadoc import state
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


# First attempt with getting dropdown items, temporary move for testing new solution
# Very hard to get variable_short_name
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
    )
    def callback_change_language_variable_metadata_new_input(
    accordions: list,
    language: str,
) -> tuple[object, ...]:
    Update dataset metadata values upon change of language.
    variables_short_names = get_variables_short_names()
    return (
        *(
            e.options_getter(SupportedLanguages(language))
            for e in DISPLAYED_DROPDOWN_VARIABLES_METADATA
        ),
    ) * len(variables_short_names)

"""
