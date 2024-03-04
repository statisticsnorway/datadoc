import functools
import pathlib

import pandas as pd
import pytest

from datadoc.backend.unit_types import UnitTypes
from tests.utils import TEST_RESOURCES_DIRECTORY

TEST_UNIT_TYPES_DIR = "unit_types"


@pytest.fixture()
def _mock_fetch_dataframe(
    mocker,
    unit_types_csv_filepath: pathlib.Path,
) -> None:
    def fake_unit_types() -> pd.DataFrame:
        return pd.read_csv(unit_types_csv_filepath)

    mocker.patch(
        "datadoc.backend.unit_types.UnitTypes._fetch_data_from_external_source",
        functools.partial(fake_unit_types),
    )


@pytest.fixture()
def unit_types_fake_structure(
    _mock_fetch_dataframe,
) -> UnitTypes:
    return UnitTypes(100)


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


def test_non_existent_code():
    unit_types = UnitTypes(0)
    unit_types.wait_for_external_result()
    assert unit_types.classifications == []
