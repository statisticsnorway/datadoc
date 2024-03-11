import pytest

from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

ACCORDION_TYPE = "variables-accordion"


@pytest.mark.parametrize(
    ("header", "key", "variable_shortname", "input_list"),
    [
        (
            "pers_id",
            {"type": ACCORDION_TYPE, "id": "pers_id"},
            "pers_id",
            [],
        ),
        (
            "sykepenger",
            {"type": ACCORDION_TYPE, "id": "sykepenger"},
            "sykepenger",
            OPTIONAL_VARIABLES_METADATA,
        ),
        (
            "ber_bruttoformue",
            {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
            "ber_bruttoformue",
            OBLIGATORY_VARIABLES_METADATA,
        ),
        (
            "hoveddiagnose",
            {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
            "hoveddiagnose",
            [],
        ),
        (
            "",
            {"type": ACCORDION_TYPE, "id": ""},
            "ber_bruttoformue",
            OBLIGATORY_VARIABLES_METADATA,
        ),
    ],
)
def test_build_ssb_accordion(header, key, variable_short_name, input_list):
    accordion = build_ssb_accordion(header, key, variable_short_name, input_list)
    assert accordion.id == key
