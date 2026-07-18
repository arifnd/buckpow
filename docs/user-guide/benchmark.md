# Benchmark

Compare energy consumption across multiple experiment sessions.

---

## Overview

The Benchmark page lets you compare 2–3 finished sessions side-by-side. It shows a comparison table with key metrics and an overlay chart comparing power consumption over time.

<!-- TODO: Replace with benchmark page screenshot -->

## Use Cases

- Compare **firmware versions** to find the most efficient one
- Compare **hardware configurations** (e.g., different ESP32 boards)
- Compare **workloads** (e.g., idle vs. active vs. sleep mode)
- Compare **power sources** (e.g., battery vs. USB vs. solar)
- Validate **power optimizations** with before/after measurements

## How to Benchmark

### Step 1 — Run Multiple Sessions

Create and run separate sessions for each configuration you want to compare:

```bash title="Session 1: Firmware v1.0 idle"
curl -X POST http://localhost:8000/api/v1/sessions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <jwt-token>' \
  -d '{"name":"FW v1.0 Idle","device_id":1}'
```

```bash title="Session 2: Firmware v1.1 idle"
curl -X POST http://localhost:8000/api/v1/sessions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <jwt-token>' \
  -d '{"name":"FW v1.1 Idle","device_id":1}'
```

Start each session, collect data, then stop:

```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/start -H 'Authorization: Bearer <jwt-token>'
# ... wait for data ...
curl -X POST http://localhost:8000/api/v1/sessions/1/stop -H 'Authorization: Bearer <jwt-token>'
```

### Step 2 — Open Benchmark Page

Navigate to **Benchmark** in the sidebar.

### Step 3 — Select Sessions

1. Select the first session from **Session A** dropdown
2. Select the second session from **Session B** dropdown
3. Optionally select a third session from **Session C** dropdown
4. Click **Compare**

<!-- TODO: Replace with session selection screenshot -->

!!! info "Finished sessions only"
    Only **finished** sessions appear in the dropdowns. Make sure to stop your sessions before comparing.

### Step 4 — Review Results

The comparison shows:

- A **comparison table** with key metrics
- An **overlay chart** comparing power consumption over time

## Comparison Table

The table displays these metrics for each session:

| Metric | Description |
|--------|-------------|
| **Device** | Device name or ID |
| **Avg Power (W)** | Average power consumption |
| **Peak Power (W)** | Maximum power consumption |
| **Total Energy (Wh)** | Total energy consumed during the session |
| **Avg Current (A)** | Average current draw |
| **Voltage Std Dev** | Voltage stability (lower = more stable) |
| **Duration** | Session length (days, hours, minutes, seconds) |
| **Measurements** | Number of data points collected |
| **Started** | Session start timestamp |
| **Ended** | Session end timestamp |

<!-- TODO: Replace with comparison table screenshot -->

## Overlay Chart

The chart overlays power consumption from all selected sessions on the same time axis:

<!-- TODO: Replace with overlay chart screenshot -->

| Feature | Description |
|---------|-------------|
| **X-axis** | Time (hours:minutes:seconds) |
| **Y-axis** | Power (W) |
| **Lines** | One line per session (blue, red, green) |
| **Legend** | Session names in the top-right |
| **Interaction** | Hover to see exact values |

!!! tip "Comparing different durations"
    Sessions with different durations are aligned to their start time. The chart shows overlapping time periods for direct comparison.

## Interpreting Results

### Lower Average Power is Better

When comparing firmware versions or configurations, the session with **lower average power** is more energy efficient.

### Check Peak Power

A configuration with lower average power might have higher **peak power** spikes. Consider both metrics:

- **Average power**: Overall energy consumption
- **Peak power**: Maximum draw (important for battery sizing)

### Voltage Stability

**Voltage standard deviation** indicates how stable the power supply is:

- **Low std dev** (< 0.01): Very stable voltage
- **Medium std dev** (0.01–0.1): Acceptable stability
- **High std dev** (> 0.1): Unstable voltage — investigate

### Energy Efficiency

**Total energy** depends on both power consumption and duration. When comparing:

- Use the **same duration** for fair comparison, or
- Compare **average power** instead of total energy

## Example: Firmware Comparison

### Scenario

Compare two firmware versions on an ESP32 + INA219:

- **Firmware v1.0**: Sends data every 1 second
- **Firmware v1.1**: Optimized with batch sends every 5 seconds

