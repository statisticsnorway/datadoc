import pathlib
from typing import BinaryIO, Protocol

from dapla import AuthClient, FileClient
from gcsfs import GCSFileSystem

GCS_PROTOCOL_PREFIX = "gs://"


class GCSObject:
    def __init__(self, path: str):
        self.path: str = path

        if AuthClient.is_ready():
            # Running on Dapla, rely on dapla-toolbelt for auth
            self.fs = FileClient.get_gcs_file_system()
        else:
            # All other environments, rely on Standard Google credential system
            # If this doesn't work for you, try running the following commands:
            #
            # gcloud auth application-default revoke
            # gcloud auth application-default login
            self.fs = GCSFileSystem()

    def open(self) -> BinaryIO:
        return self.fs.open(self.path)


class LocalFile:
    def __init__(self, path):
        self.path: str = path
        self.path_object: pathlib.Path = pathlib.Path(path)

    def open(self) -> BinaryIO:
        return open(self.path, mode="rb")

    def write(self) -> None:
        ...


class StorageAdapter(Protocol):
    path: str

    @staticmethod
    def for_path(path: str):
        """
        Return a concrete class implementing this Protocol based on the structure of the path.
        """
        if path.startswith(GCS_PROTOCOL_PREFIX):
            return GCSObject(path)
        else:
            return LocalFile(path)

    def open(self) -> BinaryIO:
        ...
