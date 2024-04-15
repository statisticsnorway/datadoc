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


def _find_and_update_language_strings(supplied_metadata: dict | None) -> dict | None:
    if isinstance(supplied_metadata, dict):
        for key, value in supplied_metadata.items():
            if isinstance(value, dict) and "en" in value:
                supplied_metadata[key] = _convert_language_string_type(value)
        return supplied_metadata
    return None


def _convert_language_string_type(supplied_value: dict) -> list[dict[str, str]]:
    return [
        {
            "languageCode": "en",
            "languageText": supplied_value["en"],
        },
        {
            "languageCode": "nn",
            "languageText": supplied_value["nn"],
        },
        {
            "languageCode": "nb",
            "languageText": supplied_value["nb"],
        },
    ]


def _remove_element_from_model(
    supplied_metadata: dict[str, Any],
    element_to_remove: str,
) -> None:
    if element_to_remove in supplied_metadata:
        del supplied_metadata[element_to_remove]


def handle_version_2_2_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for v2.2.0."""
    if supplied_metadata["datadoc"]["dataset"]["subject_field"] is not None:
        data = supplied_metadata["datadoc"]["dataset"]["subject_field"]
        supplied_metadata["datadoc"]["dataset"]["subject_field"] = str(
            data["nb"] or data["nn"] or data["en"],
        )

    _remove_element_from_model(supplied_metadata["datadoc"]["dataset"], "register_uri")

    for i in range(len(supplied_metadata["datadoc"]["variables"])):
        _remove_element_from_model(
            supplied_metadata["datadoc"]["variables"][i],
            "sentinel_value_uri",
        )
        supplied_metadata["datadoc"]["variables"][i]["special_value"] = None
        supplied_metadata["datadoc"]["variables"][i]["custom_type"] = None
        supplied_metadata["datadoc"]["variables"][
            i
        ] = _find_and_update_language_strings(
            supplied_metadata["datadoc"]["variables"][i],
        )
    supplied_metadata["datadoc"]["dataset"]["custom_type"] = None
    supplied_metadata["datadoc"]["dataset"] = _find_and_update_language_strings(
        supplied_metadata["datadoc"]["dataset"],
    )
    supplied_metadata["datadoc"]["document_version"] = "3.1.0"
    return supplied_metadata


def add_container(existing_metadata: dict) -> dict:
    """Add container for previous versions."""
    return {
        "document_version": "0.0.1",
        "datadoc": existing_metadata,
        "pseudonymization": None,
    }


def handle_version_2_1_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for v2.1.0.

    Datatype changed from LanguageStringType to str for owner
    """
    data = supplied_metadata["dataset"]["owner"]
    supplied_metadata["dataset"]["owner"] = str(data["nb"] or data["nn"] or data["en"])
    supplied_metadata["document_version"] = "2.2.0"
    return add_container(supplied_metadata)


def handle_version_1_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for v1.0.0."""
    datetime_fields = [("metadata_created_date"), ("metadata_last_updated_date")]
    for field in datetime_fields:
        if supplied_metadata["dataset"][field]:
            supplied_metadata["dataset"][field] = datetime.isoformat(
                datetime.fromisoformat(supplied_metadata["dataset"][field]).astimezone(
                    tz=timezone.utc,
                ),
                timespec="seconds",
            )
    if isinstance(supplied_metadata["dataset"]["data_source"], str):
        supplied_metadata["dataset"]["data_source"] = {
            "en": supplied_metadata["dataset"]["data_source"],
            "nn": "",
            "nb": "",
        }

    _remove_element_from_model(supplied_metadata["dataset"], "data_source_path")

    supplied_metadata["document_version"] = "2.1.0"
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

    key_renaming = [("data_type", "datatype")]

    for i in range(len(supplied_metadata["variables"])):
        for new_key, old_key in key_renaming:
            supplied_metadata["variables"][i][new_key] = supplied_metadata["variables"][
                i
            ].pop(
                old_key,
            )

    return supplied_metadata


# Register all the supported versions and their handlers.
# MUST be ordered from oldest to newest.
BackwardsCompatibleVersion(version="0.1.1", handler=handle_version_0_1_1)
BackwardsCompatibleVersion(version="1.0.0", handler=handle_version_1_0_0)
BackwardsCompatibleVersion(
    version="2.1.0",
    handler=handle_version_2_1_0,
)  # Her må det lages container
BackwardsCompatibleVersion(version="2.2.0", handler=handle_version_2_2_0)
BackwardsCompatibleVersion(version="3.1.0", handler=handle_current_version)


def upgrade_metadata(fresh_metadata: dict[str, Any]) -> dict[str, Any]:
    """Run the handler for this version to upgrade the document to the latest version."""
    # Special case for current version, we expose the current_model_version parameter for test purposes

    if is_metadata_in_container_structure(fresh_metadata):
        if fresh_metadata["datadoc"] is None:
            return fresh_metadata
        supplied_version = fresh_metadata["datadoc"][VERSION_FIELD_NAME]
    else:
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


def is_metadata_in_container_structure(
    metadata: dict,
) -> bool:
    """At a certain point a metadata 'container' was introduced.

    The container provides a structure for different 'types' of metadata, such as 'datadoc', 'pseudonymization' etc.
    This method returns True if the metadata is in the container structure, False otherwise.
    """
    return "datadoc" in metadata
