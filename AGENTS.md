# BuckPow — v0.1

Power monitoring dashboard built with Flask + SQLAlchemy + SQLite. Receives power readings from ESP32/ESP8266 + INA219 via HTTP POST. Serves a Tailwind CSS + HTMX dashboard with Chart.js real-time charts and dark theme.

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
| `app/templates/` | Jinja2 templates (Tailwind CSS, HTMX) |
| `app/static/` | CSS, JS (Chart.js, dashboard, theme) |
| `app/utils/` | Utility functions (calculations) |
| `instance/buckpow.db` | SQLite database (auto-created) |
| `migrations/` | Alembic migration files (Flask-Migrate) |
| `scripts/send_dummy.py` | Dummy data generator matching v0.1 API |
| `tests/` | Pytest suite (83 tests) |
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
| POST | `/api/v1/measurements` | Receive ESP32/ESP8266 data |
| GET | `/api/v1/measurements` | Paginated historical data (10/page) |
| GET | `/api/v1/measurements/export/csv` | Export filtered data as CSV |
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
- **HTMX navigation** — `hx-boost="true"` on `<body>` for SPA-like page transitions with native `<script>` re-evaluation
- **Tailwind CSS** — Utility-first styling with dark theme via CSS variables
- **Flowbite Datepicker** — Used on measurements filter page for date range selection
- **Device auto-registration** — unknown device IDs create devices automatically
- **Session auto-assignment** — new measurements assigned to running session (if any)
- **Energy calculation** — cumulative Wh = Σ(Power(W) × sampling_interval(h))
- **Device status** — dynamically computed: online if seen within 30s, else offline
- **Pagination** — All tables (devices, sessions, measurements) show 10 items/page with page nav; hidden when only 1 page
- **Virtual env** at `venv/` — activate before Python commands

## Tests

```bash
python -m pytest tests/ -v
```

# Task Management

`tasks/index.md` is the single source of truth for all tasks. Do not read files in `tasks/done/`.

When creating a new task plan (when user says "plan only" or asks to save a plan):

1. **Ensure directory exists** — Create `tasks/` if it doesn't exist:
   ```bash
   mkdir -p tasks
   ```
2. **Determine next task ID** — Read `tasks/index.md` to find the highest existing task number. The next task ID is that number + 1.
3. **APPEND to `tasks/index.md`** — **DO NOT overwrite**. Only append a new line:
   ```
   - [ ] {id}. {title} (see [task-{id}.md](task-{id}.md))
   ```
4. **Create detail file** `tasks/task-{id}.md` with this format:
   ```
   # Task {id}: {title}

   ## Files
   - `path/to/file.php` (lines X-Y)
   - ...

   ## Description
   ...

   ## Steps
   1. ...
   2. ...

   ## Expected Outcome
   ...
   ```
5. When task is executed and done:
   - Move `tasks/task-{id}.md` → `tasks/done/task-{id}.md`
   - Update `tasks/index.md`: change `[ ]` to `[x]` and update link to `done/task-{id}.md`
