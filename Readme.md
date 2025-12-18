# MonoTaur Network Monitoring Concept

MonoTaur aims to provide a map-centric network monitoring experience similar to MikroTik's The Dude. The initial concept focuses on building a lightweight web application that allows operators to place devices on a map, define monitoring checks, and visualize traffic links via SNMP.

## Vision
- Start with an empty map; allow users to upload a background image (rack layout, floor plan) or switch to OpenStreetMap tiles.
- Right-click anywhere on the map to add a device node, edit its properties, and drag it around.
- Configure device addressing and monitoring checks (ICMP, SNMP, HTTP, etc.).
- Draw logical links between devices and poll switches via SNMP to display utilization on individual interfaces.
- Provide status dashboards and alerting hooks so changes in device health are immediately visible.

## High-level Architecture
- **Frontend**: React + TypeScript using a map component (Leaflet or MapLibre). Provides node/edge editing, context menus, and health indicators. Stores map layouts persistently via API.
- **Backend**: Python (FastAPI) for REST + WebSocket updates. Performs active checks (ICMP, HTTP) and SNMP polling using `easysnmp`/`pysnmp`. Exposes device inventory, monitoring results, and topology data.
- **Data store**: PostgreSQL (devices, checks, link definitions), Redis or in-memory cache for short-lived poll results.
- **Telemetry workers**: Background task queue (Celery or RQ) running periodic polls and pushing updates to the backend for fan-out to the UI.
- **Authentication**: JWT-backed sessions with role-based access for view-only vs. admin users.

## Proposed Feature Slice for an MVP
1. **Map & Layouts**
   - Upload an image to use as a map background or choose OpenStreetMap tiles.
   - Add, move, rename, and delete device nodes with a right-click context menu.
   - Save and load map layouts from the backend.
2. **Device Management**
   - Store device name, type, and IP/hostname.
   - Configure monitoring profiles (PING, SNMP read community, optional services like HTTP/HTTPS).
3. **Monitoring & Alerts**
   - Periodic ICMP checks for reachability and latency.
   - SNMP polling for interface counters on switches/routers.
   - Threshold-based alerts surfaced in a notification panel and via WebSocket to the UI.
4. **Link Visualization**
   - Draw links between devices; associate each link with switch port OIDs to show utilization.
   - Color-code link lines based on bandwidth usage; show hover tooltips with current metrics.
5. **Extensibility**
   - Plugin interface for new service checks.
   - Import/export layouts and device lists.

## Development Roadmap
- **Phase 1: Skeleton**
  - Set up the FastAPI backend with endpoints for devices, checks, and layouts.
  - Build a React SPA scaffold with Leaflet/MapLibre and a context menu for adding nodes.
- **Phase 2: Monitoring Core**
  - Implement background polling tasks for ICMP and SNMP.
  - Stream real-time updates to the frontend via WebSocket.
- **Phase 3: Visualization & UX**
  - Link rendering with utilization coloring, alert overlays, and layout persistence.
  - User auth and RBAC.

## Repository Layout (proposed)
```
/Readme.md           Project overview
/docs/architecture.md Detailed architecture decisions and APIs
/docs/data-model.md   ERDs and schemas for devices, checks, and links
/frontend/            React app (not yet added)
/backend/             FastAPI services and workers (prototype scaffold)
```

## Next Steps
- Choose the map library (Leaflet vs MapLibre) and finalize UI component library.
- Expand the prototype backend in `/backend` beyond the current in-memory CRUD scaffold for devices, layouts, and links. A first
  ICMP check executor and `/checks` endpoints now exist to test reachability from the API.
- Define database schema for devices, checks, links, and poll results.
- Implement ICMP/SNMP pollers with a pluggable check abstraction.
- Add sample topology data and fixtures for rapid UI testing.
