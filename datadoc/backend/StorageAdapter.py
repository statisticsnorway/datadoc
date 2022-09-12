import logging
import os
import pathlib
from io import IOBase, TextIOWrapper
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

GCS_PROTOCOL_PREFIX = "gs://"

logger = logging.getLogger(__name__)


class GCSObject:
    def __init__(self, path: str):
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

        except ImportError:
            msg = f"Missing support for GCS. Install datadoc with 'pip install ssb-datadoc[gcs]'"
            raise ImportError(msg)

    def _rebuild_url(self, new_path: str) -> str:
        return urlunsplit((self._url.scheme, self._url.netloc, new_path, None, None))

    def open(self, **kwargs) -> IOBase:
        return self.fs.open(self.location, **kwargs)

    def parent(self) -> str:
        parent = os.path.dirname(self._url.path)
        return self._rebuild_url(parent)

    def joinpath(self, part):
        """Modify the path in place"""
        self._url = urlsplit(self._rebuild_url(os.path.join(self._url.path, part)))

    def exists(self) -> bool:
        return self.fs.exists(self.location)

    def write_text(self, text: str) -> None:
        f: TextIOWrapper
        with self.fs.open(self.location, mode="w") as f:
            f.write(text)

    @property
    def location(self) -> str:
        return urlunsplit(self._url)


class LocalFile:
    def __init__(self, path):
        self._path_object: pathlib.Path = pathlib.Path(path)

    def open(self, **kwargs) -> IOBase:
        return open(str(self._path_object), **kwargs)

    def parent(self) -> str:
        return str(self._path_object.resolve().parent)

    def joinpath(self, part):
        """Modify the path in place"""
        self._path_object = self._path_object.joinpath(part)

    def exists(self) -> bool:
        return self._path_object.exists()

    def write_text(self, text: str) -> None:
        self._path_object.write_text(text, encoding="utf-8")

    @property
    def location(self) -> str:
        return str(self._path_object)


class StorageAdapter(Protocol):
    @staticmethod
    def for_path(path: str):
        """
        Return a concrete class implementing this Protocol based on the structure of the path.
        """
        if path.startswith(GCS_PROTOCOL_PREFIX):
            return GCSObject(path)
        else:
            return LocalFile(path)

    def open(self, **kwargs) -> IOBase:
        ...

    def parent(self) -> str:
        ...

    def joinpath(self, part: str) -> None:
        ...

    def exists(self) -> bool:
        ...

    def write_text(self, text: str) -> None:
        ...

    @property
    def location(self) -> str:
        ...
