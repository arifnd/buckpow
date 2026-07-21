# Designing Energy Observability

How BuckPow evolved from a simple power monitor to an observability platform.

---

## From Monitoring to Observability

Power **monitoring** tells you the current draw. Power **observability** tells you why it changed, when it changed, and what changed.

### Monitoring

```
Voltage: 5.12V
Current: 241mA
Power: 1.23W
```

### Observability

```
Session "FW v1.1 baseline"
Device: esp32-01
Duration: 1h 32m
Energy: 1.85 Wh
Average Power: 1.21W
Peak Power: 2.34W
Comparison: 12% less than v1.0
```

## The Session Model

BuckPow's core insight: **every measurement belongs to a session**.

A session groups measurements into a meaningful unit:

- "Firmware v1.0 baseline test"
- "Battery discharge test #3"
- "Solar panel evaluation — cloudy day"
- "OTA update energy cost"

### Why Sessions Matter

| Without Sessions | With Sessions |
|------------------|---------------|
| 10,000 measurements | 10 experiments |
| No context | Named, timestamped |
| Can't compare | Benchmarkable |
| Just data | Engineering insights |

## Energy Calculation

BuckPow calculates energy from power and time:

```
Energy (Wh) = Σ Power (W) × Sampling Interval (h)
```

### Example

```
Reading 1: 1.2W at t=0s
Reading 2: 1.3W at t=1s
Reading 3: 1.1W at t=2s

Energy = (1.2 × 1/3600) + (1.3 × 1/3600) + (1.1 × 1/3600)
       = 0.000333 + 0.000361 + 0.000306
       = 0.001000 Wh
       = 1.0 mWh
```

### Why Accumulate on the Server

The server accumulates energy because:

1. **Consistency** — Same formula regardless of device firmware
2. **Accuracy** — Server has precise timestamps
3. **Flexibility** — Can recalculate with different intervals
4. **Aggregation** — Can sum across sessions

## The Three Pillars

### 1. Measure

Collect raw telemetry:

- Bus voltage (V)
- Shunt voltage (mV)
- Current (mA)
- Power (mW)

### 2. Analyze

Transform telemetry into insights:

- Energy accumulation (Wh)
- Statistical summaries (avg, min, max, p95)
- Threshold-based alerts
- Trend detection

### 3. Compare

Benchmark across sessions:

- Side-by-side charts
- Energy difference percentages
- Statistical significance
- Export for external analysis

## Architecture Decisions

### Why SQLite (for now)

- Zero configuration
- Single file database
- Perfect for self-hosted
- Easy backup (copy one file)
- Scales to millions of readings

### Why FastAPI

- Async support
- Automatic OpenAPI docs
- Type-safe with Pydantic
- Dependency injection
- Modern Python ecosystem

### Why HTMX

- No JavaScript build step
- Server-rendered pages
- SPA-like experience
- Progressive enhancement
- Works without JavaScript

### Why Tailwind CSS

- Utility-first styling
- Dark mode built-in
- No CSS files to manage
- Consistent design system
- Small bundle size

## The Data Model

```
User
 └── Project
      └── Device
           ├── Measurement (many)
           └── Session
                ├── Measurement (many)
                └── Benchmark (comparison)
```

### Key Relationships

| Relationship | Cardinality | Description |
|--------------|-------------|-------------|
| Project → Device | 1:N | Devices belong to projects |
| Device → Measurement | 1:N | Devices generate measurements |
| Device → Session | 1:N | Devices participate in sessions |
| Session → Measurement | 1:N | Sessions contain measurements |

## Alert Engine

Automatic alerts based on thresholds:

```
IF power > high_power_threshold THEN
  CREATE ALERT (critical, "High power on esp32-01")

IF current > high_current_threshold THEN
  CREATE ALERT (critical, "High current on esp32-01")

IF voltage < low_voltage_threshold THEN
  CREATE ALERT (warning, "Low voltage on esp32-01")
```

### Threshold Hierarchy

1. Device-specific thresholds (highest priority)
2. Project owner's user settings
3. Default values (2.5W, 0.5A, 4.5V)

## Future Directions

### Planned Features

- **Raspberry Pi Agent** — Monitor Pi power consumption
- **Linux Agent** — Server power monitoring
- **MQTT Ingestion** — Optional MQTT support
- **Webhooks** — Push alerts to Slack, Discord, email
- **Grafana Export** — Dashboard integration
- **Multi-user** — Team collaboration
- **API Keys** — Per-user API key management

### Long-term Vision

BuckPow becomes the standard tool for energy-aware development:

- Every firmware change is benchmarked
- Every hardware revision is compared
- Every deployment is monitored
- Energy becomes a first-class metric

## Lessons Learned

### 1. Start Simple

The first version was just a REST API and SQLite database. No dashboard, no sessions, no benchmarking.

### 2. Sessions Change Everything

Adding sessions transformed raw data into engineering experiments.

### 3. Self-Hosted Matters

Developers want control over their data. Self-hosted is a feature, not a limitation.

### 4. Hardware Agnostic

Start with ESP32, but design for any device. The API doesn't care what sends the data.

### 5. Export is Essential

CSV and XLSX export lets users analyze data in Excel, Python, R, or any tool.

## Conclusion

Energy observability is more than monitoring. It's about understanding, comparing, and improving. BuckPow makes energy a measurable, comparable, actionable metric.
