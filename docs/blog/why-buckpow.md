# Why BuckPow

Most IoT dashboards answer: "What is happening right now?"

BuckPow answers engineering questions.

---

## The Problem

Building low-power devices involves guesswork.

- "How long will my battery last?"
- "Which firmware version uses less power?"
- "Is my solar panel big enough?"

Traditional IoT dashboards show live voltage and current. They don't help you **compare**, **benchmark**, or **understand** energy behavior over time.

## The Gap

Energy measurement is treated as an afterthought. Developers wire up a multimeter, take a few readings, and make decisions based on snapshots.

What's missing:

- **Session-based recording** — Compare "before" and "after" firmware changes
- **Energy accumulation** — Calculate total Wh, not just instantaneous W
- **Benchmarking** — Overlay multiple sessions to find differences
- **Reproducibility** — Run the same experiment twice and compare results

## BuckPow's Approach

BuckPow treats every measurement as part of an engineering experiment.

### Measurements → Sessions → Benchmarks

1. **Measure** — Collect voltage, current, power, energy from edge devices
2. **Session** — Group measurements into named experiments
3. **Benchmark** — Compare sessions to find energy differences

### Example Workflow

```
1. Flash firmware v1.0 → Start session "FW v1.0 baseline"
2. Run workload for 1 hour
3. Stop session
4. Flash firmware v1.1 → Start session "FW v1.1 optimization"
5. Run same workload for 1 hour
6. Stop session
7. Benchmark → v1.1 uses 23% less energy
```

## Who It's For

| User | Use Case |
|------|----------|
| **Makers** | Optimize battery life for wearables |
| **Researchers** | Profile TinyML inference energy |
| **Engineers** | Validate power supply designs |
| **Educators** | Teach energy-aware programming |
| **Hobbyists** | Characterize Raspberry Pi energy consumption |

## Design Principles

### Self-Hosted

Your data stays on your server. No cloud dependency.

### Open Source

MIT licensed. Modify, extend, deploy anywhere.

### Hardware Agnostic

Start with ESP32 + INA219. Add Raspberry Pi, Linux agents, MQTT devices later.

### Session-Oriented

Every measurement belongs to a session. Every session is an experiment.

## What Makes It Different

| Feature | Traditional Dashboard | BuckPow |
|---------|----------------------|---------|
| Live characterization | Yes | Yes |
| Session recording | No | Yes |
| Energy accumulation | No | Yes (Wh) |
| Benchmark comparison | No | Yes |
| Device threshold alerts | Sometimes | Yes |
| CSV/XLSX export | Sometimes | Yes |
| Self-hosted | Varies | Yes |

## Roadmap

Planned features:

- Raspberry Pi power agent
- Linux power agent
- INA226 support
- MQTT device ingestion
- PZEM-004T support
- Multi-user collaboration
- API webhooks
- Grafana integration

## Try It

```bash
git clone https://github.com/arifnd/buckpow.git
cd buckpow
docker compose up -d
```

Open http://localhost:8000 and start measuring.
