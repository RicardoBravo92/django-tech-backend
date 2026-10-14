"""Test fixtures.

Django's test client needs three small adjustments:

* JSON bodies are sent as ``content_type="application/json"`` + ``data=<str>``
  instead of a ``json=`` keyword argument;
* response objects expose ``.content`` (bytes) but have no ``.json()`` helper;
* auth headers must be passed as ``HTTP_*`` extra kwargs.

``TestClient`` below is a thin adapter so the tests read naturally with
``client.post(..., json=..., headers=...)`` and ``r.json()``.
"""
from __future__ import annotations

import json as _json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client as DjangoClient

from apps.users.models import UserRole

User = get_user_model()


class _Response:
    def __init__(self, django_response):
        self._response = django_response
        self.status_code = django_response.status_code
        self.content = django_response.content
        self.headers = django_response.headers

    def json(self):
        raw = self._response.content.decode("utf-8")
        return _json.loads(raw) if raw else None


class TestClient:
    """Minimal adapter matching the subset of the test client used here."""

    def __init__(self):
        self._client = DjangoClient()

    def _request(
        self,
        method,
        path,
        json=None,
        headers=None,
        data=None,
        content_type=None,
    ):
        kwargs = {}
        if headers:
            for key, value in headers.items():
                kwargs["HTTP_" + key.upper().replace("-", "_")] = value
        if json is not None:
            kwargs["data"] = _json.dumps(json)
            kwargs["content_type"] = "application/json"
        elif data is not None:
            kwargs["data"] = data
            if content_type:
                kwargs["content_type"] = content_type

        response = getattr(self._client, method)(path, **kwargs)
        return _Response(response)

    def get(self, path, **kwargs):
        return self._request("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("post", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("put", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("delete", path, **kwargs)


@pytest.fixture(autouse=True)
def _mock_email():
    """Never hit the real Resend API.

    Patching ``resend.Emails.send`` (rather than our own ``_send`` wrapper)
    keeps the real ``_send`` in the loop, so call-signature bugs surface.
    """
    with patch("resend.Emails.send"):
        yield


def _token(client, email, password):
    r = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return r.json()["access_token"]


@pytest.fixture()
def client(db):
    return TestClient()


@pytest.fixture()
def admin_token(client):
    user = User.objects.filter(email="admin-test@huby.com").first()
    if not user:
        user = User.objects.create_user(
            email="admin-test@huby.com",
            full_name="Admin Test",
            password="password123",
            role=UserRole.ADMIN,
        )
    return _token(client, "admin-test@huby.com", "password123")


@pytest.fixture()
def customer_token(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "customer-test@huby.com",
            "full_name": "Customer",
            "password": "password123",
        },
    )
    if r.status_code == 409:
        pass
    else:
        assert r.status_code == 201
    return _token(client, "customer-test@huby.com", "password123")


@pytest.fixture()
def product(client, admin_token):
    import uuid

    uid = uuid.uuid4().hex[:8]
    r = client.post(
        "/api/v1/products",
        json={
            "sku": f"TST-{uid}",
            "name": f"Producto Test {uid}",
            "slug": f"producto-test-{uid}",
            "cost_price": 10,
            "sale_price": 20,
            "stock": 50,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201
    return r.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}
