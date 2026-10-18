"""API tests for the login endpoint.

These hit the live API, so they are opt-in: they run only when
``DILI_RUN_API_TESTS=1`` (keeps CI off production, per the audit). Run with:

    DILI_RUN_API_TESTS=1 pytest -m api
"""

from __future__ import annotations

import os

import pytest

requests = pytest.importorskip("requests")

pytestmark = pytest.mark.api

API_URL = os.environ.get("DILI_API_URL", "https://api.diliai.com/auth/login/")

run_api = pytest.mark.skipif(
    os.environ.get("DILI_RUN_API_TESTS") != "1",
    reason="set DILI_RUN_API_TESTS=1 to run live API tests",
)


@run_api
@pytest.mark.parametrize(
    "payload",
    [
        {"username": "qa-invalid-user@example.com", "password": "not-a-real-password"},
        {"username": "abc", "password": "x"},
        {},
    ],
    ids=["unknown-user", "non-email", "empty-object"],
)
def test_invalid_login_returns_consistent_error(payload):
    r = requests.post(API_URL, json=payload, timeout=15)
    assert r.status_code == 400
    body = r.json()
    assert body == {"errors": {"login": "Invalid username or password"}}


@run_api
@pytest.mark.xfail(
    reason="AUDIT finding #1: empty-string credentials returned 200 + a token; "
    "this asserts the intended behaviour and should fail until the backend is fixed",
    strict=False,
)
def test_empty_string_credentials_are_rejected():
    r = requests.post(API_URL, json={"username": "", "password": ""}, timeout=15)
    assert r.status_code == 400, f"empty credentials should be rejected, got {r.status_code}"
