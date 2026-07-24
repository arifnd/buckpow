# API Reference

Complete REST API reference for BuckPow.

---

## Overview

BuckPow exposes a RESTful API under `/api/v1/`. The API supports:

- **JSON request/response** for all endpoints
- **JWT authentication** for user endpoints
- **API key authentication** for device endpoints
- **Pagination** for list endpoints

<!-- TODO: Replace with Swagger UI screenshot -->

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

### JWT Token (User)

Obtain a token via login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"password"}'
```

Use the token in requests:

```bash
curl http://localhost:8000/api/v1/devices \
  -H 'Authorization: Bearer <jwt-token>'
```

### API Key (Device)

Obtain the key from the device detail page, then:

```bash
curl -X POST http://localhost:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <api-key>' \
  -d '{"device_id":"esp32-01","bus_voltage":5.0,"shunt_voltage":50,"current":150,"power":750}'
```

## Response Format

### Success

```json
{
  "status": "success",
  "id": 1
}
```

### Error

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

### Paginated List

```json
{
  "items": [...],
  "page": 1,
  "pages": 10,
  "total": 100,
  "per_page": 10
}
```

---

## Health

### Health Check

```http
GET /api/v1/health
```

**Authentication:** None

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "min_firmware_version": "1.0.0"
}
```

---

## Measurements

### Receive Measurement

```http
POST /api/v1/measurements
```

**Authentication:** Device API key (or none if `DEVICE_AUTH_ENABLED=false`)

**Request Body:**

```json
{
  "device_id": "esp32-ina219-01",
  "bus_voltage": 5.12,
  "shunt_voltage": 82,
  "current": 241,
  "power": 1234,
  "firmware_version": "1.2.0"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | string | Yes | Device identifier (auto-registers if new) |
| `bus_voltage` | float | Yes | Bus voltage (V) |
| `shunt_voltage` | float | Yes | Shunt voltage (mV) |
| `current` | float | Yes | Current (mA) |
| `power` | float | Yes | Power (mW) |
| `firmware_version` | string | No | Firmware version string |

**Response (201):**

```json
{
  "status": "success",
  "id": 1
}
```

!!! info "Unit conversion"
    The API converts mA → A and mW → W when storing measurements.

### List Measurements

```http
GET /api/v1/measurements
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 50 | Items per page |
| `device_id` | integer | — | Filter by device ID |
| `session_id` | integer | — | Filter by session ID |
| `start_date` | string | — | Start date (ISO 8601) |
| `end_date` | string | — | End date (ISO 8601) |

**Response (200):**

```json
{
  "measurements": [
    {
      "id": 1,
      "device_id": 1,
      "device_name": "esp32-ina219-01",
      "session_id": 1,
      "session_name": "FW v1.0 Idle",
      "bus_voltage": 5.120,
      "shunt_voltage": 0.082,
      "load_voltage": 5.038,
      "current": 0.241,
      "power": 1.234,
      "energy": 0.000343,
      "created_at": "2026-07-18T10:00:00+00:00"
    }
  ],
  "page": 1,
  "pages": 10,
  "total": 500,
  "per_page": 50
}
```

### Export CSV

```http
GET /api/v1/measurements/export/csv
```

**Authentication:** JWT token

**Parameters:** Same as list measurements

**Response (200):**

- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=measurements.csv`

```csv
ID,Node,Session,Bus Voltage,Shunt Voltage,Load Voltage,Current (A),Power (W),Energy (Wh),Timestamp
1,esp32-ina219-01,FW v1.0 Idle,5.120,0.082,5.038,0.241,1.234,0.000343,2026-07-18T10:00:00+00:00
```

### Export XLSX

```http
GET /api/v1/measurements/export/xlsx
```

**Authentication:** JWT token

**Parameters:** Same as list measurements

**Response (200):**

- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename=measurements.xlsx`

### Chart Data

