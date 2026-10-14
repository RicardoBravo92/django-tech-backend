from tests.conftest import auth


def test_payment_marks_order_paid(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=auth(customer_token),
    )
    order_id = r.json()["id"]
    assert r.json()["status"] == "pending"

    r = client.post(
        f"/api/v1/payments/orders/{order_id}/pay",
        json={"method": "card"},
        headers=auth(customer_token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "succeeded"
    assert r.json()["reference"].startswith("mock-")

    r = client.get(f"/api/v1/orders/{order_id}", headers=auth(customer_token))
    assert r.json()["status"] == "paid"


def test_double_payment_conflict(client, product, customer_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=auth(customer_token),
    )
    order_id = r.json()["id"]
    client.post(
        f"/api/v1/payments/orders/{order_id}/pay",
        json={"method": "card"},
        headers=auth(customer_token),
    )
    r = client.post(
        f"/api/v1/payments/orders/{order_id}/pay",
        json={"method": "cash"},
        headers=auth(customer_token),
    )
    assert r.status_code == 409


def test_cannot_pay_others_order(client, product, customer_token, admin_token):
    r = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=auth(customer_token),
    )
    order_id = r.json()["id"]
    other_tok = client.post(
        "/api/v1/auth/login",
        json={"email": "otro2@huby.com", "password": "password123"},
    )
    if other_tok.status_code == 401:
        client.post(
            "/api/v1/auth/register",
            json={"email": "otro2@huby.com", "full_name": "Otro", "password": "password123"},
        )
        other_tok = client.post(
            "/api/v1/auth/login",
            json={"email": "otro2@huby.com", "password": "password123"},
        )
    r = client.post(
        f"/api/v1/payments/orders/{order_id}/pay",
        json={"method": "card"},
        headers=auth(other_tok.json()["access_token"]),
    )
    assert r.status_code == 403
