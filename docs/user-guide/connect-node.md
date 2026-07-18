# Connect Node

Connect your ESP32/ESP8266 measurement node to the BuckPow server.

---

## Overview

After building your [Measurement Node](measurement-node.md), you need to configure it to send measurements to your BuckPow server. This guide covers network setup, firmware configuration, and connection verification.

<!-- TODO: Replace with connection flow diagram -->

## Prerequisites

- A running BuckPow instance (see [Quick Start](../quick-start.md))
- A configured measurement node (see [Measurement Node](measurement-node.md))
- Both devices on the same network (or with network access to each other)

## Step 1 — Find Your Server IP

### Local Network

Find the IP address of the machine running BuckPow:

=== "Linux / macOS"

    ```bash
    hostname -I
    # or
    ifconfig | grep inet
    ```

=== "Windows"

    ```cmd
    ipconfig
    ```

The IP will be something like `192.168.1.x` or `10.0.0.x`.

### Docker

If running with Docker Compose, the server is accessible at the host IP:

```bash
# Find your host IP
hostname -I
```

Use `http://<host-ip>:8000` as the API base URL.

### Cloud / Remote

If BuckPow is deployed on a cloud server or remote machine, use its public IP or domain name:

```
https://your-domain.com
```

## Step 2 — Verify Server is Running

Test connectivity from any machine on the network:

```bash
curl http://<server-ip>:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "min_firmware_version": "1.0.0"
}
```

If this fails:

- Check that BuckPow is running
- Verify firewall rules allow port 8000
- Ensure the ESP32/ESP8266 can reach this IP

## Step 3 — Get Your API Key

1. Open the BuckPow dashboard at `http://<server-ip>:8000`
2. Navigate to **Devices**
3. Click **New Device** or use an existing device
4. Click the **Key** button to view the full API key
5. Copy the key

<!-- TODO: Replace with API key screenshot -->

!!! info "No API key?"
    If `DEVICE_AUTH_ENABLED=false`, you can skip this step. Devices will authenticate by `device_id` only.

## Step 4 — Configure Firmware

Open the Arduino sketch and edit the configuration constants:

```cpp
// ── WiFi Configuration ──
const char* WIFI_SSID     = "your-network-name";
const char* WIFI_PASSWORD = "your-network-password";

// ── BuckPow API Configuration ──
const char* API_BASE   = "http://192.168.1.100";
const char* API_PATH   = "/api/v1/measurements";
const char* DEVICE_ID  = "esp32-ina219-01";
const char* API_KEY    = "your-api-key-here";
const bool  USE_HTTPS  = false;
```

### Configuration Reference

