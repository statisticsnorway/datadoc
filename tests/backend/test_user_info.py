import string

import jwt
import pytest
from faker import Faker

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


@pytest.fixture()
def raw_jwt_payload(faker: Faker) -> dict[str, object]:
    user_name = "".join(faker.random_sample(elements=string.ascii_lowercase, length=3))
    email = f"{user_name}@ssb.no"
    first_name = faker.first_name()
    last_name = faker.last_name()
    return {
        "exp": faker.unix_time(),
        "iat": faker.unix_time(),
        "auth_time": faker.unix_time(),
        "jti": faker.uuid4(),
        "iss": faker.url(),
        "aud": [
            faker.word(),
            faker.uuid4(),
            "broker",
            "account",
        ],
        "sub": faker.uuid4(),
        "typ": "Bearer",
        "azp": "onyxia",
        "session_state": faker.uuid4(),
        "allowed-origins": ["*"],
        "realm_access": {
            "roles": [faker.word(), faker.word()],
        },
        "resource_access": {
            "broker": {"roles": [faker.word()]},
            "account": {
                "roles": [faker.word()],
            },
        },
        "scope": "openid email profile",
        "sid": faker.uuid4(),
        "email_verified": True,
        "name": f"{first_name} {last_name}",
        "short_username": f"ssb-{user_name}",
        "preferred_username": email,
        "given_name": first_name,
        "family_name": last_name,
        "email": email,
    }


@pytest.fixture()
def fake_jwt(raw_jwt_payload):
    return jwt.encode(raw_jwt_payload, "test secret", algorithm="HS256")


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


def test_dapla_lab_user_info_short_email(fake_jwt: str, raw_jwt_payload, monkeypatch):
    monkeypatch.setenv("OIDC_TOKEN", fake_jwt)
    assert DaplaLabUserInfo().short_email == raw_jwt_payload["email"]
