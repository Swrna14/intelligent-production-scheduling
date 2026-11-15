from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_frontend_origin_is_allowed_by_cors() -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_dashboard_summary_endpoint() -> None:
    response = client.get("/api/dashboard/summary")

    assert response.status_code == 200
    payload = response.json()
    assert "total_products" in payload
    assert "total_machines" in payload
    assert "total_orders" in payload
    assert "total_schedules" in payload


def test_schedule_run_endpoint() -> None:
    response = client.post("/api/scheduling/run", json={"scale": "starter", "seed": 20261022})

    assert response.status_code == 200
    payload = response.json()
    assert "feasible" in payload
    assert "assignments" in payload
    assert isinstance(payload["assignments"], list)


def test_dataset_endpoint_supports_pagination() -> None:
    response = client.get("/api/data/products?limit=2&offset=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset"] == "products"
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) <= 2


def test_schedule_run_rejects_unsupported_scale() -> None:
    response = client.post("/api/scheduling/run", json={"scale": "unknown", "seed": 20261022})

    assert response.status_code == 422
