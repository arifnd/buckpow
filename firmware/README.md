# BakPow Firmware — ESP32/ESP8266 + INA219

Arduino sketch for the BakPow power monitoring dashboard. Sends INA219 readings (voltage, current, power) via HTTP POST to the BakPow API.

## Wiring

| INA219 | ESP32 | ESP8266 |
|--------|-------|---------|
| VCC    | 3.3V  | 3.3V    |
| GND    | GND   | GND     |
| SCL    | GPIO 22 | D1 (GPIO 5) |
| SDA    | GPIO 21 | D2 (GPIO 4) |

## Required Libraries

Install via Arduino Library Manager (`Tools → Manage Libraries`):

- **Adafruit INA219** by Adafruit
- **ArduinoJson** by Benoit Blanchon

## Configuration

Edit these values near the top of `bakpow_ina219.ino`:

```cpp
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";
const char* API_BASE      = "http://192.168.1.100:5001";
const char* DEVICE_ID     = "esp32-ina219-01";
```

| Setting | Description |
|---|---|
| `WIFI_SSID` / `WIFI_PASSWORD` | Your 2.4 GHz WiFi credentials |
| `API_BASE` | BakPow server address and port |
| `DEVICE_ID` | Unique identifier for this device (auto-registers on first reading) |
| `INTERVAL_MS` | Milliseconds between readings (default: 1000) |

## Measurement Range

| Parameter | Range |
|---|---|
| Bus voltage | 0–26V |
| Current | ±3.2A (0.1Ω shunt) |
| Resolution | ~0.1 mA |

INA219 is calibrated via `setCalibration_32V_2A()` — despite the name, this gives optimal accuracy for up to **3.2A** with the standard 0.1Ω shunt resistor.

## WiFi Behavior

- **Startup** — tries to connect for 30 seconds (`WIFI_TIMEOUT`), then continues even if WiFi is unavailable.
- **Runtime** — if disconnected, retries every 30 seconds. Readings are skipped until WiFi reconnects.

## API Unreachable

When the server doesn't respond or returns an error, the sketch backs off for 10 seconds before retrying. This prevents spamming retries on a down server.

## Serial Output

Status messages print over Serial at 115200 baud. The sketch runs normally with or without a Serial monitor connected.

## Upload

1. Select your board (`Tools → Board → ESP32 Dev Module` or `Generic ESP8266 Module`)
2. Select the correct port
3. Click **Upload**

Open `Serial Monitor` (115200 baud) to verify WiFi connection and readings.

## Data Sent

Each POST contains:

```json
{
  "device_id": "esp32-ina219-01",
  "bus_voltage": 5.12,
  "shunt_voltage": 82.0,
  "current": 241.0,
  "power": 1234.0
}
```

- `bus_voltage` — load voltage (V)
- `shunt_voltage` — shunt voltage (mV)
- `current` — current draw (mA)
- `power` — power consumption (mW)
