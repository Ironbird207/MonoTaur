from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.main import app
from backend.app.storage import InMemoryStore

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    # each test starts with a clean in-memory store
    main.store = InMemoryStore()
    yield


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_device_and_layout_and_link():
    device_payload = {"name": "router-1", "ip_address": "192.0.2.1", "type": "router"}
    resp = client.post("/devices", json=device_payload)
    assert resp.status_code == 201
    device = resp.json()
    UUID(device["id"])  # validates UUID

    layout_payload = {"name": "lab", "background": "osm", "devices": []}
    resp = client.post("/layouts", json=layout_payload)
    assert resp.status_code == 201
    layout = resp.json()
    UUID(layout["id"])

    link_payload = {
        "source_device_id": device["id"],
        "target_device_id": device["id"],
    }
    resp = client.post("/links", json=link_payload)
    assert resp.status_code == 400  # cannot link device to itself

    second_device = client.post(
        "/devices", json={"name": "switch", "ip_address": "192.0.2.2", "type": "switch"}
    ).json()
    resp = client.post(
        "/links",
        json={
            "source_device_id": device["id"],
            "target_device_id": second_device["id"],
            "label": "uplink",
        },
    )
    assert resp.status_code == 201
    link = resp.json()
    assert link["label"] == "uplink"

    resp = client.get("/links")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_checks_can_run_icmp_ping():
    device_payload = {"name": "loopback", "ip_address": "127.0.0.1", "type": "host"}
    device = client.post("/devices", json=device_payload).json()

    check_payload = {
        "device_id": device["id"],
        "target": "127.0.0.1",
        "type": "icmp",
        "interval_s": 5,
        "timeout_ms": 1000,
    }
    resp = client.post("/checks", json=check_payload)
    assert resp.status_code == 201
    check = resp.json()

    run_resp = client.post(f"/checks/{check['id']}/run")
    assert run_resp.status_code == 200
    result = run_resp.json()
    assert result["status"] in {"up", "down", "unknown"}
    assert "checked_at" in result

    get_resp = client.get(f"/checks/{check['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["last_result"]["status"] == result["status"]


def test_checks_validate_device():
    payload = {
        "device_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "target": "192.0.2.55",
        "type": "icmp",
    }
    resp = client.post("/checks", json=payload)
    assert resp.status_code == 400
