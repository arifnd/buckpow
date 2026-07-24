# Firmware

Arduino sketches for ESP32/ESP8266 + INA219 power monitors.

---

## Overview

BuckPow provides two firmware variants:

| Sketch | Display | Version | Interval |
|--------|---------|---------|----------|
| `buckpow_ina219` | None (Serial only) | 1.2.0 | 1s |
| `buckpow_ina219_oled` | SSD1306 128x32 OLED | 1.2.0 | 5s |
| `buckpow_ina219_captive` | None (Web UI) | 1.2.0 | Configurable |

Both sketches support **ESP32** and **ESP8266** with the INA219 current/power sensor.

## Hardware Requirements

### Components

| Component | Quantity | Notes |
|-----------|----------|-------|
| ESP32 or ESP8266 | 1 | Dev board (e.g. ESP32-DevKitC, NodeMCU) |
| INA219 breakout | 1 | I2C address 0x40 (default) |
| SSD1306 OLED | 1 | I2C address 0x3C (OLED variant only) |
| Jumper wires | 6-8 | For I2C connections |
| USB cable | 1 | For programming and serial monitor |

### Wiring

#### INA219 to ESP32/ESP8266

| INA219 Pin | ESP32 | ESP8266 |
|------------|-------|---------|
| VCC | 3.3V | 3.3V |
| GND | GND | GND |
| SCL | GPIO 22 | D1 (GPIO 5) |
| SDA | GPIO 21 | D2 (GPIO 4) |

#### OLED (I2C Shared Bus)

| SSD1306 Pin | ESP32 | ESP8266 |
|-------------|-------|---------|
| VCC | 3.3V | 3.3V |
| GND | GND | GND |
| SCL | GPIO 22 | D1 (GPIO 5) |
| SDA | GPIO 21 | D2 (GPIO 4) |

!!! info "Shared I2C bus"
    INA219 (0x40) and SSD1306 (0x3C) share the same I2C bus. No additional wiring needed.

## Configuration

Edit these constants near the top of each sketch:

### WiFi Settings

```cpp
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";
```

### API Settings

```cpp
const char* API_BASE   = "http://192.168.100.16:8000";
const char* API_PATH   = "/api/v1/measurements";
const char* NODE_ID   = "esp32-ina219-01";
const char* API_KEY    = "";
const bool  USE_HTTPS  = false;
```

| Setting | Description |
|---------|-------------|
| `API_BASE` | BuckPow server URL (e.g. `http://192.168.1.100:8000`) |
| `API_PATH` | API endpoint (default: `/api/v1/measurements`) |
| `NODE_ID` | Unique node ID (auto-registers on first reading) |
| `API_KEY` | API key for authentication; leave empty for dev mode |
| `USE_HTTPS` | Set `true` for HTTPS (uses `setInsecure()` — no cert verification) |

### Timing Settings

```cpp
const unsigned long INTERVAL_MS  = 1000;   // 1 second
const unsigned long WIFI_TIMEOUT = 30000;  // 30 seconds
const unsigned long RETRY_MS     = 10000;  // 10 seconds
```

| Setting | Description |
|---------|-------------|
| `INTERVAL_MS` | Milliseconds between readings (1000 = 1s, 5000 = 5s) |
| `WIFI_TIMEOUT` | WiFi connection timeout |
| `RETRY_MS` | Backoff after API failure |

## Required Libraries

Install via Arduino Library Manager:

### buckpow_ina219

| Library | Author |
|---------|--------|
| Adafruit INA219 | Adafruit |
| ArduinoJson | Benoit Blanchon |

### buckpow_ina219_oled

| Library | Author |
|---------|--------|
| Adafruit INA219 | Adafruit |
| Adafruit SSD1306 | Adafruit |
| Adafruit GFX Library | Adafruit |
| ArduinoJson | Benoit Blanchon |

### buckpow_ina219_captive

| Library | Author |
|---------|--------|
| Adafruit INA219 | Adafruit |
| ArduinoJson | Benoit Blanchon |

No external WiFi library required — uses built-in `DNSServer` and `WebServer` for the captive portal.

## Upload Instructions

### 1. Install Board Support

Open Arduino IDE → File → Preferences → Board Manager URLs:

