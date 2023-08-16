"""Perform operations on files stored with a range of technologies.

Defines a Protocol and the concrete implementations of it.
"""

from __future__ import annotations

import logging
import pathlib
import typing as t
from urllib.parse import urlsplit, urlunsplit

if t.TYPE_CHECKING:
    from io import IOBase, TextIOWrapper

GCS_PROTOCOL_PREFIX = "gs://"

logger = logging.getLogger(__name__)


class GCSObject:
    """Implementation of the Protocol 'StorageAdapter' for Google Cloud Storage."""

    def __init__(self: t.Self @ GCSObject, path: str) -> None:
        """Initialize the class."""
        self._url = urlsplit(path)
        try:
            from dapla import AuthClient, FileClient

            if AuthClient.is_ready():
                # Running on Dapla, rely on dapla-toolbelt for auth
                self.fs = FileClient.get_gcs_file_system()
            else:
                # All other environments, rely on Standard Google credential system
                # If this doesn't work for you, try running the following commands:
                #
                # gcloud auth application-default revoke
                # gcloud auth application-default login
                from gcsfs import GCSFileSystem

                self.fs = GCSFileSystem()

        except ImportError as e:
            msg = "Missing support for GCS. Install datadoc with 'pip install ssb-datadoc[gcs]'"
            raise ImportError(msg) from e

    def _rebuild_url(self: t.Self @ GCSObject, new_path: str | pathlib.Path) -> str:
        return urlunsplit(
            (self._url.scheme, self._url.netloc, str(new_path), None, None),
        )

    def open(self: t.Self @ GCSObject, **kwargs: dict[str, t.Any]) -> IOBase:
        """Return a file-like-object."""
        return self.fs.open(self.location, **kwargs)

    def parent(self: t.Self @ GCSObject) -> str:
        """Return the logical parent of this object."""
        parent = pathlib.Path(self._url.path).parent
        return self._rebuild_url(parent)

    def joinpath(self: t.Self @ GCSObject, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        self._url = urlsplit(
            self._rebuild_url(pathlib.Path(self._url.path) / part),
        )

    def exists(self: t.Self @ GCSObject) -> bool:
        """Return True if the object exists."""
        return self.fs.exists(self.location)

    def write_text(self: t.Self @ GCSObject, text: str) -> None:
        """Write the given text to disk."""
        f: TextIOWrapper
        with self.fs.open(self.location, mode="w") as f:
            f.write(text)

    @property
    def location(self: t.Self @ GCSObject) -> str:
        """Return a locator for this object."""
        return urlunsplit(self._url)


class LocalFile:
    """Implementation of the Protocol 'StorageAdapter' for file systems."""

    def __init__(self: t.Self @ LocalFile, path: str) -> None:
        """Initialize the class."""
        self._path_object: pathlib.Path = pathlib.Path(path)

    def open(self: t.Self @ LocalFile, **kwargs: dict[str, t.Any]) -> IOBase:
        """Return a file-like-object."""
        return pathlib.Path.open(str(self._path_object), **kwargs)

    def parent(self: t.Self @ LocalFile) -> str:
        """Return the parent of this file."""
        return str(self._path_object.resolve().parent)

    def joinpath(self: t.Self @ LocalFile, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        self._path_object = self._path_object.joinpath(part)

    def exists(self: t.Self @ LocalFile) -> bool:
        """Return True if the file exists."""
        return self._path_object.exists()

    def write_text(self: t.Self @ LocalFile, text: str) -> None:
        """Write the given text to disk."""
        self._path_object.write_text(text, encoding="utf-8")

    @property
    def location(self: t.Self @ LocalFile) -> str:
        """Return a locator for this object."""
        return str(self._path_object)


class StorageAdapter(t.Protocol):
    """Implement this Protocol for the technologies on which we store datasets and metadata documents."""

    @staticmethod
    def for_path(path: str | pathlib.Path) -> StorageAdapter:
        """Return a concrete class implementing this Protocol based on the structure of the path."""
        path = str(path)
        if path.startswith(GCS_PROTOCOL_PREFIX):
            return GCSObject(path)

        return LocalFile(path)

    def open(self: t.Self @ StorageAdapter, **kwargs: dict[str, t.Any]) -> IOBase:
        """Return a file-like-object."""
        ...

    def parent(self: t.Self @ StorageAdapter) -> str:
        """Return the logical parent of this instance."""
        ...

    def joinpath(self: t.Self @ StorageAdapter, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        ...

    def exists(self: t.Self @ StorageAdapter) -> bool:
        """Return True if the object exists."""
        ...

    def write_text(self: t.Self @ StorageAdapter, text: str) -> None:
        """Write the given text to disk."""
        ...

    @property
    def location(self: t.Self @ StorageAdapter) -> str:
        """Return a locator for this object."""
        ...
