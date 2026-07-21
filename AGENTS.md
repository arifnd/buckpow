# BuckPow

Power monitoring dashboard built with FastAPI + SQLAlchemy + SQLite. Receives power readings from ESP32/ESP8266 + INA219 via HTTP POST. Serves a Tailwind CSS + HTMX dashboard with Chart.js real-time charts and dark theme.

## Compatibility Matrix

Pin to these versions or newer. Examples in this file assume them.

| Dependency       | Minimum   | Notes                                                |
|------------------|-----------|------------------------------------------------------|
| Python           | 3.12      | Required for `StrEnum` and `X \| Y` union syntax     |
| FastAPI          | 0.115     | `Annotated[T, Depends(...)]` is the idiomatic form   |
| Pydantic         | 2.7       | v1 APIs (`json_encoders`, `.dict()`) are removed     |
| pydantic-settings| 2.4       | Lives in a separate package since Pydantic v2        |
| SQLAlchemy       | 2.0       | Uses sync `Session` (not async) — see note below     |
| Alembic          | 1.13      | Migrations for PostgreSQL                            |
| httpx            | 0.27      | Use `ASGITransport` for in-process tests             |
| PyJWT            | 2.9       | Use this, not the unmaintained `python-jose`         |
| ruff             | 0.6       | Replaces black, isort, autoflake                     |

> **Async note**: This project uses SQLAlchemy 2.0 sync API (`Session`, `SessionLocal`).
> Routes are `def` (sync, threadpool) unless they await HTMX template rendering.
> Do NOT switch to `AsyncSession` without project lead approval — the entire service
> layer and all dependencies assume sync sessions.

## Repository structure

| Path | Purpose |
|---|---|---|
| `src/main.py` | FastAPI entrypoint (`fastapi run src/main.py`) |
| `src/__init__.py` | FastAPI app factory, lifespan, exception handlers |
| `src/config.py` | Settings via `pydantic-settings` BaseSettings |
| `src/database.py` | SQLAlchemy engine, SessionLocal, Base, `get_db` dependency |
| `src/router.py` | API router aggregator + health endpoint |
| `src/dependencies.py` | Canonical re-export of all FastAPI dependencies |
| `src/template_helpers.py` | Jinja2 rendering helpers |
| `src/auth/` | Auth domain (models, schemas, router, service, JWT deps) |
| `src/devices/` | Device domain (models, schemas, router, service) |
| `src/sessions/` | Session domain (models, schemas, router, service) |
| `src/measurements/` | Measurement domain (models, schemas, router, service) |
| `src/projects/` | Project domain (models, schemas, router, service) |
| `src/alerts/` | Alert domain (models, schemas, router, service) |
| `src/audit/` | Audit log domain (models, schemas, router, service) |
| `src/benchmark/` | Benchmark domain (models, schemas, router, service) |
| `src/settings/` | Settings domain (schemas, router, service) |
| `src/dashboard/` | Dashboard (page routes per domain, API endpoints, service) |
| `src/middleware/` | ASGI middleware (rate limiter) |
| `src/utils/` | Utility functions (calculations, errors, validators, hash, pagination, query) |
| `templates/` | Jinja2 templates (Tailwind CSS, HTMX) |
| `templates/_partials/` | Reusable template fragments (confirm modal, etc.) |
| `src/static/` | CSS, JS (format, Chart.js, dashboard, theme) |
| `instance/buckpow.db` | SQLite database (auto-created) |
| `migrations/` | Alembic migration files (Flask-Migrate) |
| `scripts/send_dummy.py` | Dummy data generator |
| `firmware/` | Arduino sketches for ESP32/ESP8266 + INA219 |
| `requirements/base.txt` | Core dependencies |
| `requirements/dev.txt` | Dev/test dependencies |
| `requirements/prod.txt` | Production dependencies |
| `tests/` | Pytest suite (696+ tests, organized by domain) |
| `.env` | Config via env vars |
| `Dockerfile` | `CMD ["fastapi", "run", "src/main.py", "--port", "8000", "--proxy-headers"]` |
| `docker-compose.yml` | PostgreSQL + Nginx production stack |

## Quick start

```bash
source venv/bin/activate
pip install -r requirements/dev.txt
fastapi run src/main.py
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
- **Schemas** — Pydantic request/response models in `src/{domain}/schemas.py`, imported by API route files
- **Dependencies** — canonical import point in `src/dependencies.py` (re-exports from `src/auth` and `src/database`)
- **Pagination** — `PaginatedResult` dataclass in `src/utils/pagination.py` used by all services
- **Middleware** — ASGI middleware in `src/middleware/` (rate limiter with sliding window)
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

## Dependencies

### Use Annotated, not default-arg `Depends(...)`

`Annotated[T, Depends(...)]` is the idiomatic form since FastAPI 0.95.

```python
from typing import Annotated
from fastapi import Depends
from src.dependencies import get_db
from sqlalchemy.orm import Session

DbDep = Annotated[Session, Depends(get_db)]

@router.get("/devices")
def list_devices(db: DbDep) -> list[DeviceResponse]: ...
```

### Chain dependencies for reuse

```python
from uuid import UUID
from typing import Annotated
from fastapi import Depends
from src.dependencies import get_db
from src.devices.service import DeviceService

