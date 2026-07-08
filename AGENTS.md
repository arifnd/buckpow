# PowerDash — v0.1

Power monitoring dashboard built with Flask + SQLAlchemy + SQLite. Receives power readings from ESP32+INA219 via HTTP POST. Serves a Bootstrap 5 dashboard with Chart.js real-time charts.

## Repository structure

| Path | Purpose |
|---|---|
| `run.py` | Flask entrypoint |
| `app/` | Python package: config, models, services, API, dashboard |
| `app/config.py` | Config classes (Config, DevConfig) |
| `app/models/` | SQLAlchemy models (Device, Session, Measurement) |
| `app/services/` | Business logic layer |
| `app/api/` | REST API v1 blueprints (`/api/v1/*`) |
| `app/dashboard/` | Server-rendered page routes |
| `app/templates/` | Jinja2 templates (Bootstrap 5) |
| `app/static/` | CSS, JS (Chart.js frontend) |
| `instance/powerdash.db` | SQLite database (auto-created) |
| `migrations/` | Alembic migration files (Flask-Migrate) |
| `scripts/send_dummy.py` | Dummy data generator matching v0.1 API |
| `tests/` | Pytest suite (28 tests) |
| `.env` | Config via env vars |

## Quick start

```bash
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade           # create/update database schema
python run.py              # start on port 5001 (see .env)
```

**Or** (auto-creates tables on first run):

```bash
python run.py              # db.create_all() runs on startup
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/measurements` | Receive ESP32 data |
| GET | `/api/v1/measurements` | Paginated historical data |
| GET | `/api/v1/dashboard` | Latest + stats + devices |
| GET | `/api/v1/chart` | Chart data (device/session filter) |
| GET/POST | `/api/v1/devices` | List / create devices |
| GET/PUT/DELETE | `/api/v1/devices/<id>` | Device CRUD |
| GET/POST | `/api/v1/sessions` | List / create sessions |
| GET/PUT/DELETE | `/api/v1/sessions/<id>` | Session CRUD |
| POST | `/api/v1/sessions/<id>/start` | Start session |
| POST | `/api/v1/sessions/<id>/stop` | Stop session |

## Test with curl

```bash
curl -X POST http://localhost:5001/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"esp32-01","bus_voltage":5.12,"shunt_voltage":82,"current":241,"power":1234}'
```

## Key facts

- **Migration ready** — Flask-Migrate / Alembic configured for future PostgreSQL
- **Service layer** — business logic separated from HTTP handlers
- **Device auto-registration** — unknown device IDs create devices automatically
- **Session auto-assignment** — new measurements assigned to running session (if any)
- **Energy calculation** — cumulative Wh = Σ(Power(W) × sampling_interval(h))
- **Device status** — online if seen within 30s, else offline
- **Virtual env** at `venv/` — activate before Python commands

## Tests

```bash
python -m pytest tests/ -v
```

## Task management

See `tasks/index.md`. Move done tasks to `tasks/done/`.
