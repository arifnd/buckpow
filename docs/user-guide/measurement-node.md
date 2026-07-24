# Measurement Node

Build and configure a power measurement node using ESP32/ESP8266 and INA219.

---

## Overview

<!-- TODO: Replace with actual hardware photo -->

A measurement node is a hardware device that reads voltage, current, and power from a DC circuit and sends measurements to BuckPow over WiFi.

The supported configuration uses:

- **MCU**: ESP32 or ESP8266
- **Sensor**: INA219 current/power sensor
- **Communication**: WiFi + HTTP POST

## Supported Hardware

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| MCU | ESP32 DevKit | ESP8266 (NodeMCU, Wemos D1) |
| Sensor | INA219 breakout board | — |
| Display | SSD1306 128x32 OLED *(optional)* | — |
| Power Supply | USB or regulated 3.3V–5V | — |

## INA219 Sensor

The INA219 is a I2C current/power monitor that measures:

| Measurement | Range | Resolution |
|-------------|-------|------------|
| Bus Voltage | 0–26V | 4 mV |
| Shunt Voltage | ±320 mV | 10 μV |
| Current | ±3.2A (with 0.1Ω shunt) | 0.1 mA |
| Power | Calculated from voltage × current | — |

### Calibration

BuckPow firmware uses the `setCalibration_32V_2A()` preset:

- **Bus voltage range**: 0–26V
- **Current range**: 0–3.2A
- **Shunt resistor**: 0.1Ω

## Wiring

<!-- TODO: Replace with actual wiring diagram -->

### ESP32 + INA219

```
INA219          ESP32
────────        ────────
VCC       →     3.3V
GND       →     GND
SCL       →     GPIO 22
SDA       →     GPIO 21
```

### ESP8266 + INA219

```
INA219          ESP8266
────────        ───────
VCC       →     3.3V
GND       →     GND
SCL       →     D1 (GPIO 5)
SDA       →     D2 (GPIO 4)
```

### Shared I2C Bus (with OLED)

Both INA219 and SSD1306 OLED share the same I2C bus:

| Device | I2C Address |
|--------|-------------|
| INA219 | `0x40` (default) |
| SSD1306 OLED | `0x3C` (default) |

Connect both devices to the same SDA/SCL pins. No additional wiring needed.

## Firmware Variants

| Variant | Display | Interval | Features |
|---------|---------|----------|----------|
| `buckpow_ina219` | None (Serial) | 1 second | Basic measurement node |
| `buckpow_ina219_oled` | SSD1306 128x32 | 5 seconds | Local display + energy accumulation |

### Base Variant (`buckpow_ina219`)

The simplest configuration. Reads measurements and sends them to the API. Debug output via Serial Monitor.

### OLED Variant (`buckpow_ina219_oled`)

<!-- TODO: Replace with actual OLED display photo -->

Adds a local display showing:

```
V :   5.12 V
I : 241.0 mA
P : 1234.0 mW
E :   0.34 Wh 00:15
```

- **Voltage**: Bus voltage in volts
- **Current**: Current draw in milliamps
- **Power**: Power consumption in milliwatts or watts (auto-scaled)
- **Energy**: Cumulative energy in milliwatt-hours or watt-hours (auto-scaled) + uptime

Energy is accumulated locally: `energyWh += power_mW × interval_ms / 3600000000`

## Measurement Range

| Parameter | Unit | Typical Range |
|-----------|------|---------------|
| Bus Voltage | V | 0–26V |
| Shunt Voltage | mV | 0–320 mV |
| Current | mA | 0–3200 mA |
| Power | mW | 0–80000 mW |

!!! tip "Low-power devices"
    For devices drawing less than 10 mA, consider using a lower calibration or a different shunt resistor for better accuracy.

## Data Format

Each measurement is sent as a JSON POST request:

```json
{
  "device_id": "esp32-ina219-01",
  "firmware_version": "1.2.0",
  "bus_voltage": 5.12,
  "shunt_voltage": 82,
  "current": 241,
  "power": 1234
}
```

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `device_id` | string | — | Unique device identifier |
| `firmware_version` | string | — | Firmware version string |
| `bus_voltage` | float | V | Bus voltage from INA219 |
| `shunt_voltage` | float | mV | Shunt voltage from INA219 |
| `current` | float | mA | Current draw from INA219 |
| `power` | float | mW | Power consumption from INA219 |

!!! info "Server-side conversion"
    BuckPow converts mA → A and mW → W when storing measurements.

## WiFi Behavior

### Connection

- Connects to 2.4 GHz WiFi network
- Timeout: 30 seconds
- Retries every 30 seconds if connection fails

### Auto-Reconnect

If WiFi disconnects during operation:

