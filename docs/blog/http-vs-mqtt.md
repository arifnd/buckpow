# HTTP vs MQTT for IoT Power Monitoring

Why BuckPow uses HTTP instead of MQTT for device communication.

---

## The Question

When building an IoT power monitor, should you use HTTP or MQTT for sending measurements to the server?

## Short Answer

**HTTP** for BuckPow. Here's why.

## MQTT: What It Does Well

MQTT is a lightweight publish-subscribe protocol designed for constrained devices:

- **Low overhead** — 2-byte fixed header
- **Persistent connection** — No TCP handshake per message
- **QoS levels** — Guaranteed delivery (0, 1, 2)
- **Retained messages** — Last value available on subscribe
- **Wildcard topics** — Hierarchical subscriptions

### When MQTT Shines

- Thousands of devices publishing simultaneously
- Unreliable networks with frequent disconnects
- Real-time dashboards requiring sub-second latency
- Bidirectional control (device ← server)

## Why BuckPow Chose HTTP

### 1. Simplicity

HTTP is universal. Every language, every platform, every device has an HTTP client.

```cpp
// ESP32 HTTP — no special library needed
HTTPClient http;
http.begin(url);
http.addHeader("Content-Type", "application/json");
int code = http.POST(payload);
```

MQTT requires:

- A broker (Mosquitto, EMQX, HiveMQ)
- Client library (PubSubClient, AsyncMqttClient)
- Topic management
- Connection lifecycle handling

### 2. No Broker Dependency

HTTP is point-to-point. Device talks directly to server.

MQTT requires a broker running 24/7:

```
Device → MQTT Broker → (your app subscribes)
```

HTTP:

```
Device → BuckPow API
```

One less thing to deploy, configure, and monitor.

### 3. Standard Authentication

HTTP uses standard `Authorization` headers:

```http
POST /api/v1/measurements HTTP/1.1
Authorization: Bearer <api_key>
Content-Type: application/json
```

MQTT authentication is broker-specific and varies by implementation.

### 4. RESTful API Design

HTTP maps naturally to REST:

| Operation | HTTP Method |
|-----------|-------------|
| Send measurement | `POST /api/v1/measurements` |
| Get measurements | `GET /api/v1/measurements` |
| Export data | `GET /api/v1/measurements/export/csv` |

MQTT is topic-based, not resource-based. You lose REST semantics.

### 5. Firewall Friendly

HTTP (port 80/443) passes through corporate firewalls, proxies, and load balancers.

MQTT (port 1883/8883) often requires firewall rules and special configuration.

### 6. Device Auto-Registration

BuckPow auto-registers unknown devices on first `POST`:

```json
POST /api/v1/measurements
{
  "device_id": "esp32-01",
  "bus_voltage": 5.12,
  "current": 241,
  "power": 1234
}
```

No pre-configuration needed. The device just works.

## The Trade-offs

### What You Lose with HTTP

| MQTT Feature | HTTP Equivalent |
|--------------|-----------------|
| Persistent connection | New TCP connection per request |
| QoS guarantees | Application-level retry |
| Bidirectional push | Polling or WebSocket |
| Wildcard subscriptions | REST queries with filters |

### What BuckPow Gains

| Benefit | Impact |
|---------|--------|
| No broker | Simpler deployment |
| Standard auth | Easier integration |
| REST semantics | Clear API design |
| Universal support | Any device can connect |

## BuckPow's Retry Strategy

Since HTTP has no built-in QoS, BuckPow implements retry with backoff:

```cpp
// Firmware retry logic
if (millis() - lastApiFail < RETRY_MS) return;  // 10s backoff

int code = http.POST(payload);
if (code == 201) {
  // Success
} else {
  lastApiFail = millis();  // Start backoff
}
```

Server-side rate limiting prevents abuse:

```
POST /api/v1/measurements — 60 requests/minute per API key
```

## When MQTT Would Be Better

BuckPow's HTTP approach works well for:

- Small to medium deployments (< 100 devices)
- Local network monitoring
- Experiment-based workflows

Consider MQTT if you need:

- Real-time bidirectional control
- Thousands of devices publishing simultaneously
- Ultra-low latency (< 100ms)
- Aggressive power saving (persistent connection)

## Future: MQTT Support

BuckCow may add MQTT as an optional ingestion endpoint:

```
mqtt://broker:1883/buckpow/measurements
```

This would allow MQTT-native devices to participate alongside HTTP devices.

## Conclusion

HTTP is the right choice for BuckPow's use case:

- **Simple** — No broker, no extra dependencies
- **Universal** — Works with any device, any language
- **RESTful** — Clean API design
- **Battle-tested** — Decades of tooling and support

MQTT is excellent for other scenarios. For a self-hosted energy observability platform, HTTP wins on simplicity.
