"""Tests for the ModelBackwardsCompatibility class."""

import json
from pathlib import Path

import pytest

from datadoc.backend.datadoc_metadata import DataDocMetadata
from datadoc.backend.model_backwards_compatibility import (
    UnknownModelVersionError,
    upgrade_metadata,
)

from .utils import TEST_COMPATIBILITY_DIRECTORY

BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES = [
    d for d in TEST_COMPATIBILITY_DIRECTORY.iterdir() if d.is_dir()
]
BACKWARDS_COMPATIBLE_VERSION_NAMES = [
    d.stem for d in BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES
]


def test_existing_metadata_current_model_version():
    current_model_version = "2.0.0"
    fresh_metadata = {"document_version": current_model_version}
    upgraded_metadata = upgrade_metadata(fresh_metadata)
    assert upgraded_metadata == fresh_metadata


def test_existing_metadata_unknown_model_version():
    fresh_metadata = {"document_version": "0.27.65"}
    with pytest.raises(UnknownModelVersionError):
        upgrade_metadata(fresh_metadata)


@pytest.mark.parametrize(
    "existing_metadata_path",
    BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES,
    ids=BACKWARDS_COMPATIBLE_VERSION_NAMES,
)
@pytest.mark.usefixtures("remove_document_file")
def test_backwards_compatibility(
    existing_metadata_file: str,
    metadata: DataDocMetadata,
):
    with Path.open(Path(existing_metadata_file)) as f:
        file_metadata = json.loads(f.read())

    # Just test a single value to make sure we have a working model
    assert metadata.meta.dataset.name.en == file_metadata["dataset"]["name"]["en"]
