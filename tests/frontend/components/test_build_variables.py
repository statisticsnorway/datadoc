"""Test new variables functions to build layout."""

import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

ACCORDION_TYPE = "variables-accordion"


@pytest.mark.parametrize(
    ("accordion"),
    [
        build_ssb_accordion(
            "pers_id",
            {"type": ACCORDION_TYPE, "id": "pers_id"},
            "pers_id",
            [],
        ),
        build_ssb_accordion(
            "sykepenger",
            {"type": ACCORDION_TYPE, "id": "sykepenger"},
            "sykepenger",
            OPTIONAL_VARIABLES_METADATA,
        ),
        build_ssb_accordion(
            "ber_bruttoformue",
            {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
            "ber_bruttoformue",
            OBLIGATORY_VARIABLES_METADATA,
        ),
        build_ssb_accordion(
            "hoveddiagnose",
            {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
            "hoveddiagnose",
            [],
        ),
        build_ssb_accordion(
            "",
            {"type": ACCORDION_TYPE, "id": ""},
            "ber_bruttoformue",
            OBLIGATORY_VARIABLES_METADATA,
        ),
    ],
)
def test_build_ssb_accordion(accordion):
    assert accordion.id["type"] == ACCORDION_TYPE
    assert accordion.id["id"] == accordion.header
    assert isinstance(accordion, ssb.Accordion)
