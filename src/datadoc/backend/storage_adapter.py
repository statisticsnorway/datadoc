"""Perform operations on files stored with a range of technologies.

Defines a Protocol and the concrete implementations of it.
"""

from __future__ import annotations

import logging
import pathlib
from typing import TYPE_CHECKING
from typing import Protocol
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from dapla import AuthClient
from dapla import FileClient

if TYPE_CHECKING:
    import os
    from io import IOBase
    from io import TextIOWrapper

GCS_PROTOCOL_PREFIX = "gs://"

logger = logging.getLogger(__name__)


class GCSObject:
    """Implementation of the Protocol 'StorageAdapter' for Google Cloud Storage."""

    def __init__(self, path: str | os.PathLike) -> None:
        """Initialize the class."""
        self._url = urlsplit(str(path))

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

    @staticmethod
    def for_path(path: str | os.PathLike) -> StorageAdapter:
        """Return an instance of this class instantiated for path."""
        return GCSObject(path)

    def _rebuild_url(self, new_path: str | os.PathLike) -> str:
        return urlunsplit(
            (self._url.scheme, self._url.netloc, str(new_path), None, None),
        )

    def open(self, **kwargs: str) -> IOBase:
        """Return a file-like-object."""
        return self.fs.open(self.location, **kwargs)

    def parent(self) -> str:
        """Return the logical parent of this object."""
        parent = pathlib.PurePosixPath(self._url.path).parent
        return self._rebuild_url(parent)

    def joinpath(self, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        self._url = urlsplit(
            self._rebuild_url(pathlib.Path(self._url.path) / part),
        )

    def exists(self) -> bool:
        """Return True if the object exists."""
        return self.fs.exists(self.location)

    def write_text(self, text: str) -> None:
        """Write the given text to disk."""
        f: TextIOWrapper
        with self.fs.open(self.location, mode="w") as f:
            f.write(text)

    @property
    def location(self) -> str:
        """Return a locator for this object."""
        return urlunsplit(self._url)


class LocalFile:
    """Implementation of the Protocol 'StorageAdapter' for file systems."""

    def __init__(self, path: str | os.PathLike) -> None:
        """Initialize the class."""
        self._path_object: pathlib.Path = pathlib.Path(path)

    @staticmethod
    def for_path(path: str | os.PathLike) -> StorageAdapter:
        """Return an instance of this class instantiated for path."""
        return LocalFile(path)

    def open(self, **kwargs: str) -> IOBase:
        """Return a file-like-object."""
        return pathlib.Path.open(self._path_object, **kwargs)  # type: ignore [call-overload]

    def parent(self) -> str:
        """Return the parent of this file."""
        return str(self._path_object.resolve().parent)

    def joinpath(self, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        self._path_object = self._path_object.joinpath(part)

    def exists(self) -> bool:
        """Return True if the file exists."""
        return self._path_object.exists()

    def write_text(self, text: str) -> None:
        """Write the given text to disk."""
        self._path_object.write_text(text, encoding="utf-8")

    @property
    def location(self) -> str:
        """Return a locator for this object."""
        return str(self._path_object)


class StorageAdapter(Protocol):
    """Implement this Protocol for the technologies on which we store datasets and metadata documents."""

    @staticmethod
    def for_path(path: str | os.PathLike) -> StorageAdapter:
        """Return a concrete class implementing this Protocol based on the structure of the path."""
        if str(path).startswith(GCS_PROTOCOL_PREFIX):
            return GCSObject(path)

        return LocalFile(path)

    def open(self, **kwargs: str) -> IOBase:
        """Return a file-like-object."""
        ...

    def parent(self) -> str:
        """Return the logical parent of this instance."""
        ...

    def joinpath(self, part: str) -> None:
        """Join 'part' onto the current path.

        In-place operation.
        """
        ...

    def exists(self) -> bool:
        """Return True if the object exists."""
        ...

    def write_text(self, text: str) -> None:
        """Write the given text to disk."""
        ...

    @property
    def location(self) -> str:
        """Return a locator for this object."""
        ...
