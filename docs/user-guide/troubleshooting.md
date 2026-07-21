# Troubleshooting

Resolve common issues and manage alerts.

---

## Alerts Overview

BuckPow automatically generates alerts when measurements exceed configured thresholds or devices go offline. The Alerts page lets you view, filter, and resolve these alerts.

<!-- TODO: Replace with alerts page screenshot -->

Navigate to **Alerts** in the sidebar.

## Alert Levels

| Level | Color | Description |
|-------|-------|-------------|
| **Info** | Blue | Informational messages (e.g., device came back online) |
| **Warning** | Yellow/Orange | Threshold warnings (e.g., low voltage, device offline) |
| **Critical** | Red | Critical issues requiring attention (e.g., high power, high current) |

## Automatic Alerts

BuckPow generates alerts automatically based on device thresholds:

### High Power Alert

Triggered when power exceeds the threshold:

- **Default threshold**: 2.5 W
- **Level**: Critical
- **Message**: `High power on <device_id>: <value>W (threshold: <threshold>W)`

### High Current Alert

Triggered when current exceeds the threshold:

- **Default threshold**: 0.5 A
- **Level**: Critical
- **Message**: `High current on <device_id>: <value>A (threshold: <threshold>A)`

### Low Voltage Alert

Triggered when voltage drops below the threshold:

- **Default threshold**: 4.5 V
- **Level**: Warning
- **Message**: `Low voltage on <device_id>: <value>V (threshold: <threshold>V)`

### Device Offline Alert

Triggered when no measurement received within the timeout:

- **Default timeout**: 30 seconds
- **Level**: Warning
- **Message**: `Device offline (<device_id>) — no data received for >30s`

### Device Back Online

Generated when a device comes back online after being offline:

- **Level**: Info
- **Message**: `Device back online (<device_id>)`

## Threshold Configuration

Thresholds can be set at two levels:

### Device-Level Thresholds

Set per-device thresholds on the device edit page:

1. Navigate to **Devices**
2. Click **Edit** on the device
3. Set threshold values:

| Field | Unit | Default | Description |
|-------|------|---------|-------------|
| **High Power Threshold** | W | 2.5 | Alert when power exceeds this value |
| **High Current Threshold** | A | 0.5 | Alert when current exceeds this value |
| **Low Voltage Threshold** | V | 4.5 | Alert when voltage drops below this value |

4. Click **Save**

### Global Thresholds (Settings)

Set default thresholds for all devices in Settings:

1. Navigate to **Settings**
2. Set default threshold values
3. Click **Save**

Device-level thresholds override global defaults.

## Managing Alerts

### Viewing Alerts

The Alerts page shows all alerts with:

| Column | Description |
|--------|-------------|
| **Level** | Info, Warning, or Critical |
| **Message** | Alert description |
| **Device** | Device name or ID |
| **Created** | When the alert was generated |
| **Resolved** | When the alert was resolved (empty if unresolved) |

### Filtering Alerts

Use the filters to narrow down alerts:

| Filter | Options |
|--------|---------|
| **Device** | All devices or specific device |
| **Level** | All, Info, Warning, Critical |
| **Status** | All, Unresolved, Resolved |

### Resolving a Single Alert

1. Find the alert in the list
2. Click the **Resolve** button (checkmark icon)
3. The alert is marked as resolved with a timestamp

### Resolving All Alerts

1. Click **Resolve All** button
2. All unresolved alerts are marked as resolved

!!! tip "Resolve by device"
    You can also resolve all alerts for a specific device using the API:

    ```bash
    curl -X POST "http://localhost:8000/api/v1/alerts/resolve-all?device_id=1" \
      -H 'Authorization: Bearer <jwt-token>'
    ```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/alerts` | List alerts (paginated, filterable) |
| `POST` | `/api/v1/alerts` | Create alert manually |
| `PATCH` | `/api/v1/alerts/{id}/resolve` | Resolve a single alert |
| `POST` | `/api/v1/alerts/resolve-all` | Resolve all unresolved alerts |

### List Alerts

```bash
curl "http://localhost:8000/api/v1/alerts?resolved=false&level=critical" \
  -H 'Authorization: Bearer <jwt-token>'
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 10) |
| `device_id` | integer | Filter by device ID |
| `level` | string | Filter by level: `info`, `warning`, `critical` |
| `resolved` | string | Filter: `true` or `false` |

### Create Alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <jwt-token>' \
  -d '{
    "device_id": 1,
    "level": "warning",
    "message": "Custom alert message"
  }'
