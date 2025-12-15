# Architecture Overview

This document outlines how MonoTaur can deliver a map-centric network monitoring experience.

## Frontend
- **Framework**: React + TypeScript for maintainability and component reuse.
- **Map Rendering**: Leaflet or MapLibre with a custom layer for device nodes and edges. Context menus enable right-click add/edit/delete operations. Drag-and-drop support updates node coordinates in persisted layouts.
- **State Management**: React Query for server state and optimistic updates when moving nodes or editing device details.
- **Realtime Updates**: WebSocket client to consume polling results and push status badges and link utilization changes without full refreshes.
- **Uploads & Backgrounds**: File upload to store floor-plan/rack images; toggle to switch to OSM tiles.

## Backend
- **API Layer**: FastAPI serving REST endpoints for devices, checks, links, and map layouts. WebSocket endpoint for streaming monitoring results and alerts.
- **Persistence**: PostgreSQL for inventory data (devices, checks, layouts, links). Migrations handled by Alembic.
- **Task Processing**: Celery or RQ workers executing scheduled polls. The scheduler enqueues ICMP/SNMP/HTTP checks at configurable intervals.
- **Monitoring Checks**:
  - **ICMP**: Ping with latency and packet loss metrics; timeout/threshold controls per device.
  - **SNMP**: Interface counters (ifInOctets/ifOutOctets) for utilization, and device info (sysName/sysDescr). Supports v2c and v3 profiles.
  - **HTTP/HTTPS (optional)**: Health-check endpoints for devices exposing web services.
- **Alerting**: Threshold rules stored per check with status transitions (OK/WARN/CRIT). Alerts are emitted to WebSocket clients and recorded in an alerts table for history.

## Data Model (high level)
- **Device**: id, name, type, ip/hostname, SNMP profile, coordinates (x, y) within a layout.
- **Check**: id, device_id, type (icmp, snmp, http), interval, parameters (timeout, community, OIDs), thresholds.
- **Layout**: id, name, background (uploaded image or map tiles), list of devices with positions.
- **Link**: id, source_device_id, target_device_id, interface mappings (source ifIndex, target ifIndex) for utilization overlay.
- **Metric Sample**: timestamped check result with status, latency, packet loss, bandwidth counters, or HTTP status.

## API Sketch
- `GET /api/devices` / `POST /api/devices` / `PATCH /api/devices/{id}` / `DELETE /api/devices/{id}`
- `GET /api/layouts` / `POST /api/layouts` / `PATCH /api/layouts/{id}` / `DELETE /api/layouts/{id}`
- `GET /api/links` / `POST /api/links` / `PATCH /api/links/{id}` / `DELETE /api/links/{id}`
- `POST /api/checks/test` to validate connectivity and credentials.
- `GET /api/alerts` for recent events.
- `WS /ws/updates` streaming `{deviceId, status, metrics}` payloads.

## Deployment Considerations
- **Containerization**: Docker images for backend, workers, and frontend served via Nginx.
- **Scaling**: Horizontal worker scaling for polling throughput; rate limiting of SNMP to avoid overwhelming devices.
- **Security**: Secrets management for SNMPv3 credentials; HTTPS termination; RBAC for UI actions.
- **Observability**: Prometheus metrics for poll latency/success, with Grafana dashboards; structured logs for traceability.

## Minimal Prototype Plan
- Scaffold FastAPI with in-memory store and WebSocket endpoint emitting mock monitoring updates.
- Build a React map view that allows adding nodes and persisting them to the backend.
- Implement ICMP ping checks using `asyncio` subprocess and SNMP stubs with mock data to unblock UI integration.
- Add link drawing and simulated utilization coloring for demo purposes.
