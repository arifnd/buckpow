# BuckPow

Power monitoring dashboard built with FastAPI + SQLAlchemy + SQLite. Receives power readings from ESP32/ESP8266 + INA219 via HTTP POST. Serves a Tailwind CSS + HTMX dashboard with Chart.js real-time charts and dark theme.

## Repository structure

| Path | Purpose |
|---|---|
| `app/main.py` | FastAPI entrypoint (`fastapi run app/main.py`) |
| `app/__init__.py` | FastAPI app factory, lifespan, exception handlers, router mounting |
| `app/config.py` | Settings via `pydantic-settings` BaseSettings |
| `app/database.py` | SQLAlchemy engine, SessionLocal, Base, `get_db` dependency |
| `app/auth.py` | JWT creation/verification, `get_current_user`, `get_api_key_device` deps |
| `app/dependencies.py` | Canonical re-export of all FastAPI dependencies (`get_db`, `require_user`, etc.) |
| `app/schemas/` | Pydantic request/response models (Measurement, Session, Device, Alert, Project, Auth, Settings) |
| `app/models/` | SQLAlchemy models (User, Device, Session, Measurement, Alert, Project) |
| `app/services/` | Business logic layer (User, Device, Session, Measurement, Alert, Project, Dashboard) |
| `app/middleware/` | ASGI middleware (rate limiter) |
| `app/api/` | FastAPI APIRouters (`/api/v1/*`) |
| `app/dashboard/` | Server-rendered page routes (Jinja2) |
| `app/templates/` | Jinja2 templates (Tailwind CSS, HTMX) |
| `app/templates/_partials/` | Reusable template fragments (confirm modal, etc.) |
| `app/static/` | CSS, JS (Chart.js, dashboard, theme) |
| `app/utils/` | Utility functions (calculations, errors, validators, hash, pagination) |
| `instance/buckpow.db` | SQLite database (auto-created) |
| `migrations/` | Alembic migration files (Flask-Migrate) |
| `scripts/send_dummy.py` | Dummy data generator |
| `firmware/` | Arduino sketches for ESP32/ESP8266 + INA219 |
| `tests/` | Pytest suite (607 tests) |
| `.env` | Config via env vars |
| `Dockerfile` | `CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--proxy-headers"]` |
| `docker-compose.yml` | PostgreSQL + Nginx production stack |

## Quick start

```bash
source venv/bin/activate
pip install -r requirements.txt
fastapi run app/main.py
```