```

---

## Common Issues

### Device Not Appearing in Dashboard

**Symptoms:**

- Device doesn't appear in the Devices list
- No measurements are being recorded

**Solutions:**

1. **Check WiFi connection** — Verify the device is connected to WiFi (check Serial Monitor)
2. **Verify server URL** — Ensure `API_BASE` in the firmware points to the correct server
3. **Check API key** — Verify the API key matches the device in BuckPow
4. **Test connectivity** — From a computer on the same network:

    ```bash
    curl http://<server-ip>:8000/api/v1/health
    ```

5. **Check firewall** — Ensure port 8000 is open on the server

### Device Shows Offline

**Symptoms:**

- Device appears in the dashboard but status is **offline**
- No recent measurements

**Solutions:**

1. **Check device power** — Ensure the ESP32/ESP8266 is powered
2. **Check WiFi signal** — Move the device closer to the router
3. **Review Serial Monitor** — Look for connection errors
4. **Check server** — Verify BuckPow is running:

    ```bash
    curl http://localhost:8000/api/v1/health
    ```

5. **Increase timeout** — If the device is slow, increase `DEVICE_ONLINE_TIMEOUT`:

    ```env
    DEVICE_ONLINE_TIMEOUT=60
    ```

### Measurements Not Recording

**Symptoms:**

- Device is online but no measurements appear
- Dashboard shows no chart data

**Solutions:**

1. **Start a session** — Measurements are assigned to running sessions
2. **Check device enabled** — Ensure the device is not disabled in the dashboard
3. **Verify INA219** — Check wiring and I2C connection
4. **Check Serial Monitor** — Look for HTTP errors (400, 401, 403)

### High Power / Current Alerts

**Symptoms:**

- Constant critical alerts for high power or current

**Solutions:**

1. **Adjust thresholds** — Increase the threshold if the value is expected:

    - Edit the device and set a higher threshold
    - Or update global defaults in Settings

2. **Investigate the load** — High power may indicate:
    - A short circuit
    - An overloaded circuit
    - A malfunctioning device

3. **Check wiring** — Incorrect wiring can cause false readings

### Low Voltage Alerts

**Symptoms:**

- Warning alerts for low voltage

**Solutions:**

1. **Check power supply** — Ensure the power source is adequate
2. **Check connections** — Loose connections cause voltage drops
3. **Adjust threshold** — If low voltage is expected, increase the threshold:

    ```env
    # In device settings or global settings
    low_voltage_threshold: 3.3
    ```

### Export Not Working

**Symptoms:**

- CSV or XLSX download fails or returns empty file

**Solutions:**

1. **Check filters** — Ensure date range or filters are not too restrictive
2. **Verify data exists** — Check the Measurements page for data
3. **Check rate limit** — Export is limited to 10 requests/minute
4. **Try API directly** — Test the export endpoint:

    ```bash
    curl "http://localhost:8000/api/v1/measurements/export/csv" \
      -H 'Authorization: Bearer <jwt-token>' \
      --output test.csv
    ```

### Dashboard Not Loading

**Symptoms:**

- Blank page or loading spinner
- JavaScript errors in browser console

**Solutions:**

1. **Clear browser cache** — Hard refresh with Ctrl+Shift+R
2. **Check console** — Open browser developer tools (F12)
3. **Verify JavaScript** — Ensure `app/static/js/` files are accessible
4. **Check HTMX** — Look for HTMX errors in the console
5. **Restart server** — Restart BuckPow:

    ```bash
    # Docker
    docker compose restart app

    # Local
    # Stop and restart the server
    ```

### Login Fails

**Symptoms:**

- Cannot log in with admin credentials
- Redirected back to login page

**Solutions:**

1. **Verify credentials** — Check `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`
2. **Check JWT_SECRET** — Ensure `JWT_SECRET` is set (required in production)
3. **Clear cookies** — Clear browser cookies for the BuckPow domain
4. **Check JWT expiry** — Tokens expire after 7 days by default

### Database Errors

**Symptoms:**

- Server won't start
- Error messages about database connection

**Solutions:**

1. **SQLite** — Delete the database and restart:

    ```bash
    rm -f instance/buckpow.db
    ```

2. **PostgreSQL** — Check connection string in `.env`:

    ```env
    DATABASE_URL=postgresql://user:password@host:5432/dbname
    ```

3. **Run migrations** — For PostgreSQL/MySQL:

    ```bash
    alembic upgrade head
    ```

4. **Check database server** — Ensure the database is running:

    ```bash
    # PostgreSQL
    pg_isready

    # MySQL
    mysqladmin ping
    ```

### Firmware Outdated Warning

**Symptoms:**

- API returns `X-Firmware-Outdated: true` header

**Solutions:**

1. **Update firmware** — Download the latest version from the repository
2. **Re-upload** — Upload the new firmware to your ESP32/ESP8266
3. **Check compatibility** — The minimum firmware version is `1.0.0`

---

## Getting Help

If you can't resolve an issue:

1. **Check the logs** — View server logs for error messages:

    ```bash
    # Docker
    docker compose logs app

    # Local
    # Check terminal output
    ```

2. **Search issues** — Check [GitHub Issues](https://github.com/arifnd/buckpow/issues) for similar problems
3. **Open an issue** — Create a new issue with:
    - BuckPow version
    - Steps to reproduce
    - Error messages
    - Server logs
