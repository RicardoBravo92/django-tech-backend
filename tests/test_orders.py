from decimal import Decimal

from tests.conftest import auth


def test_checkout_creates_order_with_tax(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=auth(customer_token),
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "pending"
    assert Decimal(data["subtotal"]) == Decimal("40.00")
    assert Decimal(data["tax_amount"]) == Decimal("7.20")
    assert Decimal(data["total"]) == Decimal("47.20")


def test_checkout_with_discount(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={
            "items": [{"product_id": product["id"], "quantity": 2}],
            "discount_percent": 10,
        },
        headers=auth(customer_token),
    )
    data = r.json()
    assert r.status_code == 201
    assert Decimal(data["discount_amount"]) == Decimal("4.00")
    assert Decimal(data["total"]) == Decimal("42.48")


def test_checkout_reduces_stock(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 3}]},
        headers=auth(customer_token),
    )
    assert r.status_code == 201
    r = client.get(f"/api/v1/products/{product['id']}")
    assert r.json()["stock"] == product["stock"] - 3


def test_checkout_insufficient_stock(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 9999}]},
        headers=auth(customer_token),
    )
    assert r.status_code == 409


def test_orders_are_private(client, product, customer_token, admin_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=auth(customer_token),
    )
    order_id = r.json()["id"]

    r = client.get(f"/api/v1/orders/{order_id}", headers=auth(customer_token))
    assert r.status_code == 200

    other = client.post(
        "/api/v1/auth/register",
        json={"email": "otro@huby.com", "full_name": "Otro", "password": "password123"},
    )
    other_tok = client.post(
        "/api/v1/auth/login",
        json={"email": "otro@huby.com", "password": "password123"},
    ).json()["access_token"]
    r = client.get(f"/api/v1/orders/{order_id}", headers=auth(other_tok))
    assert r.status_code == 403

    r = client.get(f"/api/v1/orders/{order_id}", headers=auth(admin_token))
    assert r.status_code == 200
