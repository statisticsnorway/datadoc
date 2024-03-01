"""New variables tab."""

from __future__ import annotations

from datadoc import state
from datadoc.utils import get_display_values


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
