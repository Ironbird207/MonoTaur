# Data Model Sketch

This file captures proposed tables and entities for MonoTaur. Field names are suggestions and can evolve as code lands.

## devices
| column        | type        | notes |
|---------------|-------------|-------|
| id            | UUID (pk)   | primary key |
| name          | text        | display name |
| type          | text        | router, switch, server, wireless, etc. |
| ip_address    | inet        | main management IP or hostname |
| snmp_profile  | jsonb       | SNMP version, community, v3 credentials |
| created_at    | timestamptz | |
| updated_at    | timestamptz | |

## layouts
| column       | type        | notes |
|--------------|-------------|-------|
| id           | UUID (pk)   | |
| name         | text        | layout name |
| background   | text        | uploaded image path or `osm` for map tiles |
| created_at   | timestamptz | |
| updated_at   | timestamptz | |

## layout_devices
Tracks coordinates of devices within a specific layout.

| column      | type      | notes |
|-------------|-----------|-------|
| id          | UUID (pk) | |
| layout_id   | UUID (fk) | references layouts.id |
| device_id   | UUID (fk) | references devices.id |
| x           | numeric   | normalized 0-1 horizontal position |
| y           | numeric   | normalized 0-1 vertical position |

## links
| column            | type        | notes |
|-------------------|-------------|-------|
| id                | UUID (pk)   | |
| source_device_id  | UUID (fk)   | |
| target_device_id  | UUID (fk)   | |
| source_ifindex    | integer     | optional SNMP ifIndex for utilization |
| target_ifindex    | integer     | optional SNMP ifIndex for utilization |
| label             | text        | optional description |

## checks
| column        | type        | notes |
|---------------|-------------|-------|
| id            | UUID (pk)   | |
| device_id     | UUID (fk)   | |
| type          | text        | icmp, snmp, http, https, custom |
| interval_s    | integer     | polling interval |
| timeout_ms    | integer     | timeout for the check |
| params        | jsonb       | e.g., OIDs, URLs, auth headers |
| thresholds    | jsonb       | status transition rules |

## metrics
Stores individual poll results. Large tables may use retention policies.

| column       | type        | notes |
|--------------|-------------|-------|
| id           | UUID (pk)   | |
| check_id     | UUID (fk)   | |
| ts           | timestamptz | timestamp of poll |
| status       | text        | ok, warn, crit, unknown |
| latency_ms   | numeric     | for ping/HTTP |
| packet_loss  | numeric     | for ping |
| bandwidth_in | numeric     | bits per second (derived) |
| bandwidth_out| numeric     | bits per second (derived) |
| details      | jsonb       | raw payload including SNMP counters or HTTP status |

## alerts
| column       | type        | notes |
|--------------|-------------|-------|
| id           | UUID (pk)   | |
| device_id    | UUID (fk)   | |
| check_id     | UUID (fk)   | |
| status       | text        | warn, crit, clear |
| message      | text        | description |
| triggered_at | timestamptz | |
| cleared_at   | timestamptz | nullable |