1. The device continues running
2. Every 30 seconds, it attempts to reconnect
3. Once reconnected, measurements resume sending

### API Error Backoff

If the API returns an error or is unreachable:

1. The device waits 10 seconds before retrying
2. After 10 seconds, it attempts the next measurement
3. This prevents flooding a down server

## Firmware Configuration

Edit these constants at the top of the sketch:

```cpp
// WiFi
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";

// BuckPow API
const char* API_BASE   = "http://192.168.100.16:8000";
const char* API_PATH   = "/api/v1/measurements";
const char* NODE_ID   = "esp32-ina219-01";
const char* API_KEY    = "";
const bool  USE_HTTPS  = false;

// Timing
const unsigned long INTERVAL_MS = 1000;
```

| Setting | Description |
|---------|-------------|
| `WIFI_SSID` | Your WiFi network name |
| `WIFI_PASSWORD` | Your WiFi password |
| `API_BASE` | BuckPow server URL (no trailing slash) |
| `API_PATH` | API endpoint path |
| `NODE_ID` | Unique node identifier (auto-registers if new) |
| `API_KEY` | Device API key (empty = no auth) |
| `USE_HTTPS` | `true` for HTTPS (uses `setInsecure()` — no cert verification) |
| `INTERVAL_MS` | Milliseconds between measurements |

## Uploading Firmware

### Prerequisites

1. Install [Arduino IDE](https://www.arduino.cc/en/software) or [PlatformIO](https://platformio.org/)
2. Install board support via Board Manager:
    - **ESP32**: `esp32` by Espressif
    - **ESP8266**: `esp8266` by ESP8266 Community
3. Install required libraries via Library Manager:

    **Base variant:**

    | Library | Author |
    |---------|--------|
    | Adafruit INA219 | Adafruit |
    | ArduinoJson | Benoit Blanchon |

    **OLED variant (additional):**

    | Library | Author |
    |---------|--------|
    | Adafruit SSD1306 | Adafruit |
    | Adafruit GFX Library | Adafruit |

### Upload Steps

1. Open the sketch (`.ino` file) in Arduino IDE
2. Edit WiFi and API configuration constants
3. Select board:
    - **ESP32**: `Tools > Board > ESP32 Dev Module`
    - **ESP8266**: `Tools > Board > Generic ESP8266 Module`
4. Select port: `Tools > Port`
5. Click **Upload**
6. Open **Serial Monitor** at **115200 baud** to verify

### Verify

<!-- TODO: Replace with actual Serial Monitor screenshot -->

After upload, the Serial Monitor should show:

```
BuckPow INA219 Firmware v1.2.0
Host: http://192.168.100.16:8000
Proto: HTTP
Key:   abcd****ef01
Connecting to WiFi.... connected
IP: 192.168.100.42
INA219 detected
OK id=esp32-ina219-01
OK id=esp32-ina219-01
```

## Using the API Key

1. Create a device in the BuckPow dashboard (or let it auto-register)
2. Copy the API key from the device detail page
3. Paste it into the `API_KEY` constant in the sketch
4. Upload the firmware

```cpp
const char* API_KEY = "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890";
```

## HTTPS Support

Set `USE_HTTPS = true` for encrypted communication:

```cpp
const char* API_BASE  = "https://your-domain.com";
const bool  USE_HTTPS = true;
```

!!! warning "Certificate verification"
    The firmware uses `setInsecure()` which skips SSL certificate verification. This is suitable for development. For production, consider implementing certificate pinning.

## Troubleshooting

### INA219 not found

```
ERROR: INA219 not found. Check wiring.
```

- Verify SDA/SCL connections
- Check that INA219 is powered (3.3V or 5V)
- Confirm I2C address (default `0x40`)
- Run an I2C scanner sketch to verify

### WiFi timeout

```
WiFi timeout!
Running offline.
```

- Check SSID and password
- Ensure 2.4 GHz network (ESP8266 doesn't support 5 GHz)
- Move the device closer to the router

### HTTP errors

```
HTTP 401
```

- Verify `API_KEY` matches the device in BuckPow
- Check that `DEVICE_AUTH_ENABLED` is `true` on the server

```
HTTP 400
```

- Verify the measurement payload format
- Check that `device_id` matches expectations

### API unreachable

```
API unreachable
```

- Verify `API_BASE` URL is correct
- Ensure the BuckPow server is running
- Check network connectivity (ping the server)
- Verify firewall rules allow port 8000

### OLED not displaying

```
ERROR: SSD1306 OLED not found. Check wiring.
```

- Verify SDA/SCL connections (shared I2C bus with INA219)
- Check OLED I2C address (default `0x3C`)
- Ensure 3.3V power supply
