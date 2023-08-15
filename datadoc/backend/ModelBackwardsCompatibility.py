from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

VERSION_FIELD_NAME = "document_version"


class UnknownModelVersionError(Exception):
    def __init__(self, supplied_version, *args) -> None:
        super().__init__(args)
        self.supplied_version = supplied_version

    def __str__(self) -> str:
        return f"Document Version ({self.supplied_version}) of discovered file is not supported"


SUPPORTED_VERSIONS: dict[str, BackwardsCompatibleVersion] = {}


@dataclass()
class BackwardsCompatibleVersion:
    version_string: int
    upgrade_function: Callable

    def __post_init__(self):
        SUPPORTED_VERSIONS[self.version_string] = self


def handle_current_version(supplied_metadata: dict) -> dict:
    """Nothing to do here."""
    return supplied_metadata


def handle_version_0_1_1(supplied_metadata: dict) -> dict:
    """Handles changes made in this PR: https://github.com/statisticsnorway/ssb-datadoc-model/pull/4."""
    key_renaming = [
        ("metadata_created_date", "created_date"),
        ("metadata_created_by", "created_by"),
        ("metadata_last_updated_date", "last_updated_date"),
        ("metadata_last_updated_by", "last_updated_by"),
    ]
    for new_key, old_key in key_renaming:
        supplied_metadata["dataset"][new_key] = supplied_metadata["dataset"].pop(
            old_key,
        )
    return supplied_metadata


# Register all the supported versions and their handlers
BackwardsCompatibleVersion("0.1.1", handle_version_0_1_1)
BackwardsCompatibleVersion(
    "1",
    handle_version_0_1_1,
)  # Some documents exist with incorrect version specification


def upgrade_metadata(fresh_metadata: dict, current_model_version: str) -> dict:
    # Special case for current version, we expose the current_model_version parameter for test purposes
    SUPPORTED_VERSIONS[current_model_version] = BackwardsCompatibleVersion(
        current_model_version,
        handle_current_version,
    )
    supplied_version = fresh_metadata[VERSION_FIELD_NAME]
    try:
        # Retrieve the upgrade function for this version
        upgrade = SUPPORTED_VERSIONS[supplied_version].upgrade_function
    except KeyError:
        raise UnknownModelVersionError(supplied_version)  # noqa TC200
    else:
        return upgrade(fresh_metadata)
