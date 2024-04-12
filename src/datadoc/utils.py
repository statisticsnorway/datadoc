"""General utilities."""

from __future__ import annotations

import datetime
import importlib
from typing import TYPE_CHECKING
from typing import Any

from datadoc_model import model
from pydantic import AnyUrl

if TYPE_CHECKING:
    from datadoc.enums import SupportedLanguages

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"


def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook."""
    try:
        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")  # type: ignore [name-defined]
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer."""
    return round((completed / total) * 100)


def get_languagetext_from_languagestringtype(
    variable: list[dict[str, str]] | None,
    language: SupportedLanguages,
) -> str | None:
    """Return value from a LanguageStringType for given language."""
    root = variable
    if root:
        for i in root:
            if i["languageCode"] == language.value:
                return i["languageText"]
    else:
        msg = "Root is none"
        raise AssertionError(msg)
    return None


def get_display_values(
    variable: model.Variable,
    current_language: SupportedLanguages,
) -> dict[str, Any]:
    """Return a dictionary representation of Model.DataDocVariable with strings in the currently selected language."""
    return_dict = {}
    for field_name, value in variable:
        if isinstance(value, model.LanguageStringType):
            return_dict[field_name] = get_languagetext_from_languagestringtype(
                value.model_dump(),  # type: ignore [arg-type]
                current_language,
            )
        elif isinstance(value, AnyUrl):
            return_dict[field_name] = str(value)
        else:
            return_dict[field_name] = value
    return return_dict


def pick_random_port() -> int:
    """Pick a random free port number.

    The function will bind a socket to port 0, and a random free port from
    1024 to 65535 will be selected by the operating system.
    """
    import socket

    with socket.socket() as sock:
        sock.bind(("", 0))
        return int(sock.getsockname()[1])


def get_timestamp_now() -> datetime.datetime:
    """Return a timestamp for the current moment."""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_app_version() -> str:
    """Get the version of the Datadoc package."""
    return importlib.metadata.distribution("ssb-datadoc").version
