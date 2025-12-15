from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


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
