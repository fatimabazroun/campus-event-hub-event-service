from datetime import datetime, timedelta, timezone

import pytest

_API_KEY = "changeme-in-production"
_HEADERS = {"x-api-key": _API_KEY}


def _payload(**overrides) -> dict:
    now = datetime.now(timezone.utc)
    base = {
        "title": "Test Event",
        "description": "A test campus event",
        "location": "Campus Hall A",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
        "capacity": 100,
        "organizer_id": "user-123",
    }
    base.update(overrides)
    return base


# ── create ──────────────────────────────────────────────────────────────────

async def test_create_event_returns_201(client):
    resp = await client.post("/api/v1/events", json=_payload(), headers=_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Event"
    assert data["status"] == "draft"
    assert "id" in data


async def test_create_event_missing_api_key_returns_422(client):
    resp = await client.post("/api/v1/events", json=_payload())
    assert resp.status_code == 422


async def test_create_event_bad_api_key_returns_401(client):
    resp = await client.post("/api/v1/events", json=_payload(), headers={"x-api-key": "wrong"})
    assert resp.status_code == 401


async def test_create_event_end_before_start_returns_422(client):
    now = datetime.now(timezone.utc)
    resp = await client.post(
        "/api/v1/events",
        json=_payload(
            start_time=(now + timedelta(hours=2)).isoformat(),
            end_time=(now + timedelta(hours=1)).isoformat(),
        ),
        headers=_HEADERS,
    )
    assert resp.status_code == 422


# ── list ─────────────────────────────────────────────────────────────────────

async def test_list_events_empty(client):
    resp = await client.get("/api/v1/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_list_events_pagination(client):
    for i in range(3):
        await client.post("/api/v1/events", json=_payload(title=f"Event {i}"), headers=_HEADERS)

    resp = await client.get("/api/v1/events?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


# ── get ──────────────────────────────────────────────────────────────────────

async def test_get_event(client):
    create_resp = await client.post("/api/v1/events", json=_payload(), headers=_HEADERS)
    event_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/events/{event_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == event_id


async def test_get_event_not_found_returns_404(client):
    resp = await client.get("/api/v1/events/does-not-exist")
    assert resp.status_code == 404


# ── update ───────────────────────────────────────────────────────────────────

async def test_update_event(client):
    create_resp = await client.post("/api/v1/events", json=_payload(), headers=_HEADERS)
    event_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/events/{event_id}",
        json={"title": "Updated Title", "status": "published"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "published"


async def test_update_event_not_found_returns_404(client):
    resp = await client.put(
        "/api/v1/events/does-not-exist",
        json={"title": "X"},
        headers=_HEADERS,
    )
    assert resp.status_code == 404


# ── delete ───────────────────────────────────────────────────────────────────

async def test_delete_event(client):
    create_resp = await client.post("/api/v1/events", json=_payload(), headers=_HEADERS)
    event_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/events/{event_id}", headers=_HEADERS)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/events/{event_id}")
    assert get_resp.status_code == 404


async def test_delete_event_not_found_returns_404(client):
    resp = await client.delete("/api/v1/events/does-not-exist", headers=_HEADERS)
    assert resp.status_code == 404