```http
GET /api/v1/chart
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | — | Filter by device ID |
| `session_id` | integer | — | Filter by session ID |
| `limit` | integer | 500 | Max data points |
| `granularity` | string | — | `s`, `m`, `h`, `d` |
| `range` | string | — | `1h`, `24h`, `7d`, `30d` |
| `start_date` | string | — | Start date (ISO 8601) |
| `end_date` | string | — | End date (ISO 8601) |

**Response (200):**

```json
{
  "labels": ["10:00:00", "10:00:01", "..."],
  "voltage": [5.12, 5.11, "..."],
  "current": [0.241, 0.239, "..."],
  "power": [1.234, 1.223, "..."],
  "energy": [0.000343, 0.000686, "..."]
}
```

---

## Devices

### List Devices

```http
GET /api/v1/devices
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (0 = all) |
| `per_page` | integer | 10 | Items per page |

**Response (200):**

```json
{
  "devices": [
    {
      "id": 1,
      "device_id": "esp32-ina219-01",
      "alias": "Lab Sensor",
      "description": "INA219 on power supply",
      "sampling_interval": 1,
      "last_seen": "2026-07-18T10:05:00+00:00",
      "status": "online",
      "api_key": "a1b2c3****ef01",
      "enabled": true,
"firmware_version": "1.2.0",
      "local_ip": "192.168.1.100",
      "project_id": 1,
      "project_name": "Power Lab",
      "high_current_threshold": 0.5,
      "high_power_threshold": 2.5,
      "low_voltage_threshold": 4.5,
      "created_at": "2026-07-18T09:00:00+00:00",
      "updated_at": "2026-07-18T10:05:00+00:00"
    }
  ],
  "page": 1,
  "pages": 5,
  "total": 50,
  "per_page": 10
}
```

### Create Device

