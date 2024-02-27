import pytest

from datadoc.backend.unit_types import UnitTypes
from tests.utils import TEST_RESOURCES_DIRECTORY

TEST_UNIT_TYPES_DIR = "unit_types"


@pytest.mark.parametrize(
    ("unit_types_csv_filepath", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / TEST_UNIT_TYPES_DIR / "unit_types.csv",
            [
                "Adresse",
                "Arbeidsulykke",
                "Bolig",
                "Bygning",
                "Eiendom",
                "Familie",
                "Foretak",
                "Fylke (forvaltning)",
                "Fylke (geografisk)",
                "Havneanløp",
                "Husholdning",
                "Kjøretøy",
                "Kommune (forvaltning)",
                "Kommune (geografisk)",
                "Kurs",
                "Lovbrudd",
                "Person",
                "Skip",
                "Statlig virksomhet",
                "Storfe",
                "Trafikkulykke",
                "Transaksjon",
                "Valg",
                "Vare/tjeneste",
                "Verdipapir",
                "Virksomhet",
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / TEST_UNIT_TYPES_DIR / "empty.csv",
            [],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_dataframe")
def test_read_dataframe(
    unit_types_fake_structure: UnitTypes,
    expected: list[str],
):
    unit_types_fake_structure.wait_for_external_result()
    assert unit_types_fake_structure.classifications == expected


def test_no_source_url():
    unit_types = UnitTypes(None)
    unit_types.wait_for_external_result()
    assert unit_types.classifications == []
