from __future__ import annotations

import contextlib
import logging
from typing import Protocol

import jwt

from datadoc import config
from datadoc.enums import DaplaRegion
from datadoc.enums import DaplaService

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


class DaplaLabUserInfo:
    """Information about the current user when running on Dapla Lab."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        encoded_jwt = config.get_oidc_token()
        if encoded_jwt:
            # The JWT has been verified by the platform prior to injection, no need to verify.
            decoded_jwt = jwt.decode(encoded_jwt, options={"verify_signature": False})
            with contextlib.suppress(KeyError):
                # If email can't be found in the JWT, fall through and return None
                return decoded_jwt["email"]

        logger.warning(
            "Could not access JWT from environment. Could not get short email address.",
        )
        return None


class JupyterHubUserInfo:
    """Information about the current user when running on JupyterHub."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        return config.get_jupyterhub_user()


def get_user_info_for_current_platform() -> UserInfo:
    """Return the correct implementation of UserInfo for the current platform."""
    if config.get_dapla_region() == DaplaRegion.DAPLA_LAB:
        return DaplaLabUserInfo()
    elif config.get_dapla_service() == DaplaService.JUPYTERLAB:  # noqa: RET505
        return JupyterHubUserInfo()
    else:
        logger.warning(
            "Was not possible to retrieve user information! Some fields may not be set.",
        )
        return UnknownUserInfo()
