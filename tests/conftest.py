"""Shared fixtures and configuration."""

from __future__ import annotations

import copy
import functools
import os
import pathlib
import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from bs4 import ResultSet
from datadoc_model import model

from datadoc import state
from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.backend.unit_types import UnitTypes
from datadoc.backend.user_info import TestUserInfo
from tests.backend.test_statistic_subject_mapping import (
    STATISTICAL_SUBJECT_STRUCTURE_DIR,
)
from tests.backend.test_unit_types import UNIT_TYPES_DIR

from .utils import TEST_EXISTING_METADATA_DIRECTORY
from .utils import TEST_EXISTING_METADATA_FILE_NAME
from .utils import TEST_PARQUET_FILEPATH
from .utils import TEST_RESOURCES_DIRECTORY
from .utils import TEST_RESOURCES_METADATA_DOCUMENT

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest import mock

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _clear_environment(mocker: MockerFixture) -> None:
    """Ensure that the environment is cleared."""
    mocker.patch.dict(os.environ, clear=True)


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["no_NO"]


@pytest.fixture()
def dummy_timestamp() -> datetime:
    return datetime(2022, 1, 1, tzinfo=timezone.utc)


@pytest.fixture()
def _mock_timestamp(mocker: MockerFixture, dummy_timestamp: datetime) -> None:
    mocker.patch(
        "datadoc.backend.datadoc_metadata.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture()
def _mock_user_info(mocker: MockerFixture) -> None:
    mocker.patch(
        "datadoc.backend.user_info.get_user_info_for_current_platform",
        return_value=TestUserInfo(),
    )


@pytest.fixture()
def metadata(
    _mock_timestamp: None,
    _mock_user_info: None,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
) -> DataDocMetadata:
    return DataDocMetadata(
        subject_mapping_fake_statistical_structure,
        str(TEST_PARQUET_FILEPATH),
    )


@pytest.fixture(autouse=True)
def remove_document_file() -> Generator[None, None, None]:
    # Yield so we only run teardown
    yield None
    if TEST_RESOURCES_METADATA_DOCUMENT.exists():
        TEST_RESOURCES_METADATA_DOCUMENT.unlink()


@pytest.fixture()
def existing_metadata_path() -> Path:
    return TEST_EXISTING_METADATA_DIRECTORY


@pytest.fixture()
def existing_metadata_file(existing_metadata_path: Path) -> str:
    # Setup by copying the file into the relevant directory
    shutil.copy(
        existing_metadata_path / TEST_EXISTING_METADATA_FILE_NAME,
        TEST_RESOURCES_METADATA_DOCUMENT,
    )
    return str(TEST_RESOURCES_METADATA_DOCUMENT)


@pytest.fixture()
def existing_metadata_with_valid_id_file(existing_metadata_file: Path) -> Path:
    return existing_metadata_file


@pytest.fixture(autouse=True)
def _clear_state() -> None:
    """Global fixture, referred to in pytest.ini."""
    try:
        del state.metadata
        del state.current_metadata_language
        del state.statistic_subject_mapping
    except AttributeError:
        pass


@pytest.fixture()
def mock_gcsfs_open(mocker: MockerFixture) -> mock.Mock:
    return mocker.patch("gcsfs.GCSFileSystem.open")


@pytest.fixture()
def mock_gcsfs_exists(mocker: MockerFixture) -> mock.Mock:
    mock = mocker.patch("gcsfs.GCSFileSystem.exists")
    mock.return_value = True
    return mock


@pytest.fixture()
def mock_pathlib_write_text(mocker: MockerFixture) -> mock.Mock:
    return mocker.patch("pathlib.Path.write_text")


ENGLISH_NAME = "English Name"
BOKMÅL_NAME = "Bokmål Name"
NYNORSK_NAME = "Nynorsk Name"


@pytest.fixture()
def english_name() -> str:
    return "English Name"


@pytest.fixture()
def bokmål_name() -> str:
    return "Bokmål navn"


@pytest.fixture()
def nynorsk_name() -> str:
    return "Nynorsk namn"


@pytest.fixture()
def language_object(english_name: str, bokmål_name: str) -> model.LanguageStringType:
    return model.LanguageStringType(en=english_name, nb=bokmål_name)


@pytest.fixture()
def existing_data_path() -> Path:
    return TEST_PARQUET_FILEPATH


@pytest.fixture()
def generate_periodic_file(
    existing_data_path: Path,
    insert_string: str,
) -> Generator[Path, None, None]:
    file_name = existing_data_path.name
    insert_pos = file_name.find("_v1")
    new_file_name = file_name[:insert_pos] + insert_string + file_name[insert_pos:]
    new_path = TEST_RESOURCES_DIRECTORY / new_file_name
    shutil.copy(existing_data_path, new_path)
    yield new_path
    if new_path.exists():
        new_path.unlink()


@pytest.fixture()
def full_dataset_state_path(
    path_parts_to_insert: str | list[str],
) -> pathlib.Path:
    """Create a longer path structure from just one section.

    Examples:
    >>> full_dataset_state_path('inndata')
    'tests/inndata/resources/person_data_v1.parquet'
    >>> full_dataset_state_path(['klargjorte_data', 'arbmark'])
    'tests/klargjorte_data/arbmark/resources/person_data_v1.parquet'
    """
    split_path = list(pathlib.Path(TEST_PARQUET_FILEPATH).parts)
    new_path = copy.copy(split_path)
    if isinstance(path_parts_to_insert, str):
        parts = [path_parts_to_insert]
    else:
        parts = path_parts_to_insert
    for p in parts:
        new_path.insert(-2, p)
    return pathlib.Path().joinpath(*new_path)


@pytest.fixture()
def copy_dataset_to_path(
    tmp_path: pathlib.Path,
    full_dataset_state_path: pathlib.Path,
) -> pathlib.Path:
    temporary_dataset = tmp_path / full_dataset_state_path
    temporary_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEST_PARQUET_FILEPATH, temporary_dataset)
    return temporary_dataset


