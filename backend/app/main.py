from __future__ import annotations

import asyncio
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from . import schemas
from .monitoring import run_check
from .storage import InMemoryStore


store = InMemoryStore()
app = FastAPI(title="MonoTaur API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Devices
@app.get("/devices", response_model=List[schemas.Device])
def list_devices():
    return store.list_devices()


@app.post("/devices", response_model=schemas.Device, status_code=201)
def create_device(payload: schemas.DeviceCreate):
    return store.create_device(payload)


@app.patch("/devices/{device_id}", response_model=schemas.Device)
def update_device(device_id: UUID, payload: schemas.DeviceUpdate):
    if device_id not in store.devices:
        raise HTTPException(status_code=404, detail="device not found")
    return store.update_device(device_id, payload)


@app.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: UUID):
    store.delete_device(device_id)


# Layouts
@app.get("/layouts", response_model=List[schemas.Layout])
def list_layouts():
    return store.list_layouts()


@app.post("/layouts", response_model=schemas.Layout, status_code=201)
def create_layout(payload: schemas.LayoutCreate):
    return store.create_layout(payload)


@app.patch("/layouts/{layout_id}", response_model=schemas.Layout)
def update_layout(layout_id: UUID, payload: schemas.LayoutUpdate):
    if layout_id not in store.layouts:
        raise HTTPException(status_code=404, detail="layout not found")
    return store.update_layout(layout_id, payload)


@app.delete("/layouts/{layout_id}", status_code=204)
def delete_layout(layout_id: UUID):
    store.delete_layout(layout_id)


# Links
@app.get("/links", response_model=List[schemas.Link])
def list_links():
    return store.list_links()


@app.post("/links", response_model=schemas.Link, status_code=201)
def create_link(payload: schemas.LinkCreate):
    if payload.source_device_id == payload.target_device_id:
        raise HTTPException(status_code=400, detail="link endpoints must be different devices")
    for device_id in (payload.source_device_id, payload.target_device_id):
        if device_id not in store.devices:
            raise HTTPException(status_code=400, detail="link endpoints must reference existing devices")
    return store.create_link(payload)


@app.patch("/links/{link_id}", response_model=schemas.Link)
def update_link(link_id: UUID, payload: schemas.LinkUpdate):
    if link_id not in store.links:
        raise HTTPException(status_code=404, detail="link not found")
    return store.update_link(link_id, payload)


@app.delete("/links/{link_id}", status_code=204)
def delete_link(link_id: UUID):
    store.delete_link(link_id)


# Checks
@app.get("/checks", response_model=List[schemas.Check])
def list_checks():
    return store.list_checks()


@app.post("/checks", response_model=schemas.Check, status_code=201)
def create_check(payload: schemas.CheckCreate):
    if payload.device_id not in store.devices:
        raise HTTPException(status_code=400, detail="device_id must reference an existing device")
    return store.create_check(payload)


@app.get("/checks/{check_id}", response_model=schemas.Check)
def get_check(check_id: UUID):
    if check_id not in store.checks:
        raise HTTPException(status_code=404, detail="check not found")
    return store.get_check(check_id)


@app.patch("/checks/{check_id}", response_model=schemas.Check)
def update_check(check_id: UUID, payload: schemas.CheckUpdate):
    if check_id not in store.checks:
        raise HTTPException(status_code=404, detail="check not found")
    return store.update_check(check_id, payload)


@app.delete("/checks/{check_id}", status_code=204)
def delete_check(check_id: UUID):
    store.delete_check(check_id)


@app.post("/checks/{check_id}/run", response_model=schemas.CheckResult)
async def execute_check(check_id: UUID):
    if check_id not in store.checks:
        raise HTTPException(status_code=404, detail="check not found")
    check = store.get_check(check_id)
    result = await run_check(check)
    store.record_check_result(check_id, result)
    return result


# WebSocket stub for streaming monitoring events
@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_json({"type": "welcome", "message": "MonoTaur mock stream"})
        while True:
            await asyncio.sleep(5)
            await websocket.send_json({"type": "heartbeat", "active_devices": len(store.devices)})
    except WebSocketDisconnect:
        return