def valid_device(device_id: UUID, db: Annotated[Session, Depends(get_db)]) -> Device:
    device = DeviceService(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

def valid_owned_device(
    device: Annotated[Device, Depends(valid_device)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Device:
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your device")
    return device
```

### Rules
- Dependencies are **cached per request**. Same `Depends(x)` called 5 times → `x` runs once.
- Prefer `async def` dependencies for I/O (DB queries). Sync deps run in threadpool.
- Use **the same path-variable name** across endpoints when sharing a dependency.

## Routes — sync vs async

This project uses sync SQLAlchemy — follow these rules:

| Route does this                        | Use         |
|----------------------------------------|-------------|
| DB-only I/O (sync SQLAlchemy)          | `def` (sync, threadpool) |
| Sync DB + HTMX template rendering      | `async def` + `await` templates |
| Sync DB + `BackgroundTasks`            | `def` |
| Pure API endpoint (no templates)       | `def` |

```python
# DO — sync route for API endpoint with DB access
@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(db: DbDep) -> list[DeviceResponse]:
    return DeviceService(db).get_all()

# DO — async route for dashboard with template rendering
@router.get("/")
async def dashboard(request: Request, db: DbDep):
    data = DashboardService(db).get_summary()          # sync DB call
    return templates.TemplateResponse("dashboard.html", {"request": request, **data})

# DON'T — async route with sync DB call that has no await
@router.get("/bad")
async def bad(db: DbDep):
    return DeviceService(db).get_all()    # no await, just overhead
```

## Pydantic

### Use built-in validators

```python
from enum import StrEnum
from pydantic import BaseModel, Field


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    level: AlertLevel
    message: str = Field(min_length=1, max_length=512)
```

> **Don't** write `Field(ge=18, default=None)`. Constraint and default contradict.
> Decide: required (`Field(ge=18)`) or optional (`int | None = Field(default=None, ge=18)`).

### Custom base model — modern serialization

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, field_serializer


class AppBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def _serialize_datetimes(self, value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))
            return value.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value
```

## Authentication — JWT

Use **`PyJWT`**, not `python-jose` (unmaintained).

```python
import jwt  # PyJWT
from jwt.exceptions import InvalidTokenError

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
```

## Database — SQLAlchemy 2.0 sync

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Naming conventions
- `lower_case_snake`
- Singular tables: `user`, `device`, `session`, `measurement`, `alert`, `project`
- `_at` suffix for `datetime`, `_date` suffix for `date`
- Use the same FK column name everywhere it appears

## Background work — BackgroundTasks

```python
from fastapi import BackgroundTasks

@router.post("/alerts")
def create_alert(payload: AlertCreate, db: DbDep, bg: BackgroundTasks):
    alert = AlertService.create(db, payload)
    bg.add_task(notify_users, alert)   # fire-and-forget, in-process
    return alert
```

> BackgroundTasks run **after the response is sent**. No retry. Don't use for
> anything you'd page on.

## Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_device(client: AsyncClient):
    resp = await client.post("/api/v1/devices", json={"name": "esp-01"})
    assert resp.status_code == 201
```

> **Don't** use `async_asgi_testclient`. Use httpx + `ASGITransport`.

### Override dependencies in tests

```python
from src.auth.dependencies import get_current_user
from src.main import app


def fake_user():
    return User(id=1, email="test@example.com")


@pytest.fixture(autouse=True)
def _override_auth():
    app.dependency_overrides[get_current_user] = fake_user
    yield
    app.dependency_overrides.clear()
```

## Linting

```shell
ruff check --fix src
ruff format src
```

## Migrations (Alembic)

- Migrations must be static and reversible.
- Descriptive filenames — use `file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s`

## API documentation

Hide docs outside dev/staging:

```python
from src.config import settings

SHOW_DOCS_IN = {"development", "staging"}
app_kwargs = {"title": "BuckPow"}
if settings.APP_ENV not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)
```

## Anti-patterns — common AI-agent mistakes

Check diffs for these. Each is a real failure mode from production code.

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| `requests.get(...)` inside `async def` | Blocks the event loop. `requests` is sync. | Use `httpx.AsyncClient` or `await run_in_threadpool(requests.get, ...)`. |
| `time.sleep` / `open()` / sync DB driver inside `async def` | Blocks the loop. | Use the async equivalent or keep route `def`. |
| `from jose import jwt` | `python-jose` is unmaintained. | `import jwt` (PyJWT). |
| `from async_asgi_testclient import TestClient` | Unmaintained. | `httpx.AsyncClient` + `ASGITransport`. |
| `model_config = ConfigDict(json_encoders={...})` | Deprecated in Pydantic v2. | `@field_serializer` or `Annotated[T, PlainSerializer(...)]`. |
| `Field(ge=18, default=None)` | Constraint contradicts the default. | Pick required or optional, not both. |
| `def get_user(id: int = Depends(...))` (default-arg form) | Legacy; gotchas with default values. | `user: Annotated[User, Depends(...)]`. |
| Catching bare `Exception` around a route body | Hides bugs, turns 500s into silent 200s. | Catch specific exception; raise `HTTPException`. |
| `BackgroundTasks` for anything you'd page on | No retry, dies with the worker. | Use Celery / Arq / RQ. |
| Returning a Pydantic model *and* setting `response_model=` to same class | Model constructed twice (validate + serialize). | Return a dict/ORM row and let `response_model` validate, or drop `response_model`. |
| Importing across domains via deep paths (`from src.services.user.user_service import ...`) | Tight coupling, hard to refactor. | `from src.services import user_service`. |
| Reusing one `BaseSettings` for the whole app | Hard to reason about. | One `BaseSettings` per domain. |
| Mocking the database in integration tests | Mock/prod divergence. | Use a real DB (testcontainers, ephemeral schema) and `dependency_overrides` for auth. |
| Switching to `AsyncSession` without project lead approval | Entire service layer assumes sync `Session`. | Keep sync unless approved. |

## Tests

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
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
