import pytest

from datadoc.backend.unit_types import UnitType
from datadoc.backend.unit_types import UnitTypes
from tests.utils import TEST_RESOURCES_DIRECTORY

UNIT_TYPES_DIR = "unit_types"


@pytest.mark.parametrize(
    (
        "unit_types_csv_filepath_nb",
        "unit_types_csv_filepath_nn",
        "unit_types_csv_filepath_en",
        "expected",
    ),
    [
        (
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_nb.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_nn.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_en.csv",
            [
                UnitType(
                    titles={
                        "nb": "Adresse",
                        "nn": "Adresse",
                        "en": "Adresse",
                    },
                    unit_code="01",
                ),
                UnitType(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": "Arbeidsulykke",
                        "en": "Arbeidsulykke",
                    },
                    unit_code="02",
                ),
                UnitType(
                    titles={
                        "nb": "Bolig",
                        "nn": "Bolig",
                        "en": "Bolig",
                    },
                    unit_code="03",
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "empty.csv",
            [],
        ),
        (
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_nb.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "empty.csv",
            [
                UnitType(
                    titles={
                        "nb": "Adresse",
                        "nn": None,
                        "en": None,
                    },
                    unit_code="01",
                ),
                UnitType(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": None,
                        "en": None,
                    },
                    unit_code="02",
                ),
                UnitType(
                    titles={
                        "nb": "Bolig",
                        "nn": None,
                        "en": None,
                    },
                    unit_code="03",
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "no_code.csv",
            [
                UnitType(
                    titles={
                        "nb": "Adresse",
                        "nn": "Adresse",
                        "en": "Adresse",
                    },
                    unit_code=None,
                ),
                UnitType(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": "Arbeidsulykke",
                        "en": "Arbeidsulykke",
                    },
                    unit_code=None,
                ),
                UnitType(
                    titles={
                        "nb": "Bolig",
                        "nn": "Bolig",
                        "en": "Bolig",
                    },
                    unit_code=None,
                ),
            ],
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