| Constant | Example | Description |
|----------|---------|-------------|
| `WIFI_SSID` | `"HomeNetwork"` | Your WiFi network name (2.4 GHz) |
| `WIFI_PASSWORD` | `"password123"` | Your WiFi password |
| `API_BASE` | `"http://192.168.1.100"` | BuckPow server URL (no trailing `/`) |
| `API_PATH` | `"/api/v1/measurements"` | API endpoint path (don't change) |
| `DEVICE_ID` | `"esp32-ina219-01"` | Unique device identifier |
| `API_KEY` | `"a1b2c3..."` | Device API key (empty for no auth) |
| `USE_HTTPS` | `false` | `true` for HTTPS connections |

### Finding the API Key

The API key is shown masked in the device list. To get the full key:

1. Go to **Devices** in the dashboard
2. Click the **Key** button on your device
3. Copy the full key from the modal

Or via API:

```bash
curl http://localhost:8000/api/v1/devices/<device-id>/key \
  -H 'Authorization: Bearer <jwt-token>'
```

## Step 5 — Upload and Test

1. Upload the firmware to your ESP32/ESP8266 (see [Measurement Node](measurement-node.md#uploading-firmware))
2. Open the Serial Monitor at **115200 baud**
3. Wait for the connection sequence:

```
BuckPow INA219 Firmware v1.1.0
Host: http://192.168.1.100:8000
Proto: HTTP
Key:   a1b2****ef01
Connecting to WiFi.... connected
IP: 192.168.1.42
INA219 detected
OK id=esp32-ina219-01
OK id=esp32-ina219-01
```

4. Open the BuckPow dashboard — your device should appear with status **online**

## Step 6 — Verify in Dashboard

1. Navigate to **Dashboard** in the sidebar
2. Check the **Devices** card — your device should show as online
3. Select the device's session (if running) to view live charts
4. Verify measurements are updating every few seconds

<!-- TODO: Replace with dashboard verification screenshot -->

## HTTPS Configuration

For secure connections, enable HTTPS in the firmware:

```cpp
const char* API_BASE  = "https://your-domain.com";
const bool  USE_HTTPS = true;
```

### Using Let's Encrypt

If your BuckPow server uses a Let's Encrypt certificate:

```cpp
const char* API_BASE  = "https://your-domain.com";
const bool  USE_HTTPS = true;
```

!!! warning "Certificate verification"
    The firmware uses `setInsecure()` which skips SSL certificate verification. For production, consider implementing certificate pinning.

### Self-Signed Certificates

For self-signed certificates, you may need to add the CA certificate to the firmware. This is not supported by the default firmware — consider using a reverse proxy with a valid certificate.

## Multiple Devices

Each device needs a unique `DEVICE_ID`. Configure each node with a different ID:

```cpp
// Device 1
const char* DEVICE_ID = "esp32-lab-01";

// Device 2
const char* DEVICE_ID = "esp32-lab-02";

// Device 3
const char* DEVICE_ID = "esp8266-office-01";
```

Each device gets its own API key from the BuckPow dashboard.

## Changing Server Address

If you move your BuckPow server to a new address:

1. Update `API_BASE` in the firmware
2. Re-upload the firmware
3. The device will register with the new server automatically

No other changes needed — the `DEVICE_ID` remains the same.

## Connection Troubleshooting

### WiFi Won't Connect

```
WiFi timeout!
Running offline.
```

- Verify `WIFI_SSID` and `WIFI_PASSWORD` are correct
- Ensure the network is 2.4 GHz (ESP8266 doesn't support 5 GHz)
- Move the device closer to the router
- Check if MAC filtering is enabled on the router

### Device Not Appearing in Dashboard

1. Check Serial Monitor for errors
2. Verify `API_BASE` points to the correct server
3. Test connectivity from a computer:

```bash
curl -X POST http://<server-ip>:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"test","bus_voltage":5.0,"shunt_voltage":50,"current":150,"power":750}'
```

4. Check if the device is disabled in the dashboard

### HTTP 401 Unauthorized

```
HTTP 401
```

- Verify `API_KEY` matches the device in BuckPow
- Ensure `DEVICE_AUTH_ENABLED=true` on the server
- Check for extra whitespace in the API key

### HTTP 403 Forbidden

```
HTTP 403
```

- The `device_id` in the firmware doesn't match the authenticated device
- The device is disabled in the dashboard
- The API key belongs to a different device

### HTTP 400 Bad Request

```
HTTP 400
```

- Check the measurement payload format
- Ensure all required fields are present: `device_id`, `bus_voltage`, `shunt_voltage`, `current`, `power`

### API Unreachable

```
API unreachable
```

- Verify the server is running
- Check network connectivity (ping the server)
- Ensure firewall rules allow port 8000
- If using HTTPS, verify the certificate is valid

### Firmware Outdated

The API returns a header `X-Firmware-Outdated: true` when the device firmware is below the minimum version. Update to the latest firmware from the repository.

### Intermittent Failures

If measurements succeed sometimes but fail other times:

- WiFi signal may be weak — move the device closer to the router
- The server may be overloaded — check server logs
- Network congestion — increase `INTERVAL_MS` to reduce request frequency

## Rate Limits

BuckPow limits measurement ingestion to **60 requests per minute** per API key. If you exceed this:

- Increase `INTERVAL_MS` in the firmware
- The device will receive HTTP 429 responses
- The firmware backs off for 10 seconds after failures

For high-frequency sampling, consider:

- Using a shorter interval (e.g., 2 seconds instead of 1)
- Sampling locally and sending aggregated data
- Using multiple devices with separate API keys
