# BuckPow

ESP32/ESP8266 power meter dashboard.

**Tech stack:** [FastAPI](https://fastapi.tiangolo.com/) · [SQLAlchemy](https://www.sqlalchemy.org/) · [SQLite](https://www.sqlite.org/) · [Tailwind CSS](https://tailwindcss.com/) · [HTMX](https://htmx.org/) · [Chart.js](https://www.chartjs.org/)

## Features

- **Real-time power monitoring** — live voltage, current, power & energy dashboard
- **Device auto-registration** — new ESP32/ESP8266 devices register on first reading
- **Session management** — start/stop recording sessions with automatic energy accumulation (Wh)
- **Device API keys** — per-device authentication with key generation & rotation
- **Alerting engine** — configurable thresholds for high power, high current, low voltage
- **Benchmarking** — compare sessions side-by-side with statistical summaries
- **Projects** — organize devices and sessions into projects
- **Data export** — CSV and XLSX export with date range filtering
- **Dark theme** — system/light/dark mode with user preference persistence
- **Pagination** — all list views paginated at 10 items/page
- **Docker ready** — PostgreSQL + Nginx production stack via docker-compose

```mermaid
graph LR
    S["ESP32/ESP8266<br/>(INA219)"] -->|HTTP POST| API["FastAPI"]
    API --> DB["SQLite"]
    API --> DASH["HTML Dashboard<br/>(HTMX, Chart.js)"]
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
fastapi run app/main.py
```

Tables auto-create on first run (SQLite only). Default admin: `admin@example.com` / `password`.

Open http://localhost:5001. (Port 5000 is often taken by macOS AirPlay — `.env` defaults to 5001.)

## Database migrations

**SQLite (dev)** — tables auto-create on startup. No migration commands needed.

**PostgreSQL (production)** — use Alembic to apply the initial migration before running the app:

```bash
alembic upgrade head
fastapi run app/main.py
```

The `migrations/` directory contains the Alembic configuration. To create a new migration after model changes:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## API

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/measurements` | Send a reading |
| GET | `/api/v1/measurements` | Paginated readings (10/page) |
| GET | `/api/v1/measurements/export/csv` | Export filtered readings as CSV |
| GET | `/api/v1/measurements/export/xlsx` | Export filtered readings as Excel |
| GET | `/api/v1/dashboard` | Latest + stats + devices |
| GET | `/api/v1/dashboard/summary` | Online/offline count, active sessions, today energy |
| GET | `/api/v1/dashboard/statistics` | Full stats with energy breakdown |
| GET | `/api/v1/chart` | Chart data (device/session filter, granularity) |
| GET/POST | `/api/v1/devices` | List / create devices |
| GET/PUT/DELETE | `/api/v1/devices/<id>` | Device CRUD |
| POST | `/api/v1/devices/<id>/regenerate-key` | Generate new API key |
| GET/POST | `/api/v1/sessions` | List / create sessions |
| GET/PUT/DELETE | `/api/v1/sessions/<id>` | Session CRUD |
| POST | `/api/v1/sessions/<id>/start` | Start session |
| POST | `/api/v1/sessions/<id>/stop` | Stop session |
| GET/POST | `/api/v1/projects` | List / create projects |
| GET/PUT/DELETE | `/api/v1/projects/<id>` | Project CRUD |
| GET | `/api/v1/alerts` | List alerts (filterable by device, level, resolved) |
| POST | `/api/v1/alerts/resolve-all` | Resolve all unresolved alerts |
| GET | `/api/v1/benchmark/compare` | Compare 2+ sessions |
| POST | `/api/v1/auth/login` | Email/password login |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Current user info |
| PUT | `/api/v1/auth/profile` | Update profile (name, email, password) |
| GET | `/api/v1/settings` | Get user settings |
| PUT | `/api/v1/settings` | Update user settings |
| GET | `/api/v1/health` | Health check |

### Send a reading

```bash
curl -X POST http://localhost:5001/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <api_key>' \
  -d '{"device_id":"esp32-01","bus_voltage":5.12,"shunt_voltage":82,"current":241,"power":1234}'
```

> **Note:** API key is optional when authentication is disabled (dev mode). Get the key from the device detail page or via `GET /api/v1/devices/<id>/key`.

## Pages

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

## Test

```bash
python -m pytest tests/ -v
```

## Send dummy data

```bash
python scripts/send_dummy.py --interval 1                               # without API key
python scripts/send_dummy.py --interval 1 --api-key <your_api_key>      # with authentication
```

## Config

`.env` supports `APP_HOST`, `APP_PORT` (default: 5001), `SECRET_KEY`, `DATABASE_URL`, `DEVICE_ONLINE_TIMEOUT`.

## License

MIT