@pytest.fixture()
def subject_xml_file_path() -> pathlib.Path:
    return (
        TEST_RESOURCES_DIRECTORY
        / STATISTICAL_SUBJECT_STRUCTURE_DIR
        / "extract_secondary_subject.xml"
    )


@pytest.fixture()
def subject_mapping_fake_statistical_structure(
    _mock_fetch_statistical_structure,
) -> StatisticSubjectMapping:
    return StatisticSubjectMapping("placeholder")


@pytest.fixture()
def _mock_fetch_statistical_structure(
    mocker,
    subject_xml_file_path: pathlib.Path,
) -> None:
    def fake_statistical_structure() -> ResultSet:
        with subject_xml_file_path.open() as f:
            return BeautifulSoup(f.read(), features="xml").find_all("hovedemne")

    mocker.patch(
        "datadoc.backend.statistic_subject_mapping.StatisticSubjectMapping._fetch_data_from_external_source",
        functools.partial(fake_statistical_structure),
    )


@pytest.fixture()
def subject_mapping_http_exception(
    requests_mock,
    exception_to_raise,
) -> StatisticSubjectMapping:
    requests_mock.get(
        "http://test.some.url.com",
        exc=exception_to_raise,
    )
    return StatisticSubjectMapping("http://test.some.url.com")


@pytest.fixture()
def unit_types_fake_structure(
    _mock_fetch_dataframe,
) -> UnitTypes:
    return UnitTypes(100)


@pytest.fixture()
def unit_types_csv_filepath_nb() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_nb.csv"


@pytest.fixture()
def unit_types_csv_filepath_nn() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_nn.csv"


@pytest.fixture()
def unit_types_csv_filepath_en() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / UNIT_TYPES_DIR / "unit_types_en.csv"


@pytest.fixture()
def _mock_fetch_dataframe(
    mocker,
    unit_types_csv_filepath_nb: pathlib.Path,
    unit_types_csv_filepath_nn: pathlib.Path,
    unit_types_csv_filepath_en: pathlib.Path,
) -> None:
    def fake_unit_types() -> dict[str, pd.DataFrame]:
        return {
            "nb": pd.read_csv(unit_types_csv_filepath_nb, converters={"code": str}),
            "nn": pd.read_csv(unit_types_csv_filepath_nn, converters={"code": str}),
            "en": pd.read_csv(unit_types_csv_filepath_en, converters={"code": str}),
        }

    mocker.patch(
        "datadoc.backend.unit_types.UnitTypes._fetch_data_from_external_source",
        functools.partial(fake_unit_types),
    )
