import pytest

from datadoc import state
from datadoc.enums import SupportedLanguages
from datadoc.frontend.fields.display_dataset import get_statistical_subject_options
from datadoc.frontend.fields.display_dataset import get_unit_type_options
from tests.backend.test_code_list import CODE_LIST_DIR
from tests.backend.test_statistic_subject_mapping import (
    STATISTICAL_SUBJECT_STRUCTURE_DIR,
)
from tests.utils import TEST_RESOURCES_DIRECTORY


@pytest.mark.parametrize(
    ("subject_xml_file_path", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY
            / STATISTICAL_SUBJECT_STRUCTURE_DIR
            / "extract_secondary_subject.xml",
            [
                {"label": "aa norwegian - aa00 norwegian", "value": "aa00"},
                {"label": "aa norwegian - aa01 norwegian", "value": "aa01"},
                {"label": "ab norwegian - ab00 norwegian", "value": "ab00"},
                {"label": "ab norwegian - ab01 norwegian", "value": "ab01"},
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY
            / STATISTICAL_SUBJECT_STRUCTURE_DIR
            / "missing_language.xml",
            [
                {"label": " - aa00 norwegian", "value": "aa00"},
                {"label": " - aa01 norwegian", "value": "aa01"},
                {"label": " - ab00 norwegian", "value": "ab00"},
                {"label": " - ", "value": "ab01"},
            ],
        ),
    ],
)
def test_get_statistical_subject_options(
    subject_mapping_fake_statistical_structure,
    expected,
):
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    state.statistic_subject_mapping.wait_for_external_result()
    assert get_statistical_subject_options(SupportedLanguages.NORSK_BOKMÅL) == expected


@pytest.mark.parametrize(
    ("unit_types_csv_filepath_nb", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "unit_types_nb.csv",
            [
                {"label": "Adresse", "value": "01"},
                {"label": "Arbeidsulykke", "value": "02"},
                {"label": "Bolig", "value": "03"},
            ],
        ),
    ],
)
def test_get_unit_type_options(
    unit_types_fake_structure,
    expected,
):
    state.unit_types = unit_types_fake_structure
    state.unit_types.wait_for_external_result()
    assert get_unit_type_options(SupportedLanguages.NORSK_BOKMÅL) == expected
