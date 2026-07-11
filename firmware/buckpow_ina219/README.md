# buckpow_ina219 — Base Variant

Sends INA219 power readings to BuckPow via HTTP POST. No display — status and readings via Serial only.

- **Version:** 1.0.0
- **Interval:** 1 second (`INTERVAL_MS = 1000`)
- **Board:** ESP32 or ESP8266

## Wiring

| INA219 | ESP32 | ESP8266 |
|--------|-------|---------|
| VCC | 3.3V | 3.3V |
| GND | GND | GND |
| SCL | GPIO 22 | D1 (GPIO 5) |
| SDA | GPIO 21 | D2 (GPIO 4) |

## Required Libraries

Install via **Arduino Library Manager** (`Tools > Manage Libraries`):

- **Adafruit INA219** by Adafruit
- **ArduinoJson** by Benoit Blanchon

## Configuration

Edit near the top of `buckpow_ina219.ino`:

```cpp
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";
const char* API_BASE      = "http://192.168.1.100:8000";
const char* DEVICE_ID     = "esp32-ina219-01";
const char* API_KEY       = "";
```

- `API_BASE` — BuckPow server address and port (default: `8000`)
- `DEVICE_ID` — unique identifier, auto-registers on first reading
- `API_KEY` — optional, leave empty when auth is disabled

## Data Sent

```json
{
  "device_id": "esp32-ina219-01",
  "firmware_version": "1.0.0",
  "bus_voltage": 5.12,
  "shunt_voltage": 82.0,
  "current": 241.0,
  "power": 1234.0
}
```

- `bus_voltage` — load voltage (V)
- `shunt_voltage` — voltage across shunt resistor (mV)
- `current` — current draw (mA)
- `power` — power consumption (mW)

## Measurement Range

| Parameter | Range |
|-----------|-------|
| Bus voltage | 0–26 V |
| Current | ±3.2 A (0.1 Ω shunt) |
| Resolution | ~0.1 mA |

Calibrated via `setCalibration_32V_2A()` — optimal accuracy up to ~3.2 A with the standard 0.1 Ω shunt.

## Serial Output

Opens Serial at 115200 baud. Shows WiFi connection status, HTTP response codes, and measurement values. The sketch runs normally with or without a Serial monitor connected.

## WiFi Behavior

- **Startup** — tries to connect for 30 seconds, then continues even if WiFi is unavailable
- **Runtime** — if disconnected, retries every 30 seconds. Readings are skipped until WiFi reconnects

## Error Backoff

If the server is unreachable or returns an error, the sketch waits 10 seconds before retrying to avoid spamming.
