import pytest

from datadoc.backend.src.code_list import CodeList
from datadoc.backend.src.code_list import CodeListItem
from datadoc.backend.tests.utils import TEST_RESOURCES_DIRECTORY

CODE_LIST_DIR = "code_list"


@pytest.mark.parametrize(
    (
        "code_list_csv_filepath_nb",
        "code_list_csv_filepath_nn",
        "code_list_csv_filepath_en",
        "expected",
    ),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nn.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_en.csv",
            [
                CodeListItem(
                    titles={
                        "nb": "Adresse",
                        "nn": "Adresse",
                        "en": "Adresse",
                    },
                    code="01",
                ),
                CodeListItem(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": "Arbeidsulykke",
                        "en": "Arbeidsulykke",
                    },
                    code="02",
                ),
                CodeListItem(
                    titles={
                        "nb": "Bolig",
                        "nn": "Bolig",
                        "en": "Bolig",
                    },
                    code="03",
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "empty.csv",
            [],
        ),
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "empty.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "empty.csv",
            [
                CodeListItem(
                    titles={
                        "nb": "Adresse",
                        "nn": None,
                        "en": None,
                    },
                    code="01",
                ),
                CodeListItem(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": None,
                        "en": None,
                    },
                    code="02",
                ),
                CodeListItem(
                    titles={
                        "nb": "Bolig",
                        "nn": None,
                        "en": None,
                    },
                    code="03",
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            [
                CodeListItem(
                    titles={
                        "nb": "Adresse",
                        "nn": "Adresse",
                        "en": "Adresse",
                    },
                    code=None,
                ),
                CodeListItem(
                    titles={
                        "nb": "Arbeidsulykke",
                        "nn": "Arbeidsulykke",
                        "en": "Arbeidsulykke",
                    },
                    code=None,
                ),
                CodeListItem(
                    titles={
                        "nb": "Bolig",
                        "nn": "Bolig",
                        "en": "Bolig",
                    },
                    code=None,
                ),
            ],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_dataframe")
def test_read_dataframe(
    code_list_fake_structure: CodeList,
    expected: list[str],
):
    code_list_fake_structure.wait_for_external_result()
    assert code_list_fake_structure.classifications == expected


def test_non_existent_code(thread_pool_executor):
    code_list = CodeList(thread_pool_executor, 0)
    code_list.wait_for_external_result()
    assert code_list.classifications == []