### Setup

1. Upload firmware v1.0, run for 10 minutes
2. Upload firmware v1.1, run for 10 minutes
3. Compare the two sessions

### Results

| Metric | FW v1.0 | FW v1.1 | Difference |
|--------|---------|---------|------------|
| Avg Power | 0.185 W | 0.162 W | -12.4% |
| Peak Power | 0.234 W | 0.198 W | -15.4% |
| Total Energy | 0.031 Wh | 0.027 Wh | -12.9% |

**Conclusion**: Firmware v1.1 is ~12% more energy efficient.

## API Reference

### Compare Sessions

```bash
GET /api/v1/benchmark/compare?sessions=1,2
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sessions` | string | Yes | Comma-separated session IDs (2–3) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/benchmark/compare?sessions=1,2,3" \
  -H 'Authorization: Bearer <jwt-token>'
```

**Response:**

```json
{
  "sessions": [
    {
      "session_id": 1,
      "session_name": "FW v1.0 Idle",
      "device_name": "esp32-ina219-01",
      "avg_power": 0.185,
      "peak_power": 0.234,
      "total_energy": 0.031,
      "avg_current": 0.036,
      "voltage_stddev": 0.008,
      "duration": 600,
      "measurement_count": 600,
      "started_at": "2026-07-18T10:00:00Z",
      "ended_at": "2026-07-18T10:10:00Z",
      "chart_data": {
        "labels": ["10:00:00", "10:00:01", "..."],
        "power": [0.182, 0.185, "..."]
      }
    },
    {
      "session_id": 2,
      "session_name": "FW v1.1 Idle",
      "device_name": "esp32-ina219-01",
      "avg_power": 0.162,
      "peak_power": 0.198,
      "total_energy": 0.027,
      "avg_current": 0.032,
      "voltage_stddev": 0.006,
      "duration": 600,
      "measurement_count": 600,
      "started_at": "2026-07-18T10:15:00Z",
      "ended_at": "2026-07-18T10:25:00Z",
      "chart_data": {
        "labels": ["10:15:00", "10:15:01", "..."],
        "power": [0.158, 0.161, "..."]
      }
    }
  ]
}
```

### Validation Rules

| Rule | Description |
|------|-------------|
| Minimum sessions | 2 |
| Maximum sessions | 3 |
| Session status | Must be `finished` |
| Same device | Recommended (not required) |

!!! tip "Same device for fair comparison"
    For the most accurate comparison, use the same device for all sessions. This eliminates hardware variability.

## Tips for Good Benchmarks

### Control Variables

Keep everything the same except what you're testing:

| Variable | Keep Constant | Why |
|----------|---------------|-----|
| **Device** | Same ESP32/ESP8266 | Hardware differences affect power |
| **Power supply** | Same voltage source | Different supplies = different readings |
| **Duration** | Same length | Fair energy comparison |
| **Environment** | Same temperature | Temperature affects power consumption |
| **Load** | Same workload | Different tasks use different power |

### Run Multiple Trials

For statistical significance, run 3+ trials of each configuration:

1. Run Session A (trial 1)
2. Run Session B (trial 1)
3. Run Session A (trial 2)
4. Run Session B (trial 2)
5. Run Session A (trial 3)
6. Run Session B (trial 3)

Compare average results across trials.

### Use Consistent Sampling

Use the same `sampling_interval` for all sessions. Different intervals affect:

- Measurement resolution
- Total number of data points
- Energy calculation accuracy

### Document Your Experiments

Use session descriptions to record:

- Firmware version
- Hardware configuration
- Environmental conditions
- Any anomalies observed

## Troubleshooting

### No Finished Sessions

Ensure you've stopped your sessions before comparing. Only **finished** sessions appear in the dropdowns.

### Sessions Not Matching

If sessions don't appear in the comparison:

- Verify both sessions are **finished** (not running or draft)
- Check that session IDs are correct
- Ensure you have at least 2 valid sessions

### Chart Not Showing Data

If the overlay chart is empty:

- Verify both sessions have measurements
- Check that the sessions have overlapping time periods
- Ensure the API is accessible from the dashboard

### Different Session Durations

Sessions with very different durations may not overlay well. Consider:

- Running sessions for the same duration
- Comparing only overlapping time periods
- Using average power instead of total energy
