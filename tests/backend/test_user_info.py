import pytest

from datadoc.backend import user_info
from datadoc.backend.user_info import PLACEHOLDER_EMAIL_ADDRESS
from datadoc.backend.user_info import DaplaLabUserInfo
from datadoc.backend.user_info import JupyterHubUserInfo
from datadoc.backend.user_info import UnknownUserInfo
from datadoc.backend.user_info import UserInfo
from datadoc.config import DAPLA_REGION
from datadoc.config import DAPLA_SERVICE
from datadoc.config import JUPYTERHUB_USER
from datadoc.enums import DaplaRegion
from datadoc.enums import DaplaService


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value", "expected_class"),
    [
        (DAPLA_SERVICE, DaplaService.JUPYTERLAB, JupyterHubUserInfo),
        (DAPLA_REGION, DaplaRegion.DAPLA_LAB, DaplaLabUserInfo),
        (None, None, UnknownUserInfo),
    ],
)
def test_get_user_info_for_current_platform(
    monkeypatch,
    environment_variable_name: str,
    environment_variable_value: str,
    expected_class: type[UserInfo],
):
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)
    assert isinstance(user_info.get_user_info_for_current_platform(), expected_class)


def test_jupyterhub_user_info_short_email(monkeypatch):
    monkeypatch.setenv(JUPYTERHUB_USER, PLACEHOLDER_EMAIL_ADDRESS)
    assert JupyterHubUserInfo().short_email == PLACEHOLDER_EMAIL_ADDRESS


def test_dapla_lab_user_info_short_email():
    assert DaplaLabUserInfo().short_email == "expected_value"
