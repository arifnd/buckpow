# BuckPow Firmware

Arduino sketches for ESP32/ESP8266 + INA219 that send power readings to the BuckPow API. Part of the BuckPow energy observability platform.

| Sketch | Display | Version | Interval |
|--------|---------|---------|----------|
| [`buckpow_ina219`](buckpow_ina219/) | None (Serial only) | 1.0.0 | 1s |
| [`buckpow_ina219_oled`](buckpow_ina219_oled/) | SSD1306 128x32 OLED | 1.1.0 | 5s |

## Common Wiring

| INA219 | ESP32 | ESP8266 |
|--------|-------|---------|
| VCC | 3.3V | 3.3V |
| GND | GND | GND |
| SCL | GPIO 22 | D1 (GPIO 5) |
| SDA | GPIO 21 | D2 (GPIO 4) |

See per-sketch READMEs for OLED wiring and variant-specific details.

## Configuration

Edit these defines near the top of the sketch:

| Define | Default | Description |
|--------|---------|-------------|
| `WIFI_SSID` / `WIFI_PASSWORD` | — | 2.4 GHz WiFi credentials |
| `API_BASE` | — | BuckPow server address (e.g. `http://192.168.1.100:8000`) |
| `DEVICE_ID` | — | Unique device ID (auto-registers on first reading) |
| `API_KEY` | (empty) | API key for device auth; leave empty for dev |
| `INTERVAL_MS` | 1000 / 5000 | Milliseconds between readings |
| `FW_VERSION` | 1.0.0 / 1.1.0 | Sent with each reading for compatibility checks |

## Upload

1. Install board support: **ESP32** or **ESP8266** via Arduino Board Manager
2. Install required libraries listed in each sketch's README
3. Select board (`Tools > Board > ESP32 Dev Module` / `Generic ESP8266 Module`)
4. Select port and click **Upload**
5. Open **Serial Monitor** at 115200 baud to verify

## Compatibility

The API health endpoint (`GET /api/v1/health`) returns `min_firmware_version`. Devices below this version still send readings, but the API flags them with a response header and updates the device record.
