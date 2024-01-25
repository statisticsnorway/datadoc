"""Centralised configuration management for Datadoc."""
from __future__ import annotations

import os

from dotenv import dotenv_values

_config: dict[str, str | None] = {
    **dotenv_values(".env.default"),  # load default config
    **dotenv_values(".env.dev"),  # load local dev config
    **os.environ,  # override loaded values with environment variables
}


def get_jupyterhub_user() -> str | None:
    """Get the JupyterHub user name."""
    return _config.get("JUPYTERHUB_USER")
