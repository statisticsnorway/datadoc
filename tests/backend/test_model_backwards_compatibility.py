"""Tests for the ModelBackwardsCompatibility class."""

import json
from pathlib import Path

import pytest

from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.model_backwards_compatibility import UnknownModelVersionError
from datadoc.backend.model_backwards_compatibility import add_container
from datadoc.backend.model_backwards_compatibility import handle_version_2_2_0
from datadoc.backend.model_backwards_compatibility import (
    is_metadata_in_container_structure,
)
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from tests.utils import TEST_COMPATIBILITY_DIRECTORY
from tests.utils import TEST_EXISTING_METADATA_FILE_NAME

BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES = [
    d for d in TEST_COMPATIBILITY_DIRECTORY.iterdir() if d.is_dir()
]
BACKWARDS_COMPATIBLE_VERSION_NAMES = [
    d.stem for d in BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES
]


def test_existing_metadata_current_model_version():
    current_model_version = "3.1.0"
    fresh_metadata = {"document_version": current_model_version}
    upgraded_metadata = upgrade_metadata(fresh_metadata)
    assert upgraded_metadata == fresh_metadata


def test_handle_version_2_2_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v2_2_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_2_2_0(fresh_metadata)
    assert "custom_type" in upgraded_metadata["datadoc"]["dataset"]
    assert "custom_type" in upgraded_metadata["datadoc"]["variables"][0]
    assert "special_value" in upgraded_metadata["datadoc"]["variables"][0]


def test_existing_metadata_unknown_model_version():
    fresh_metadata = {"document_version": "0.27.65"}
    with pytest.raises(UnknownModelVersionError):
        upgrade_metadata(fresh_metadata)


@pytest.mark.parametrize(
    "existing_metadata_path",
    BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES,
    ids=BACKWARDS_COMPATIBLE_VERSION_NAMES,
)
def test_backwards_compatibility(
    existing_metadata_file: Path,
    metadata: DataDocMetadata,
):
    with existing_metadata_file.open() as f:
        file_metadata = json.loads(f.read())

    if is_metadata_in_container_structure(file_metadata):
        file_metadata = file_metadata["datadoc"]

    # Just test a single value to make sure we have a working model
    assert metadata.dataset.name.root[0].languageText == file_metadata["dataset"]["name"]["en"]  # type: ignore [union-attr, index]


def test_add_container():
    doc = {
        "percentage_complete": 98,
        "document_version": "2.1.0",
        "dataset": {"short_name": "person_data_v1", "assessment": "SENSITIVE"},
    }
    doc_with_container = add_container(doc)
    assert doc_with_container["document_version"] == "0.0.1"
    assert doc_with_container["datadoc"]["document_version"] == "2.1.0"
    assert "pseudonymization" in doc_with_container
