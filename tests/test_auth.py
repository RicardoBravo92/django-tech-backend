from tests.conftest import auth


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_catalog_is_public(client, product):
    r = client.get("/api/v1/products")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    r = client.get("/api/v1/products?search=Producto")
    assert r.status_code == 200


def test_catalog_write_requires_admin(client, product, customer_token):
    r = client.post(
        "/api/v1/products",
        json={"sku": "X", "name": "X", "slug": "x", "sale_price": 1},
        headers=auth(customer_token),
    )
    assert r.status_code == 403


def test_register_and_login(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "nuevo@huby.com", "full_name": "Nuevo", "password": "password123"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "customer"

    r = client.post(
        "/api/v1/auth/login",
        json={"email": "nuevo@huby.com", "password": "password123"},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["refresh_token"]


def test_login_bad_password(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-test@huby.com", "password": "incorrecta"},
    )
    assert r.status_code == 401


def test_unauthenticated_access(client):
    r = client.get("/api/v1/orders/me")
    assert r.status_code == 401


def test_auth_me(client, customer_token):
    r = client.get("/api/v1/auth/me", headers=auth(customer_token))
    assert r.status_code == 200
    assert r.json()["email"] == "customer-test@huby.com"
