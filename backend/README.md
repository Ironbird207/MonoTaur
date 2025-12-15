# MonoTaur Backend (FastAPI prototype)

This directory contains a lightweight FastAPI application that sketches the APIs described in the project README and architecture notes. It uses an in-memory store so you can quickly exercise device, layout, and link CRUD flows without a database.

## Features
- REST endpoints for devices, layouts, and links
- CORS enabled for local frontend experiments
- WebSocket stub that emits a welcome payload and periodic heartbeats
- Basic pytest coverage for the health check and CRUD happy path

## Running locally
1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. Explore the interactive docs at http://localhost:8000/docs

## Tests
```bash
python -m pytest backend/tests
```
