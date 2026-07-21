# Benchmark Case Study: Firmware Power Optimization

How BuckPow helped reduce ESP32 power consumption by 23% through firmware optimization.

---

## Background

A developer was building a battery-powered ESP32 sensor that wakes up every 5 seconds, reads a sensor, and transmits data via WiFi.

The goal: maximize battery life without changing hardware.

## Setup

### Hardware

- ESP32-DevKitC
- INA219 current sensor
- 18650 Li-ion battery (3.7V, 3000mAh)

### Firmware Variants

| Version | Description |
|---------|-------------|
| v1.0 | Baseline — WiFi always connected |
| v1.1 | Optimization — WiFi sleep between readings |
| v1.2 | Further optimization — Reduced TX power |

### BuckPow Configuration

```
Node ID: esp32-battery-test
Sampling Interval: 5 seconds
Session Duration: 1 hour each
```

## Experiment 1: Baseline (v1.0)

### Session: "FW v1.0 baseline"

```
Start: 2026-07-15 09:00:00
End:   2026-07-15 10:00:00
```

### Results

| Metric | Value |
|--------|-------|
| Average Power | 85.2 mW |
| Peak Power | 312.0 mW (WiFi TX) |
| Idle Power | 62.1 mW |
| Energy (1 hour) | 85.2 mWh |

### Observations

- WiFi radio stays on continuously
- Idle power is high due to WiFi polling
- Peak during transmission is significant

## Experiment 2: WiFi Sleep (v1.1)

### Session: "FW v1.1 WiFi sleep"

```
Start: 2026-07-15 11:00:00
End:   2026-07-15 12:00:00
```

### Changes

```cpp
// v1.1 — Added WiFi sleep
WiFi.disconnect();
esp_wifi_stop();

// Wake up, connect, transmit, disconnect
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
// ... transmit ...
WiFi.disconnect();
esp_wifi_stop();
```

### Results

| Metric | Value | vs v1.0 |
|--------|-------|---------|
| Average Power | 65.7 mW | -23% |
| Peak Power | 298.0 mW | -4.5% |
| Idle Power | 12.3 mW | -80% |
| Energy (1 hour) | 65.7 mWh | -23% |

### BuckPow Benchmark

```
Comparison: v1.0 vs v1.1

Average Power: 85.2 mW → 65.7 mW (-23%)
Energy:        85.2 mWh → 65.7 mWh (-23%)

The optimization reduced energy consumption by 23%.
```

## Experiment 3: Reduced TX Power (v1.2)

### Session: "FW v1.2 TX power"

```cpp
// v1.2 — Reduced WiFi TX power
esp_wifi_set_max_tx_power(40);  // 10dBm (default: 20dBm / 80mW)
```

### Results

| Metric | Value | vs v1.0 |
|--------|-------|---------|
| Average Power | 58.3 mW | -32% |
| Peak Power | 245.0 mW | -21% |
| Idle Power | 12.3 mW | -80% |
| Energy (1 hour) | 58.3 mWh | -32% |

### BuckPow Benchmark

```
Comparison: v1.0 vs v1.1 vs v1.2

v1.0: 85.2 mWh
v1.1: 65.7 mWh (-23%)
v1.2: 58.3 mWh (-32%)

v1.2 achieves 32% energy reduction over baseline.
```

## Battery Life Projection

### Formula

```
Battery Life (hours) = Battery Capacity (Wh) / Average Power (W)
```

### Calculations

| Version | Avg Power | Battery Life |
|---------|-----------|--------------|
| v1.0 | 85.2 mW | 3000mAh × 3.7V / 85.2mW = **130 hours** |
| v1.1 | 65.7 mW | 3000mAh × 3.7V / 65.7mW = **168 hours** |
| v1.2 | 58.3 mW | 3000mAh × 3.7V / 58.3mW = **190 hours** |

### Impact

```
v1.0 → v1.2: +60 hours (+46% battery life)
```

## Key Insights

### 1. WiFi is the Biggest Consumer

WiFi radio accounts for 70%+ of ESP32 power consumption. Sleeping between readings has the largest impact.

### 2. TX Power Matters

Reducing TX power from 20dBm to 10dBm saves 7mW average with minimal range impact (indoor use).

### 3. Idle Power Drops Dramatically

From 62mW to 12mW — an 80% reduction in idle power.

### 4. Peak Power is Less Important

For battery life, average power matters more than peak power. A 312mW peak that lasts 50ms is less impactful than 62mW idle for 4.95 seconds.

## How BuckPow Helped

### Without BuckPow

- Take multimeter readings manually
- Log to spreadsheet
- Compare visually
- Guess at battery life

### With BuckPow

- Automatic measurement collection
- Named sessions for each firmware version
- One-click benchmark comparison
- Precise energy calculation
- Export to CSV for further analysis

## Reproducing This Experiment

### 1. Set Up BuckPow

```bash
docker compose up -d
```

### 2. Flash Baseline Firmware

```bash
# Flash v1.0 (WiFi always on)
arduino-cli upload --fqbn esp32:esp32:esp32
```

### 3. Start Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <jwt>' \
  -d '{"name":"FW v1.0 baseline","device_id":1}'
```

### 4. Run Test

Wait 1 hour for data collection.

### 5. Stop Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/stop
```

### 6. Repeat for Each Version

Flash v1.1, create new session, run test, stop session.

### 7. Benchmark

Open http://localhost:8000/benchmark and select sessions to compare.

## Conclusion

BuckPow turned a vague goal ("reduce power consumption") into a measurable engineering process:

1. **Baseline** — Establish current consumption
2. **Optimize** — Make targeted changes
3. **Measure** — Verify impact with real data
4. **Compare** — Quantify improvement
5. **Project** — Estimate battery life

The result: 32% energy reduction, 46% longer battery life, and confidence in the numbers.
