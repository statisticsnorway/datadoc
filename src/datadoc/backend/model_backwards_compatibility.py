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

import arrow

if TYPE_CHECKING:
    from collections.abc import Callable

VERSION_FIELD_NAME = "document_version"


class UnknownModelVersionError(Exception):
    """Exception raised for unknown model versions.

    This error is thrown when an unrecognized model version is encountered.
    """

    def __init__(
        self,
        supplied_version: str,
        *args: tuple[Any, ...],
    ) -> None:
        """Initialize the exception with the supplied version.

        Args:
            supplied_version: The version of the model that was not recognized.
            *args: Additional arguments for the Exception base class.
        """
        super().__init__(args)
        self.supplied_version = supplied_version

    def __str__(self) -> str:
        """Return string representation."""
        return f"Document Version ({self.supplied_version}) of discovered file is not supported"


SUPPORTED_VERSIONS: OrderedDict[str, BackwardsCompatibleVersion] = OrderedDict()


@dataclass()
class BackwardsCompatibleVersion:
    """A version which we support with backwards compatibility.

    This class registers a version and its corresponding handler function for backwards compatibility.
    """

    version: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def __post_init__(self) -> None:
        """Register this version in the supported versions map.

        This method adds the instance to the `SUPPORTED_VERSIONS` dictionary using the version as the key.
        """
        SUPPORTED_VERSIONS[self.version] = self


