"""Upgrade old metadata files to be compatible with new versions of the datadoc model.

An important principle of Datadoc is that we ALWAYS guarantee backwards compatibility of existing metadata documents.
This means that we guarantee that a user will never lose data, even if their document is decades old.

For each document version we release with breaking changes, we implement a handler and register the version by defining a
BackwardsCompatibleVersion instance. These documents will then be upgraded when they're opened in Datadoc.

A test must also be implemented for each new version.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Any

from datadoc_model.model import LanguageStringType

if TYPE_CHECKING:
    from collections.abc import Callable

VERSION_FIELD_NAME = "document_version"


class UnknownModelVersionError(Exception):
    """Throw this error if we haven't seen the version before."""

    def __init__(
        self,
        supplied_version: str,
        *args: tuple[Any, ...],
    ) -> None:
        """Initialize class."""
        super().__init__(args)
        self.supplied_version = supplied_version

    def __str__(self) -> str:
        """Return string representation."""
        return f"Document Version ({self.supplied_version}) of discovered file is not supported"


SUPPORTED_VERSIONS: OrderedDict[str, BackwardsCompatibleVersion] = OrderedDict()


@dataclass()
class BackwardsCompatibleVersion:
    """A version which we support with backwards compatibility."""

    version: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def __post_init__(self) -> None:
        """Register this version in the supported versions map."""
        SUPPORTED_VERSIONS[self.version] = self


def handle_current_version(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Nothing to do here."""
    return supplied_metadata


def handle_version_1_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for v1.0.0."""
    datetime_fields = [
        ("metadata_created_date"),
        ("metadata_last_updated_date"),
    ]
    for field in datetime_fields:
        if supplied_metadata["dataset"][field]:
            supplied_metadata["dataset"][field] = datetime.isoformat(
                datetime.fromisoformat(supplied_metadata["dataset"][field]).astimezone(
                    tz=timezone.utc,
                ),
                timespec="seconds",
            )

    if isinstance(supplied_metadata["dataset"]["data_source"], str):
        supplied_metadata["dataset"]["data_source"] = LanguageStringType(
            en=supplied_metadata["dataset"]["data_source"],
        )
    supplied_metadata["document_version"] = "2.0.0"

    return supplied_metadata


def handle_version_0_1_1(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
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

    # Replace empty strings with None, empty strings are not valid for LanguageStrings values
    supplied_metadata["dataset"] = {
        k: None if v == "" else v for k, v in supplied_metadata["dataset"].items()
    }
    return supplied_metadata


# Register all the supported versions and their handlers.
# MUST be ordered from oldest to newest.
BackwardsCompatibleVersion(version="0.1.1", handler=handle_version_0_1_1)
BackwardsCompatibleVersion(
    version="1.0.0",
    handler=handle_version_1_0_0,
)
BackwardsCompatibleVersion(
    version="2.0.0",
    handler=handle_current_version,
)


def upgrade_metadata(fresh_metadata: dict[str, Any]) -> dict[str, Any]:
    """Run the handler for this version to upgrade the document to the latest version."""
    # Special case for current version, we expose the current_model_version parameter for test purposes
    supplied_version = fresh_metadata[VERSION_FIELD_NAME]
    start_running_handlers = False

    # Run all the handlers in order from the supplied version onwards
    for k, v in SUPPORTED_VERSIONS.items():
        if k == supplied_version:
            start_running_handlers = True
        if start_running_handlers:
            fresh_metadata = v.handler(fresh_metadata)

    if not start_running_handlers:
        raise UnknownModelVersionError(supplied_version)

    return fresh_metadata
