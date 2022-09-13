from datadoc_model import Model
from datadoc_model.Enums import SupportedLanguages


def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook"""
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # type: ignore
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer"""
    return round((completed / total) * 100)


def get_display_values(
    variable: Model.DataDocVariable, current_language: SupportedLanguages
) -> dict:
    """Return a dictionary representation of Model.DataDocVariable with strings in
    the currently selected language"""
    return_dict = {}
    for field_name, value in variable:
        if isinstance(value, Model.LanguageStrings):
            value = value.dict()[current_language.value]
        return_dict[field_name] = value
    return return_dict


def pick_random_port():
    """Pick a random free port number. The function will bind a socket to port 0, and
    a random free port from 1024 to 65535 will be selected by the operating system."""
    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]