def handle_current_version(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle the current version of the metadata.

    This function returns the supplied metadata unmodified.

    Args:
        supplied_metadata: The metadata for the current version.

    Returns:
        dict[str, Any]: The unmodified supplied metadata.
    """
    return supplied_metadata


def _find_and_update_language_strings(supplied_metadata: dict | None) -> dict | None:
    """Find and update language-specific strings in the supplied metadata.

    This function iterates through the supplied metadata dictionary. For each key-value pair, if the value is
    a dictionary containing the key "en", it is passed to the `_convert_language_string_type` function to
    potentially update its format. The function then returns the modified metadata dictionary. If the supplied
    metadata is not a dictionary, it returns `None`.

    Args:
        supplied_metadata: A dictionary where values may include nested dictionaries with language-specific strings.

    Returns:
        Optional[dict]: The updated metadata dictionary with modified language strings, or `None` if the input is not a dictionary.
    """
    if isinstance(supplied_metadata, dict):
        for key, value in supplied_metadata.items():
            if isinstance(value, dict) and "en" in value:
                supplied_metadata[key] = _convert_language_string_type(value)
        return supplied_metadata
    return None


def _convert_language_string_type(supplied_value: dict) -> list[dict[str, str]]:
    """Convert a dictionary of language-specific strings to a list of dictionaries.

    This function takes a dictionary with language codes as keys and corresponding
    language-specific strings as values, and converts it to a list of dictionaries
    with 'languageCode' and 'languageText' keys.

    Args:
        supplied_value: A dictionary containing language codes as keys and their corresponding language strings as values.

    Returns:
        list[dict[str, str]]: A list of dictionaries, each containing 'languageCode' and 'languageText'
            keys, representing the converted language strings.
    """
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
    """Remove an element from the supplied metadata dictionary.

    This function deletes a specified element from the supplied metadata dictionary if it exists.

    Args:
        supplied_metadata: The metadata dictionary from which the element will be removed.
        element_to_remove: The key of the element to be removed from the metadata dictionary.
    """
    if element_to_remove in supplied_metadata:
        del supplied_metadata[element_to_remove]


def _cast_to_date_type(value_to_update: str | None) -> str | None:
    """Convert a string to a date string in ISO format.

    This function takes a string representing a date and converts it to a date string in ISO format.
    If the input is `None`, it returns `None` without modification.

    Args:
        value_to_update: A string representing a date or `None`.

    Returns:
        Optional[str]: The date string in ISO format if the input was a valid date string, or `None` if the input was `None`.
    """
    if value_to_update is None:
        return value_to_update

    return str(
        arrow.get(
            value_to_update,
        ).date(),
    )


def handle_version_3_3_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.3.0.

    Remove field 'direct person identifying'

    This function modifies the supplied metadata to accommodate breaking changes introduced in version 4.0.0 for version 3.3.0.
    Specifically, it removes the 'direct_person_identifying' field from each variable in 'datadoc.variables'
    and updates the 'document_version' field to "4.0.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        dict[str, Any]: The updated metadata dictionary.
    """
    for i in range(len(supplied_metadata["datadoc"]["variables"])):
        _remove_element_from_model(
            supplied_metadata["datadoc"]["variables"][i],
            "direct_person_identifying",
        )
    supplied_metadata["datadoc"]["document_version"] = "4.0.0"
    return supplied_metadata


def handle_version_3_2_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.3.0.

    Update the type of contains_data_* fields.

    Update the type of 'contains_data_*' fields to date strings.

    This function updates the 'contains_data_from' and 'contains_data_until' fields in the 'datadoc.dataset'
    and 'datadoc.variables' sections of the supplied metadata dictionary to ensure they are stored as date strings.
    It also updates the 'document_version' field to "3.3.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        dict[str, Any]: The updated metadata dictionary.
    """
    fields = ["contains_data_from", "contains_data_until"]
    for field in fields:
        supplied_metadata["datadoc"]["dataset"][field] = _cast_to_date_type(
            supplied_metadata["datadoc"]["dataset"].get(field, None),
        )
        for v in supplied_metadata["datadoc"]["variables"]:
            v[field] = _cast_to_date_type(v.get(field, None))

    supplied_metadata["datadoc"]["document_version"] = "3.3.0"
    return supplied_metadata


def handle_version_3_1_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 3.1.0.

    This function updates the 'data_source' field in both the 'dataset' and 'variables' sections of the supplied
    metadata dictionary. Specifically, it extracts the 'languageText' from the first element of the 'data_source'
    list and converts it to a string. The 'document_version' field is also updated to "3.2.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        dict[str, Any]: The updated metadata dictionary.
    """
    data: list = supplied_metadata["datadoc"]["dataset"]["data_source"]

    if data is not None:
        supplied_metadata["datadoc"]["dataset"]["data_source"] = str(
            data[0]["languageText"],
        )

    for i in range(len(supplied_metadata["datadoc"]["variables"])):
        data = supplied_metadata["datadoc"]["variables"][i]["data_source"]
        if data is not None:
            supplied_metadata["datadoc"]["variables"][i]["data_source"] = str(
                data[0]["languageText"],
            )

    supplied_metadata["datadoc"]["document_version"] = "3.2.0"
    return supplied_metadata


def handle_version_2_2_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 2.2.0.

    This function updates the 'subject_field' in the 'dataset' section of the supplied metadata dictionary by converting it to a string.
    The value is chosen based on the first non-null language field among 'nb', 'nn', and 'en'. It also removes the 'register_uri' field from the 'dataset'.
    Additionally, it removes 'sentinel_value_uri' from each variable, sets 'special_value' and 'custom_type' fields to None, and updates language strings in the 'variables' and 'dataset' sections.
    The 'document_version' is updated to "3.1.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated. It is expected to contain a nested structure with 'datadoc', 'dataset', and 'variables'.

    Returns:
        dict[str, Any]: The updated metadata dictionary.


    """
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
    """Add container for previous versions.

    Add a container structure for previous versions of metadata.
    This function wraps the existing metadata in a new container structure that includes the 'document_version', 'datadoc', and 'pseudonymization' fields.
    The 'document_version' is set to "0.0.1" and 'pseudonymization' is set to None.

    Args:
        existing_metadata: The original metadata dictionary to be wrapped. Returns: dict: A new dictionary containing the wrapped metadata with additional fields.
    """
    return {
        "document_version": "0.0.1",
        "datadoc": existing_metadata,
        "pseudonymization": None,
    }


def handle_version_2_1_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for version 2.1.0.

    This function updates the 'owner' field in the 'dataset' section of the supplied metadata dictionary by converting it from a LanguageStringType to a string.
    The value is chosen based on the first non-null language field among 'nb', 'nn', and 'en'.
    The 'document_version' is updated to "2.2.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        dict[str, Any]: The updated metadata dictionary with the 'owner' field modified and 'document_version' set to "2.2.0".
    """
    data = supplied_metadata["dataset"]["owner"]
    supplied_metadata["dataset"]["owner"] = str(data["nb"] or data["nn"] or data["en"])
    supplied_metadata["document_version"] = "2.2.0"
    return add_container(supplied_metadata)


def handle_version_1_0_0(supplied_metadata: dict[str, Any]) -> dict[str, Any]:
    """Handle breaking changes for v1.0.0.

    Handle breaking changes for version 1.0.0. This function updates the date fields 'metadata_created_date' and 'metadata_last_updated_date' to ISO 8601 format with UTC timezone.
    It also converts the 'data_source' field from a string to a dictionary with language keys if necessary and removes the 'data_source_path' field.
    The 'document_version' is updated to "2.1.0".

    'data_source' field converted (if needed), 'data_source_path' removed, and 'document_version' set to "2.1.0".

    Args:
        supplied_metadata: The metadata dictionary to be updated.

    Returns:
        dict[str, Any]: The updated metadata dictionary with date fields modified.

    """
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
)  # A container must be created at this version
BackwardsCompatibleVersion(version="2.2.0", handler=handle_version_2_2_0)
BackwardsCompatibleVersion(version="3.1.0", handler=handle_version_3_1_0)
BackwardsCompatibleVersion(version="3.2.0", handler=handle_version_3_2_0)
BackwardsCompatibleVersion(version="3.3.0", handler=handle_version_3_3_0)
BackwardsCompatibleVersion(version="4.0.0", handler=handle_current_version)


def upgrade_metadata(fresh_metadata: dict[str, Any]) -> dict[str, Any]:
    """Run the handler for this version to upgrade the document to the latest version.

    Upgrade the metadata to the latest version using registered handlers.
    This function checks the version of the provided metadata and applies a series of upgrade handlers to migrate the metadata to the latest version.
    It starts from the provided version and applies all subsequent handlers in sequence.
    If the metadata is already in the latest version or the version cannot be determined, appropriate actions are taken.

    Args:
        fresh_metadata: The metadata dictionary to be upgraded. This dictionary must include version information that determines which handlers to apply.

    Returns:
        dict[str, Any]: The upgraded metadata dictionary, after applying all necessary handlers.

    Raises:
        UnknownModelVersionError: If the metadata's version is unknown or unsupported.
    """
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

    "Check if the metadata is organized in the container structure.
    Metadata might be organized in a 'container' structure, which includes fields like 'datadoc' and 'pseudonymization'.
    This function determines if the given metadata dictionary follows this container structure by checking for the presence of the 'datadoc' field.

    Args:
        metadata: The metadata dictionary to check.

    Returns:
        bool: True if the metadata is in the container structure (i.e., contains the 'datadoc' field), False otherwise.
    """
    return "datadoc" in metadata