- **ESP32**: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
- **ESP8266**: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`

Then install via **Tools → Board → Board Manager**.

### 2. Install Libraries

Open Arduino IDE → Tools → Manage Libraries:

Search and install the libraries listed above.

### 3. Select Board

- **ESP32**: Tools → Board → ESP32 Arduino → ESP32 Dev Module
- **ESP8266**: Tools → Board → ESP8266 Arduino → Generic ESP8266 Module

### 4. Select Port

Tools → Port → Select the correct serial port.

### 5. Upload

Click the Upload button or press Ctrl+U.

### 6. Verify

Open Serial Monitor (Tools → Serial Monitor) at **115200 baud**:

```
BuckPow INA219 Firmware v1.2.0
Host: http://192.168.100.16:8000
Proto: HTTP
Key:   ****
INA219 detected
Connecting to WiFi.... connected
IP: 192.168.100.42
OK id=esp32-ina219-01
OK id=esp32-ina219-01
```

## API Payload

Each reading sends a JSON POST request:

```json
{
  "device_id": "esp32-ina219-01",
  "firmware_version": "1.2.0",
  "bus_voltage": 5.12,
  "shunt_voltage": 82.0,
  "current": 241.0,
  "power": 1234.0
}
```

### Units

| Field | Unit | Description |
|-------|------|-------------|
| `bus_voltage` | V | Supply voltage |
| `shunt_voltage` | mV | Voltage across shunt resistor |
| `current` | mA | Current through load |
| `power` | mW | Power consumed |

### Response

Success returns `201 Created`:

```json
{
  "status": "success",
  "id": 1
}
```

## OLED Display

The OLED variant shows real-time readings on a 128x32 display:

```
V :   5.12 V
I : 241.0 mA
P : 1234.0 mW
E :  12.34 Wh 02:15
```

| Line | Content |
|------|---------|
| 0 | Voltage (V) |
| 1 | Current (mA) |
| 2 | Power (mW or W) |
| 3 | Energy (mWh or Wh) + Uptime (HH:MM) |

### Energy Calculation

Energy is accumulated locally:

```cpp
energyWh += power_mW * INTERVAL_MS / 3600000000.0;
```

!!! note "Wh = mW × ms / 3,600,000,000"
    This converts milliwatt-milliseconds to watt-hours.

## Captive Portal Variant

The `buckpow_ina219_captive` variant replaces hardcoded WiFi credentials with a custom captive portal web interface.

### How It Works

1. On first boot (or after `/setup`), the device starts in AP mode as `BuckPow-XXXXXXXX`
2. Connect to the AP — a captive portal page opens automatically
3. Scan and select a WiFi network from the list
4. Configure device name, server URL, API key, and sample interval (in seconds)
5. Save — device stores credentials in EEPROM and reboots
6. Device connects to the configured WiFi network

### Captive Portal Features

- Dark-themed UI matching the status page
- WiFi network list with signal strength (dBm) and lock icons for encrypted networks
- "Strong" badges on top 3 strongest signals
- Rescan button to refresh the network list
- Show/hide password toggle
- Sample interval input in seconds (stored as milliseconds internally)

### Status Page

After connecting to WiFi, visit `http://<device-ip>/` for a live status page showing:

- WiFi connection status, IP, RSSI
- Server connection status
- Live voltage and current readings
- Last upload time, uptime, and firmware version

### Reconfiguration

Visit `http://<device-ip>/setup` to clear WiFi credentials and re-enter the captive portal.

### Architecture

```
captive_portal.h   — Captive portal HTML (PROGMEM)
status_page.h      — Status page HTML (PROGMEM, split into HEAD/BODY/SCRIPT)
setup_page.h       — Reconfigure redirect page (PROGMEM)
```

The captive portal uses the built-in `DNSServer` to redirect all DNS queries to the device IP, triggering the captive portal prompt on phones and laptops. The `WebServer` serves the config page for all requests except `/scan` and `/save`.

## WiFi Behavior

### Connection

1. On boot, attempts WiFi connection
2. If timeout, logs "timeout" and continues offline
3. Every 30 seconds, retries WiFi if disconnected

### Offline Mode

- Readings are taken but not sent
- OLED displays last known values
- Serial prints skipped readings

## Error Handling

### API Failures

```cpp
if (code == 201) {
  // Success
} else if (code > 0) {
  Serial.print("HTTP ");
  Serial.println(code);  // e.g. HTTP 400, HTTP 401
} else {
  Serial.println("API unreachable");
}
```

### Backoff

After API failure, waits `RETRY_MS` (10s) before retrying:

```cpp
if (millis() - lastApiFail < RETRY_MS) return;
```

## Calibration

The INA219 is configured for **32V, 2A** range:

```cpp
ina219.setCalibration_32V_2A();
```

This provides:

- Bus voltage: 0–32V
- Shunt voltage: ±320mV
- Current: 0–2A (with 0.1mA resolution)
- Power: 0–64W

!!! warning "Shunt resistor"
    The default calibration assumes a 0.1Ω shunt resistor. If you use a different shunt, modify `setCalibration_32V_2A()` or use custom calibration.

## Compatibility

The BuckPow API includes a `min_firmware_version` field in the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "min_firmware_version": "1.0.0"
}
```

Devices below this version still send readings but are flagged in the device record.

## Local IP Reporting

After WiFi connects and the first successful API call is made, the firmware reports its local IP address via a separate endpoint:

```http
PATCH /api/v1/devices/local-ip
Authorization: Bearer <api_key>
Content-Type: application/json

{"local_ip": "192.168.1.100"}
```

This is called once per boot. An `ipReported` flag prevents resending on every measurement cycle.

## Serial Output Reference

### Boot Sequence

```
BuckPow INA219 Firmware v1.2.0
Host: http://192.168.100.16:8000
Proto: HTTP
Key:   ****
INA219 detected
Connecting to WiFi.... connected
IP: 192.168.100.42
```

### Successful Reading

```
OK id=esp32-ina219-01
```

### Errors

```
ERROR: INA219 not found. Check wiring.    # Sensor not detected
ERROR: SSD1306 OLED not found.            # OLED not detected (OLED variant)
HTTP 400                                   # Bad request
HTTP 401                                   # Invalid API key
API unreachable                            # Server down or network error
WiFi timeout!                              # Could not connect to WiFi
```
