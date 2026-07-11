# buckpow_ina219_oled — OLED Display Variant

Sends INA219 power readings to BuckPow via HTTP POST. Shows real-time readings on an SSD1306 128x32 OLED.

- **Version:** 1.1.0
- **Interval:** 5 seconds (`INTERVAL_MS = 5000`)
- **Board:** ESP32 or ESP8266

## Wiring

INA219 and SSD1306 share the same I2C bus:

| INA219 (addr `0x40`) | SSD1306 OLED (addr `0x3C`) | ESP32 | ESP8266 |
|----------------------|----------------------------|-------|---------|
| VCC | VCC | 3.3V | 3.3V |
| GND | GND | GND | GND |
| SCL | SCL | GPIO 22 | D1 (GPIO 5) |
| SDA | SDA | GPIO 21 | D2 (GPIO 4) |

No additional pins needed — both devices share `SCL` and `SDA`.

## Required Libraries

Install via **Arduino Library Manager** (`Tools > Manage Libraries`):

- **Adafruit INA219** by Adafruit
- **Adafruit SSD1306** by Adafruit
- **Adafruit GFX Library** by Adafruit
- **ArduinoJson** by Benoit Blanchon

## Configuration

Edit near the top of `buckpow_ina219_oled.ino`:

```cpp
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";
const char* API_BASE      = "http://192.168.1.100:8000";
const char* DEVICE_ID     = "esp32-ina219-oled";
const char* API_KEY       = "";
```

## OLED Display Layout

On startup, shows `BuckPow v1.1.0` for 2 seconds, then real-time readings:

```
V:   5.12 V
I:  241.0 mA
P:  1234  mW
E:  1.23Wh 01:23
```

| Line | Content |
|------|---------|
| 0 | Bus voltage (V) |
| 1 | Current draw (mA) |
| 2 | Power consumption (mW) |
| 3 | Cumulative energy (Wh) + uptime (HH:MM) |

- **Energy** accumulates as `Wh += power_mW × interval_s / 3600` — resets on reboot
- **Uptime** tracks time since `setup()` — shown as `HH:MM`
- During WiFi reconnection, the display shows connection status instead of readings

## Data Sent

```json
{
  "device_id": "esp32-ina219-oled",
  "firmware_version": "1.1.0",
  "bus_voltage": 5.12,
  "shunt_voltage": 82.0,
  "current": 241.0,
  "power": 1234.0
}
```

## Measurement Range

| Parameter | Range |
|-----------|-------|
| Bus voltage | 0–26 V |
| Current | ±3.2 A (0.1 Ω shunt) |
| Resolution | ~0.1 mA |

## WiFi Behavior

- **Startup** — tries to connect for 30 seconds, then continues even if WiFi is unavailable
- **Runtime** — if disconnected, retries every 30 seconds. Readings are skipped until WiFi reconnects

## Error Backoff

If the server is unreachable, waits 10 seconds before retrying. The OLED continues showing live readings during backoff.
