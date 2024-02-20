from __future__ import annotations

import logging
from typing import Protocol

from datadoc import config

logger = logging.getLogger(__name__)


PLACEHOLDER_EMAIL_ADDRESS = "default_user@ssb.no"


class UserInfo(Protocol):
    """Information about the current user.

    May be implemented for different platforms.
    """

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        ...


class UnknownUserInfo:
    """Fallback when no implementation is found."""

    @property
    def short_email(self) -> str | None:
        """Unknow email address."""
        return None


class TestUserInfo:
    """Information about the current user for local development and testing."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        return PLACEHOLDER_EMAIL_ADDRESS


class JupyterHubUserInfo:
    """Information about the current user when running on JupyterHub."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        return config.get_jupyterhub_user()


def get_user_info_for_current_platform() -> UserInfo:
    """Return the correct implementation of UserInfo for the current platform."""
    if JupyterHubUserInfo().short_email:
        return JupyterHubUserInfo()

    logger.warning(
        "Was not possible to retrieve user information! Some fields may not be set.",
    )
    return UnknownUserInfo()
