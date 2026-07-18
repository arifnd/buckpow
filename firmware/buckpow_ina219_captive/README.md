# BuckPow INA219 - Captive Portal Firmware

Power monitor firmware with custom captive portal setup — no code editing required.

## Features

- **Custom Captive Portal** — Connect to device WiFi, configure via dark-themed web UI
- **WiFi Network List** — Scan and select from available networks with signal strength and lock icons
- **Status Page** — Live voltage, current, and device info at device IP
- **EEPROM Config** — WiFi credentials and device settings saved, no reflash needed
- **Auto-Reconnect** — Falls back to AP mode if WiFi/server fails
- **Show/Hide Password** — Toggle WiFi password visibility in the config form

## Required Libraries

Install via Arduino Library Manager:

| Library | Author |
|---------|--------|
| Adafruit INA219 | Adafruit |
| ArduinoJson | Benoit Blanchon |

No external WiFi manager library required — uses built-in `DNSServer` and `WebServer`.

## Wiring

```
INA219    ESP32       ESP8266
──────    ─────       ───────
VCC   →   3.3V        3.3V
GND   →   GND         GND
SCL   →   GPIO 22     D1 (GPIO 5)
SDA   →   GPIO 21     D2 (GPIO 4)
```

## Setup

1. Upload `buckpow_ina219_captive.ino` to your board
2. Open Serial Monitor (115200 baud)
3. Device creates WiFi AP: `BuckPow-XXXXXXXX`
4. Connect to AP from phone/laptop
5. Captive portal opens automatically
6. Scan and select your WiFi network from the list
7. Fill in the form:

| Field | Description |
|-------|-------------|
| WiFi Network | Select from scanned networks (top 3 strongest highlighted) |
| Password | WiFi password (show/hide toggle available) |
| Device Name | Unique ID (e.g. `esp32-ina219-01`) |
| Location | Optional label |
| BuckPow URL | Your server URL |
| API Key | Device API key (optional) |
| Sample Interval | How often to send readings (in seconds) |

8. Click **Save & Connect** — device reboots and connects

## Captive Portal

The captive portal uses a dark-themed UI matching the status page. Features include:

- **WiFi list** with signal strength (dBm), lock icons for encrypted networks, and "Strong" badges for top 3 signals
- **Rescan button** to refresh the network list
- **Network input** showing the selected SSID
- **Password field** with show/hide checkbox
- **Device configuration** (name, location)
- **Server configuration** (URL, API key)
- **Sample interval** input in seconds

## Status Page

After configuration, visit `http://<device-ip>/` to see:

- WiFi connection status, IP address, signal strength (RSSI)
- Server connection status
- Live voltage and current readings
- Last upload time and uptime
- Firmware version

## Reconfigure

Visit `http://<device-ip>/setup` to clear WiFi credentials and re-enter the captive portal.

## First Boot Behavior

1. No saved config → enters AP mode automatically
2. User configures via captive portal
3. WiFi credentials and device settings saved to EEPROM
4. Device reboots and connects to saved network
5. If WiFi connection fails → falls back to captive portal
