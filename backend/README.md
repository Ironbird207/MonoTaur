# MonoTaur Backend (FastAPI prototype)

This directory contains a lightweight FastAPI application that sketches the APIs described in the project README and architecture notes. It uses an in-memory store so you can quickly exercise device, layout, link, and monitoring check flows without a database.

## Features
- REST endpoints for devices, layouts, links, and monitoring checks
- CORS enabled for local frontend experiments
- WebSocket stub that emits a welcome payload and periodic heartbeats
- A simple ICMP check executor that shells out to `ping` to validate reachability
- Basic pytest coverage for the health check, CRUD, and check execution happy paths

## Running locally
1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. (Optional) Define a check and run it once:
   ```bash
   http POST :8000/devices name=loopback ip_address=127.0.0.1 type=host
   http POST :8000/checks device_id=<device-id> target=127.0.0.1 type=icmp interval_s=5 timeout_ms=1000
   http POST :8000/checks/<check-id>/run
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
