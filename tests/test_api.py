from fastapi.testclient import TestClient

from app.main import app, _events, _events_lock

client = TestClient(app)


def setup_function() -> None:
    with _events_lock:
        _events.clear()


def test_health_and_readiness() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}


def test_ingest_and_retrieve_event() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "source": "test-agent",
            "title": "Suspicious login",
            "description": "Repeated failed login attempts",
            "severity": "high",
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["source"] == "test-agent"
    assert created["severity"] == "high"
    assert created["id"]

    fetched = client.get(f"/api/v1/events/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_filter_events_by_severity() -> None:
    client.post("/api/v1/events", json={"source": "a", "title": "Notice", "severity": "low"})
    client.post("/api/v1/events", json={"source": "b", "title": "Alert", "severity": "critical"})

    response = client.get("/api/v1/events", params={"severity": "critical"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Alert"


def test_invalid_event_is_rejected() -> None:
    response = client.post("/api/v1/events", json={"source": "", "title": " "})
    assert response.status_code == 422


def test_unknown_event_returns_404() -> None:
    response = client.get("/api/v1/events/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
