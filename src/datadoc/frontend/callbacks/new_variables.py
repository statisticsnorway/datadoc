from datadoc import state
from datadoc.frontend.components.resources_test_new_variables import build_edit_section
from datadoc.frontend.components.resources_test_new_variables import build_ssb_accordion
from datadoc.frontend.fields.display_new_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_new_variables import OPTIONAL_VARIABLES_METADATA


def build_new_variables_workspace(metadata_variables: list) -> list:
    """Build variable workspace with accordions for variables."""
    return [
        build_ssb_accordion(
            variable.short_name,
            {"type": "variables-accordion", "id": variable.short_name},
            variable.short_name,
            children=[
                build_edit_section(
                    OBLIGATORY_VARIABLES_METADATA,
                    "Obligatorisk",
                    variable.short_name,
                    state.current_metadata_language.value,
                ),
                build_edit_section(
                    OPTIONAL_VARIABLES_METADATA,
                    "Anbefalt",
                    variable.short_name,
                    state.current_metadata_language.value,
                ),
            ],
        )
        for variable in metadata_variables
    ]
