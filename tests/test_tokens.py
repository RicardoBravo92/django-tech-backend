from tests.conftest import auth


def test_refresh_token_rotation(client, customer_token):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "customer-test@huby.com", "password": "password123"},
    )
    refresh = r.json()["refresh_token"]

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    new_refresh = r.json()["refresh_token"]
    assert new_refresh != refresh

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401


def test_logout_revokes_refresh(client, customer_token):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "customer-test@huby.com", "password": "password123"},
    )
    refresh = r.json()["refresh_token"]

    r = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh},
        headers=auth(customer_token),
    )
    assert r.status_code == 204

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401
