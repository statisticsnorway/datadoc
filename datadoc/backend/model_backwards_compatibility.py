"""Upgrade old metadata files to be compatible with new versions of the datadoc model.

An important principle of Datadoc is that we ALWAYS guarantee backwards compatibility of existing metadata documents.
This means that we guarantee that a user will never lose data, even if their document is decades old.

For each document version we release with breaking changes, we implement a handler and register the version by defining a
BackwardsCompatibleVersion instance. These documents will then be upgraded when they're opened in Datadoc.

A test must also be implemented for each new version.
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from collections.abc import Callable

VERSION_FIELD_NAME = "document_version"


class UnknownModelVersionError(Exception):
    """Throw this error if we haven't seen the version before."""

    def __init__(
        self: t.Self @ UnknownModelVersionError,
        supplied_version: str,
        *args: tuple[t.Any, ...],
    ) -> None:
        """Initialize class."""
        super().__init__(args)
        self.supplied_version = supplied_version

    def __str__(self: t.Self @ UnknownModelVersionError) -> str:
        """Return string representation."""
        return f"Document Version ({self.supplied_version}) of discovered file is not supported"


SUPPORTED_VERSIONS: dict[str, BackwardsCompatibleVersion] = {}


@dataclass()
class BackwardsCompatibleVersion:
    """A version which we support with backwards compatibility."""

    version: str
    handler: Callable

    def __post_init__(self: t.Self @ BackwardsCompatibleVersion) -> None:
        """Register this version in the supported versions map."""
        SUPPORTED_VERSIONS[self.version] = self


def handle_current_version(supplied_metadata: dict) -> dict:
    """Nothing to do here."""
    return supplied_metadata


def handle_version_0_1_1(supplied_metadata: dict) -> dict:
    """Handle breaking changes for v0.1.1.

    PR ref: https://github.com/statisticsnorway/ssb-datadoc-model/pull/4.
    """
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
BackwardsCompatibleVersion(version="0.1.1", handler=handle_version_0_1_1)
BackwardsCompatibleVersion(
    version="1",
    handler=handle_version_0_1_1,
)  # Some documents exist with incorrect version specification


def upgrade_metadata(fresh_metadata: dict, current_model_version: str) -> dict:
    """Run the handler for this version to upgrade the document to the latest version."""
    # Special case for current version, we expose the current_model_version parameter for test purposes
    SUPPORTED_VERSIONS[current_model_version] = BackwardsCompatibleVersion(
        current_model_version,
        handle_current_version,
    )
    supplied_version = fresh_metadata[VERSION_FIELD_NAME]
    try:
        # Retrieve the upgrade function for this version
        upgrade = SUPPORTED_VERSIONS[supplied_version].handler
    except KeyError as e:
        raise UnknownModelVersionError(supplied_version) from e
    else:
        return upgrade(fresh_metadata)