```http
POST /api/v1/devices
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "device_id": "esp32-ina219-01",
  "alias": "Lab Sensor",
  "description": "INA219 on power supply",
  "sampling_interval": 1,
  "project_id": 1,
  "firmware_version": "1.2.0",
  "high_current_threshold": 0.5,
  "high_power_threshold": 2.5,
  "low_voltage_threshold": 4.5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | string | Yes | Unique device identifier |
| `alias` | string | No | Friendly name |
| `description` | string | No | Notes |
| `sampling_interval` | integer | No | Seconds (default: 1) |
| `project_id` | integer | No | Project ID |
| `firmware_version` | string | No | Firmware version |
| `high_current_threshold` | float | No | Alert threshold (A) |
| `high_power_threshold` | float | No | Alert threshold (W) |
| `low_voltage_threshold` | float | No | Alert threshold (V) |

**Response (201):** Device object with generated `id` and `api_key`

### Get Device

```http
GET /api/v1/devices/{device_id}
```

**Authentication:** JWT token

**Response (200):** Device object

### Update Device

```http
PUT /api/v1/devices/{device_id}
```

**Authentication:** JWT token (owner check)

**Request Body:** Same as create (all fields optional)

**Response (200):** Updated device object

### Delete Device

```http
DELETE /api/v1/devices/{device_id}
```

**Authentication:** JWT token (owner check)

**Response (200):**

```json
{"status": "deleted"}
```

### Get API Key

```http
GET /api/v1/devices/{device_id}/key
```

**Authentication:** JWT token

**Response (200):**

```json
{
  "api_key": "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
  "id": 1
}
```

### Toggle Device

```http
PATCH /api/v1/devices/{device_id}/toggle
```

**Authentication:** JWT token (owner check)

**Response (200):** Updated device object with `enabled` toggled

### Regenerate API Key

```http
POST /api/v1/devices/{device_id}/regenerate-key
```

**Authentication:** JWT token (owner check)

**Response (200):**

```json
{
  "api_key": "new-api-key-here",
  "id": 1
}
```

!!! warning "Old key invalidated"
    The old API key is immediately invalidated after regeneration.

### Update Device Local IP

```http
PATCH /api/v1/devices/local-ip
```

**Authentication:** Device Bearer token (API key)

**Request Body:**

```json
{
  "local_ip": "192.168.1.100"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `local_ip` | string | Yes | Device local IP address |

**Response (200):**

```json
{
  "status": "ok",
  "local_ip": "192.168.1.100"
}
```

!!! info "Firmware usage"
    Firmware calls this endpoint once after WiFi connects and the first successful API call is made. The `ipReported` flag prevents resending on every measurement.

---

## Sessions

### List Sessions

```http
GET /api/v1/sessions
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (0 = all with stats) |
| `per_page` | integer | 10 | Items per page |

**Response (200):**

```json
{
  "sessions": [
    {
      "id": 1,
      "device_id": 1,
      "device_name": "esp32-ina219-01",
      "name": "FW v1.0 Idle",
      "target_device": "Raspberry Pi 4",
      "description": "Idle power test",
      "status": "finished",
      "project_id": 1,
      "project_name": "Power Lab",
      "started_at": "2026-07-18T10:00:00+00:00",
      "ended_at": "2026-07-18T10:10:00+00:00",
      "created_at": "2026-07-18T09:55:00+00:00",
      "updated_at": "2026-07-18T10:10:00+00:00",
      "avg_power": 0.185,
      "total_energy": 0.031
    }
  ],
  "page": 1,
  "pages": 5,
  "total": 50,
  "per_page": 10
}
```

### Create Session

```http
POST /api/v1/sessions
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "device_id": 1,
  "name": "FW v1.0 Idle",
  "target_device": "Raspberry Pi 4",
  "description": "Idle power test",
  "project_id": 1
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | integer | Yes | Device ID |
| `name` | string | Yes | Session name |
| `target_device` | string | No | Device under test |
| `description` | string | No | Notes |
| `project_id` | integer | No | Project ID |

**Response (201):** Session object with `status: "draft"`

### Get Session

```http
GET /api/v1/sessions/{session_id}
```

**Authentication:** JWT token

**Response (200):** Session object

### Update Session

```http
PUT /api/v1/sessions/{session_id}
```

**Authentication:** JWT token

**Request Body:** Same as create (all fields optional)

**Response (200):** Updated session object

### Delete Session

```http
DELETE /api/v1/sessions/{session_id}
```

**Authentication:** JWT token

**Response (200):**

```json
{"status": "deleted"}
```

### Start Session

```http
POST /api/v1/sessions/{session_id}/start
```

**Authentication:** JWT token

**Response (200):** Updated session object with `status: "running"` and `started_at`

**Errors:**

- `400` — Session is already running
- `400` — Another session is already running for this device

### Stop Session

```http
POST /api/v1/sessions/{session_id}/stop
```

**Authentication:** JWT token

**Response (200):** Updated session object with `status: "finished"` and `ended_at`

**Errors:**

- `400` — Session is not running

### Session Statistics

```http
GET /api/v1/sessions/{session_id}/stats
```

**Authentication:** JWT token

**Response (200):**

```json
{
  "session_id": 1,
  "session_name": "FW v1.0 Idle",
  "device_name": "esp32-ina219-01",
  "avg_power": 0.185,
  "peak_power": 0.234,
  "total_energy": 0.031,
  "avg_current": 0.036,
  "voltage_stddev": 0.008,
  "duration": 600,
  "measurement_count": 600,
  "started_at": "2026-07-18T10:00:00+00:00",
  "ended_at": "2026-07-18T10:10:00+00:00",
  "chart_data": {
    "labels": ["10:00:00", "..."],
    "power": [0.185, "..."]
  }
}
```

---

## Projects

### List Projects

```http
GET /api/v1/projects
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (0 = all) |
| `per_page` | integer | 10 | Items per page |

**Response (200):**

```json
{
  "projects": [
    {
      "id": 1,
      "name": "Power Lab",
      "description": "Lab experiments",
      "owner_id": 1,
      "created_at": "2026-07-18T09:00:00+00:00",
      "updated_at": "2026-07-18T09:00:00+00:00"
    }
  ],
  "page": 1,
  "pages": 2,
  "total": 15,
  "per_page": 10
}
```

### Create Project

```http
POST /api/v1/projects
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "name": "Power Lab",
  "description": "Lab experiments"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name |
| `description` | string | No | Notes |

**Response (201):** Project object with `owner_id` set to current user

### Get Project

```http
GET /api/v1/projects/{project_id}
```

**Authentication:** JWT token

**Response (200):** Project object

### Update Project

```http
PUT /api/v1/projects/{project_id}
```

**Authentication:** JWT token (owner check)

**Request Body:** Same as create (all fields optional)

**Response (200):** Updated project object

### Delete Project

```http
DELETE /api/v1/projects/{project_id}
```

**Authentication:** JWT token (owner check)

**Response (200):**

```json
{"status": "deleted"}
```

---

## Alerts

### List Alerts

```http
GET /api/v1/alerts
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 10 | Items per page |
| `device_id` | integer | — | Filter by device ID |
| `level` | string | — | `info`, `warning`, `critical` |
| `resolved` | string | — | `true` or `false` |

**Response (200):**

```json
{
  "alerts": [
    {
      "id": 1,
      "device_id": 1,
      "device_name": "esp32-ina219-01",
      "level": "critical",
      "message": "High power on esp32-ina219-01: 3.450W (threshold: 2.5W)",
      "created_at": "2026-07-18T10:05:00+00:00",
      "resolved_at": null
    }
  ],
  "page": 1,
  "pages": 3,
  "total": 25,
  "per_page": 10,
  "unresolved_count": 5
}
```

### Create Alert

```http
POST /api/v1/alerts
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "device_id": 1,
  "level": "warning",
  "message": "Custom alert message"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | integer | Yes | Device ID |
| `level` | string | Yes | `info`, `warning`, `critical` |
| `message` | string | Yes | Alert message |

**Response (201):** Alert object

### Resolve Alert

```http
PATCH /api/v1/alerts/{alert_id}/resolve
```

**Authentication:** JWT token

**Response (200):** Alert object with `resolved_at` set

### Resolve All Alerts

```http
POST /api/v1/alerts/resolve-all
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Optional: resolve only for this device |

**Response (200):**

```json
{"status": "ok"}
```

---

## Benchmark

### Compare Sessions

```http
GET /api/v1/benchmark/compare
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sessions` | string | Yes | Comma-separated session IDs (2–3) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/benchmark/compare?sessions=1,2,3" \
  -H 'Authorization: Bearer <jwt-token>'
```

**Response (200):**

```json
{
  "sessions": [
    {
      "session_id": 1,
      "session_name": "FW v1.0 Idle",
      "device_name": "esp32-ina219-01",
      "avg_power": 0.185,
      "peak_power": 0.234,
      "total_energy": 0.031,
      "avg_current": 0.036,
      "voltage_stddev": 0.008,
      "duration": 600,
      "measurement_count": 600,
      "started_at": "2026-07-18T10:00:00+00:00",
      "ended_at": "2026-07-18T10:10:00+00:00",
      "chart_data": {
        "labels": ["10:00:00", "..."],
        "power": [0.185, "..."]
      }
    }
  ]
}
```

---

## Authentication

### Login

```http
POST /api/v1/auth/login
```

**Request Body:**

```json
{
  "email": "admin@example.com",
  "password": "password"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "user": {
    "id": 1,
    "name": "Admin",
    "email": "admin@example.com",
    "created_at": "2026-07-18T09:00:00+00:00"
  },
  "token": "eyJ..."
}
```

Sets an httponly cookie `access_token` for dashboard access.

### Logout

```http
POST /api/v1/auth/logout
```

**Response (200):**

```json
{"status": "ok"}
```

Clears the `access_token` cookie.

### Current User

```http
GET /api/v1/auth/me
```

**Authentication:** JWT token

**Response (200):**

```json
{
  "id": 1,
  "name": "Admin",
  "email": "admin@example.com",
  "created_at": "2026-07-18T09:00:00+00:00"
}
```

### Update Profile

```http
PUT /api/v1/auth/profile
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "name": "New Name",
  "email": "new@example.com",
  "password": "new-password"
}
```

All fields optional. Only provided fields are updated.

**Response (200):**

```json
{
  "status": "ok",
  "user": {
    "id": 1,
    "name": "New Name",
    "email": "new@example.com",
    "created_at": "2026-07-18T09:00:00+00:00"
  }
}
```

---

## Settings

### Get Settings

```http
GET /api/v1/settings
```

**Authentication:** JWT token

**Response (200):**

```json
{
  "high_power_threshold": 2.5,
  "high_current_threshold": 0.5,
  "low_voltage_threshold": 4.5,
  "brand": "BuckPow",
  "timestamp_format": "24h",
  "date_format": "YYYY-MM-DD",
  "timezone": "+0",
  "device_watchdog_timeout": 30
}
```

### Update Settings

```http
PUT /api/v1/settings
```

**Authentication:** JWT token

**Request Body:**

```json
{
  "high_power_threshold": 3.0,
  "brand": "My Lab",
  "timestamp_format": "12h",
  "date_format": "DD/MM/YYYY",
  "timezone": "+8"
}
```

All fields optional.

**Response (200):** Updated settings object

### Database Info

```http
GET /api/v1/settings/db-info
```

**Authentication:** JWT token

**Response (200):**

```json
{
  "type": "sqlite",
  "size": 1258291,
  "backup_formats": {
    "sqlite": true,
    "sql_dump": false
  },
  "tool_available": true
}
```

### Download Backup

```http
GET /api/v1/settings/backup
```

**Authentication:** JWT token

**Response (200):**

- SQLite: Raw `.db` file
- PostgreSQL: Gzipped SQL dump
- MySQL: Gzipped SQL dump

---

## Audit Logs

### List Audit Logs

```http
GET /api/v1/audit/logs
```

**Authentication:** JWT token

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 10 | Items per page |
| `action` | string | — | Filter by action |
| `target_type` | string | — | Filter by target type |

**Response (200):**

```json
{
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "user_name": "Admin",
      "action": "device.create",
      "target_type": "device",
      "target_id": 1,
      "details": {},
      "ip_address": "192.168.1.100",
      "created_at": "2026-07-18T09:00:00+00:00"
    }
  ],
  "page": 1,
  "pages": 10,
  "total": 100,
  "per_page": 10
}
```

### Audit Actions

| Action | Description |
|--------|-------------|
| `device.create` | Device created |
| `device.update` | Device updated |
| `device.delete` | Device deleted |
| `device.enable` | Device enabled |
| `device.disable` | Device disabled |
| `api_key.regenerate` | API key regenerated |
| `session.start` | Session started |
| `session.stop` | Session stopped |
| `export.csv` | CSV export |
| `export.xlsx` | XLSX export |

---

## Dashboard

### Latest Data

```http
GET /api/v1/dashboard
```

**Authentication:** None

**Response (200):**

```json
{
  "latest": {
    "bus_voltage": 5.12,
    "shunt_voltage": 0.082,
    "load_voltage": 5.038,
    "current": 0.241,
    "power": 1.234,
    "energy": 0.000343,
    "created_at": "2026-07-18T10:05:00+00:00"
  },
  "devices": [
    {
      "id": 1,
      "device_id": "esp32-ina219-01",
      "status": "online"
    }
  ]
}
```

### Summary

```http
GET /api/v1/dashboard/summary
```

**Authentication:** None

**Response (200):**

```json
{
  "online_devices": 3,
  "offline_devices": 1,
  "active_sessions": 2,
  "today_energy": 0.125,
  "total_projects": 5
}
```

### Statistics

```http
GET /api/v1/dashboard/statistics
```

**Authentication:** None

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | integer | Filter by session ID |
| `start_date` | string | Start date (ISO 8601) |

**Response (200):**

```json
{
  "voltage": {"min": 5.05, "max": 5.15, "avg": 5.10},
  "current": {"min": 0.20, "max": 0.30, "avg": 0.24},
  "power": {"min": 1.0, "max": 1.5, "avg": 1.23, "peak": 1.8},
  "total_energy": 0.031,
  "energy": {
    "hourly": [{"period": "10:00", "energy": 0.005}],
    "daily": [{"period": "2026-07-18", "energy": 0.125}],
    "weekly": [{"period": "2026-W29", "energy": 0.875}],
    "monthly": [{"period": "2026-07", "energy": 3.5}]
  }
}
```

---

## Rate Limits

| Endpoint | Method | Limit | Window | Key |
|----------|--------|-------|--------|-----|
| `/api/v1/auth/login` | POST | 5 | 60s | IP |
| `/api/v1/measurements` | POST | 60 | 60s | API key |
| `/api/v1/measurements/export/csv` | GET | 10 | 60s | IP |
| `/api/v1/measurements/export/xlsx` | GET | 10 | 60s | IP |

When rate limited, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMITED"
}
```

With header: `Retry-After: <seconds>`

---

## Interactive Documentation

When `DISABLE_API_DOCS=false` (default), interactive docs are available at:

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/openapi.json` | OpenAPI schema |
