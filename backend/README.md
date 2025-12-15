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
You can run the backend tests with the helper script, which will create a local virtual environment, install dependencies, and
invoke pytest:

```bash
./scripts/run_backend_tests.sh
```

> If your environment uses an HTTP(S) proxy or blocks outbound network traffic, dependency installation may fail. Configure
> pip with your proxy (`pip install --proxy https://proxy:port -r backend/requirements.txt`) or pre-download wheels before
> running the script.