Tables auto-create on first run. Default admin: `admin@example.com` / `password`.

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/measurements` | Receive ESP32/ESP8266 data (Bearer token auth) |
| GET | `/api/v1/measurements` | Paginated historical data (10/page) |
| GET | `/api/v1/measurements/export/csv` | Export filtered data as CSV |
| GET | `/api/v1/measurements/export/xlsx` | Export filtered data as Excel |
| GET | `/api/v1/dashboard` | Latest + stats + devices |
| GET | `/api/v1/dashboard/summary` | Online/offline count, active sessions, today energy |
| GET | `/api/v1/dashboard/statistics` | Full stats with energy breakdown |
| GET | `/api/v1/chart` | Chart data (device/session filter, granularity) |
| GET/POST | `/api/v1/devices` | List / create devices |
| GET/PUT/DELETE | `/api/v1/devices/<id>` | Device CRUD |
| GET | `/api/v1/devices/<id>/key` | Get masked API key |
| PATCH | `/api/v1/devices/<id>/toggle` | Enable/disable device |
| POST | `/api/v1/devices/<id>/regenerate-key` | Generate new API key |
| GET/POST | `/api/v1/sessions` | List / create sessions |
| GET/PUT/DELETE | `/api/v1/sessions/<id>` | Session CRUD |
| POST | `/api/v1/sessions/<id>/start` | Start session |
| POST | `/api/v1/sessions/<id>/stop` | Stop session |
| GET/POST | `/api/v1/projects` | List / create projects |
| GET/PUT/DELETE | `/api/v1/projects/<id>` | Project CRUD |
| GET | `/api/v1/alerts` | List alerts (filterable by device, level, resolved) |
| POST | `/api/v1/alerts` | Create alert |
| PATCH | `/api/v1/alerts/<id>/resolve` | Resolve a single alert |
| POST | `/api/v1/alerts/resolve-all` | Resolve all unresolved alerts |
| GET | `/api/v1/benchmark/compare` | Compare 2+ sessions |
| POST | `/api/v1/auth/login` | Email/password login |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Current user info |
| PUT | `/api/v1/auth/profile` | Update profile (name, email, password) |
| GET | `/api/v1/settings` | Get user settings |
| PUT | `/api/v1/settings` | Update user settings |
| GET | `/api/v1/health` | Health check |

## Dashboard pages

| Path | Page |
|---|---|
| `/` | Dashboard with real-time charts & summary cards |
| `/devices` | Device management |
| `/devices/new` | Create device form |
| `/devices/<id>/edit` | Edit device form |
| `/sessions` | Session management |
| `/sessions/new` | Create session form |
| `/sessions/<id>/edit` | Edit session form |
| `/measurements` | Paginated readings with date range filter |
| `/projects` | Project management |
| `/benchmark` | Session comparison |
| `/alerts` | Alert management |
| `/settings` | User preferences (thresholds, brand) |
| `/profile` | Profile editing |
| `/auth/login` | Login page |

## Test with curl

```bash
# Without authentication (dev mode)
curl -X POST http://localhost:8000/api/v1/measurements \

  -d '{"device_id":"esp32-01","bus_voltage":5.12,"shunt_voltage":82,"current":241,"power":1234}'

# With API key
curl -X POST http://localhost:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <api_key>' \
  -d '{"device_id":"esp32-01","bus_voltage":5.12,"shunt_voltage":82,"current":241,"power":1234}'
```

## Key facts

- **Models** — User, Device (with API key & thresholds), Session (with energy), Measurement (with energy), Alert (levels: info/warning/critical), Project
- **Authentication** — JWT bearer token for API, JWT cookie-based for dashboard, Bearer token for device API
- **Service layer** — business logic separated from HTTP handlers (7 services), all accept `db: Session`
- **Schemas** — Pydantic request/response models in `app/schemas/`, imported by API route files
- **Dependencies** — canonical import point in `app/dependencies.py` (re-exports from `app.auth` and `app.database`)
- **Pagination** — `PaginatedResult` dataclass in `app/utils/pagination.py` used by all services
- **Middleware** — ASGI middleware in `app/middleware/` (rate limiter with sliding window)
- **Config** — `pydantic-settings` BaseSettings with env var loading and type validation
- **HTMX navigation** — `hx-boost="true"` on `<body>` for SPA-like page transitions with native `<script>` re-evaluation
- **Tailwind CSS** — Utility-first styling with dark theme via CSS variables
- **Flowbite Datepicker** — Used on measurements filter page for date range selection
- **Device auto-registration** — unknown device IDs create devices automatically
- **Session auto-assignment** — new measurements assigned to running session (if any)
- **Energy calculation** — cumulative Wh = Σ(Power(W) × sampling_interval(h))
- **Alert engine** — automatic alerts on high power/current/low voltage thresholds
- **Device status** — dynamically computed: online if seen within 30s, else offline
- **Pagination** — All tables show 10 items/page with page nav; hidden when only 1 page
- **Export** — CSV and XLSX with date range filtering
- **Docker** — PostgreSQL + Nginx production stack via docker-compose
- **Migration ready** — Flask-Migrate / Alembic configured for future PostgreSQL
- **Virtual env** at `venv/` — activate before Python commands
- **Passwords** — bcrypt via passlib; existing scrypt hashes migrated automatically

## Tests

```bash
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

## Send dummy data

```bash
python scripts/send_dummy.py --interval 1
python scripts/send_dummy.py --interval 1 --api-key <key>
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
