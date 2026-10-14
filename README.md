# tech-backend-django

A Django + Django REST Framework backend.

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (or plain `pip`)
- PostgreSQL 17 (optional for tests — they use in-memory SQLite)

## Setup

```bash
# create the virtualenv and install dependencies
uv sync

# create your local environment file
copy .env.example .env     # (cp on macOS/Linux)
```

All configuration is read from environment variables (optionally loaded from
`.env`) — see [`config/settings/base.py`](config/settings/base.py).

> **JWT tokens.** Access tokens are HS256 and signed with `SECRET_KEY`; the
> payload is `{"sub": "<user_id>", "exp": ...}`.

## Running

```bash
# migrations
uv run python manage.py migrate

# dev server (http://127.0.0.1:8000)
uv run python manage.py runserver
```

Settings modules: `config.settings.development` (default),
`config.settings.production`, `config.settings.test`.

## Docker

A PostgreSQL service plus the API container:

```bash
# build and start (http://localhost:8000)
docker compose up --build

# production override (adds Caddy for HTTPS; start from .env.prod.example)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Migrations run automatically on startup; the API is served with `gunicorn`
(`config.wsgi:application`).

## Tests

The test suite lives in `tests/` and uses in-memory SQLite with rate limiting
disabled:

```bash
uv run pytest
```

`tests/conftest.py` provides a small adapter around Django's test client so the
tests can use `client.post(..., json=..., headers=...)` and `response.json()`.

## Project layout

```
config/                 # settings, root urls, wsgi/asgi
  settings/
    base.py             # env loading, DRF config, throttling
    development.py
    production.py
    test.py             # SQLite in-memory, throttling off
apps/
  common/               # custom exceptions, pagination, permissions, throttles
  users/                # User, RefreshToken, PasswordResetToken, JWT auth, email
  catalog/              # Brand, Category
  products/             # Product, ProductSpec, ProductStock
  warehouses/           # Warehouse + stock service
  orders/               # Order, OrderItem, Payment (+ payment endpoints)
  reports/              # sales / sales-by-day / best-sellers / profit
tests/                  # test suite
Dockerfile              # uv + gunicorn image
docker-compose.yml      # db + backend (dev)
docker-compose.prod.yml # db + backend + Caddy (prod)
Caddyfile               # reverse proxy / TLS
```

## API

Base path is `/api/v1` (paths have **no trailing slash**):

| Area       | Routes |
|------------|--------|
| Health     | `GET /health` |
| Auth       | `POST /auth/login`, `/auth/register`, `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password`, `GET /auth/me` |
| Users      | `GET/POST /users`, `GET /users/<id>` |
| Catalog    | `/categories`, `/brands` (public read, admin write) |
| Products   | `GET/POST /products`, `GET/PATCH/DELETE /products/<id>` |
| Orders     | `POST /orders`, `GET /orders/me`, `GET /orders/<id>` |
| Payments   | `POST /payments/orders/<id>/pay`, `GET /payments/orders/<id>` |
| Reports    | `GET /reports/sales`, `/reports/sales/daily`, `/reports/best-sellers`, `/reports/profit` (admin) |
| Warehouses | `GET/POST /warehouses`, `PATCH/DELETE /warehouses/<id>`, `GET/PUT /warehouses/products/<product_id>/stock` (admin) |

### Authentication & authorisation

- Missing/invalid token → `401`
- Valid token but inactive user → `403`
- Authenticated but wrong role → `403`

### Numeric formatting

`Decimal` values are serialised as **strings** (e.g. `"40.00"`). Report
endpoints return plain objects whose decimals become JSON numbers.

## Known deviations

- **Request-body validation errors** return DRF's `400` with a field-keyed body
  rather than a `422` error envelope. The routes, success payloads and status
  codes for valid requests are identical; only the shape of malformed-request
  errors differs.
