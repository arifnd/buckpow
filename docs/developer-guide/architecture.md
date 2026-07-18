# Architecture

System architecture and design of BuckPow.

---

## Overview

BuckPow follows a layered architecture with clear separation of concerns:

- **API Layer** — FastAPI routers handle HTTP requests
- **Service Layer** — Business logic and data processing
- **Model Layer** — SQLAlchemy ORM models
- **Database Layer** — SQLite, PostgreSQL, or MySQL

<!-- TODO: Replace with architecture diagram -->

## High-Level Architecture

```mermaid
graph TB
    subgraph Client
        ESP[ESP32/ESP8266]
        Browser[Web Browser]
    end

    subgraph BuckPow["BuckPow Server"]
        API[FastAPI Application]
        Services[Service Layer]
        Models[SQLAlchemy Models]
        DB[(Database)]
    end

    subgraph Frontend
        HTMX[HTMX]
        Tailwind[Tailwind CSS]
        ChartJS[Chart.js]
    end

    ESP -->|HTTP POST| API
    Browser -->|HTTP GET/POST| API
    API --> Services
    Services --> Models
    Models --> DB
    Browser --> HTMX
    Browser --> Tailwind
    Browser --> ChartJS
```

## Directory Structure

```
buckpow/
├── app/
│   ├── __init__.py          # App factory, lifespan, middleware
│   ├── main.py              # Entrypoint
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine, session
│   ├── auth.py              # JWT creation/verification
│   ├── dependencies.py      # FastAPI dependencies
│   ├── api/                 # API routers
│   │   ├── __init__.py      # Router aggregation
│   │   ├── measurements.py  # /measurements, /chart
│   │   ├── devices.py       # /devices CRUD
│   │   ├── sessions.py      # /sessions CRUD + start/stop
│   │   ├── dashboard.py     # /dashboard endpoints
│   │   ├── alerts.py        # /alerts CRUD
│   │   ├── projects.py      # /projects CRUD
│   │   ├── auth.py          # /auth login/logout
│   │   ├── benchmark.py     # /benchmark/compare
│   │   ├── settings.py      # /settings
│   │   ├── audit.py         # /audit/logs
│   │   └── health.py        # /health
│   ├── dashboard/           # Server-rendered pages
│   │   └── routes.py        # Page routes (Jinja2)
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── device.py
│   │   ├── session.py
│   │   ├── measurement.py
│   │   ├── alert.py
│   │   ├── project.py
│   │   └── audit_log.py
│   ├── services/            # Business logic
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   ├── session_service.py
│   │   ├── measurement_service.py
│   │   ├── alert_service.py
│   │   ├── project_service.py
│   │   ├── dashboard_service.py
│   │   └── audit_service.py
│   ├── schemas/             # Pydantic request/response
│   ├── utils/               # Utility functions
│   ├── middleware/           # ASGI middleware
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS
├── firmware/                # Arduino sketches
├── migrations/              # Alembic migrations
├── tests/                   # Pytest suite
├── scripts/                 # Utility scripts
├── mkdocs.yml               # Documentation config
├── docs/                    # Documentation source
├── Dockerfile               # Container build
├── docker-compose.yml       # Production stack
├── alembic.ini              # Migration config
├── requirements.txt         # Dependencies
└── .env.example             # Environment template
```

## Request Flow

### API Request

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Auth
    participant Service
    participant Model
    participant DB

    Client->>Router: HTTP Request
    Router->>Auth: Verify JWT / API Key
    Auth-->>Router: User / Device
    Router->>Service: Business Logic
    Service->>Model: Query / Update
    Model->>DB: SQL Query
    DB-->>Model: Result
    Model-->>Service: Object
    Service-->>Router: Response Data
    Router-->>Client: JSON Response
```

### Dashboard Request

```mermaid
sequenceDiagram
    participant Browser
    participant Router
    participant Auth
    participant Template
    participant Static

    Browser->>Router: HTTP GET
    Router->>Auth: Verify JWT Cookie
    Auth-->>Router: User
    Router->>Template: Render Jinja2
    Template-->>Browser: HTML
    Browser->>Static: Fetch CSS/JS
    Static-->>Browser: Assets
    Browser->>Browser: HTMX init
    Browser->>Router: API Polling (5s)
    Router-->>Browser: JSON Data
    Browser->>Browser: Update Charts
```

## Models

### Entity Relationship

```mermaid
erDiagram
    User ||--o{ Project : owns
    Project ||--o{ Device : contains
    Project ||--o{ Session : contains
    Device ||--o{ Session : has
    Device ||--o{ Measurement : produces
    Device ||--o{ Alert : triggers
    Session ||--o{ Measurement : contains

    User {
        int id PK
        string name
        string email UK
        string password
        json settings
        datetime created_at
    }

    Project {
        int id PK
        string name
        text description
        int owner_id FK
        datetime created_at
        datetime updated_at
    }

    Device {
        int id PK
        string device_id UK
        string alias
        text description
        int sampling_interval
        datetime last_seen
        string status
        boolean enabled
        string firmware_version
        string api_key UK
        int project_id FK
        float high_current_threshold
        float high_power_threshold
        float low_voltage_threshold
        datetime created_at
        datetime updated_at
    }

    Session {
        int id PK
        int device_id FK
        string name
        string target_device
        text description
        string status
        int project_id FK
        datetime started_at
        datetime ended_at
        datetime created_at
        datetime updated_at
    }

    Measurement {
        int id PK
        int session_id FK
        int device_id FK
        float bus_voltage
        float shunt_voltage
        float load_voltage
        float current
        float power
        float energy
        datetime created_at
    }

    Alert {
        int id PK
        int device_id FK
        string level
        string message
        datetime created_at
        datetime resolved_at
    }
```

### Key Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| User → Project | One-to-Many | User owns projects |
| Project → Device | One-to-Many | Project contains devices |
| Project → Session | One-to-Many | Project contains sessions |
| Device → Session | One-to-Many | Device has many sessions |
| Device → Measurement | One-to-Many | Device produces measurements |
| Device → Alert | One-to-Many | Device triggers alerts |
| Session → Measurement | One-to-Many | Session contains measurements |

## Service Layer

Services encapsulate business logic and are separated from HTTP handlers:

| Service | Responsibility |
|---------|---------------|
| `UserService` | User CRUD, password hashing |
| `DeviceService` | Device CRUD, API key management, online status |
| `SessionService` | Session lifecycle (create, start, stop) |
| `MeasurementService` | Measurement creation, chart data, statistics |
| `AlertService` | Alert creation, threshold checking, resolution |
| `ProjectService` | Project CRUD |
| `DashboardService` | Dashboard aggregates, summary stats |
| `AuditService` | Audit log creation |

### Service Pattern

All services follow the same pattern:

```python
class DeviceService:
    @staticmethod
    def get_all(db: Session):
        return db.query(Device).all()

    @staticmethod
    def get_by_id(db: Session, device_id):
        return db.get(Device, device_id)

    @staticmethod
    def create(db: Session, **kwargs):
        device = Device(**kwargs)
        db.add(device)
        db.commit()
        return device

    @staticmethod
    def update(db: Session, device_id, **kwargs):
        device = db.get(Device, device_id)
        for key, value in kwargs.items():
            setattr(device, key, value)
        db.commit()
        return device
```

## Authentication

### JWT User Authentication

- **Token**: HS256 JWT with `sub` (user ID) and `exp` (expiry)
- **Transport**: Bearer header or httponly cookie
- **Expiry**: 7 days (configurable)
- **Dependencies**: `get_current_user`, `require_user`

### Device API Key Authentication

- **Key**: 64-character hex string
- **Transport**: Bearer header
- **Lookup**: Match key to device in database
- **Dependency**: `get_api_key_device`

### Rate Limiting

| Endpoint | Method | Limit | Window |
|----------|--------|-------|--------|
| `/api/v1/auth/login` | POST | 5 | 60s |
| `/api/v1/measurements` | POST | 60 | 60s |
| `/api/v1/measurements/export/csv` | GET | 10 | 60s |
| `/api/v1/measurements/export/xlsx` | GET | 10 | 60s |

## Frontend Architecture

### Server-Rendered Pages

- **Engine**: Jinja2 templates
- **Navigation**: HTMX `hx-boost` for SPA-like transitions
- **Styling**: Tailwind CSS with dark mode
- **Charts**: Chart.js with real-time updates

### HTMX Pattern

```html
<body hx-boost="true">
  <!-- Navigation links load pages without full refresh -->
  <a href="/devices">Devices</a>

  <!-- API calls update specific elements -->
  <div hx-get="/api/v1/dashboard" hx-trigger="every 5s">
    <!-- Dashboard content -->
  </div>
</body>
```

### JavaScript Modules

| File | Purpose |
|------|---------|
| `format.js` | Unit formatting (`fmtCurrent`, `fmtPower`, `fmtEnergy`) |
| `dashboard.js` | Dashboard polling, charts, session selector |
| `benchmark.js` | Benchmark comparison, overlay chart |
| `charts.js` | Chart.js factory and options |
| `theme.js` | Dark/light/system theme toggle |
| `timestamp.js` | Timezone-aware timestamp formatting |

## Database

### Supported Backends

| Backend | Connection String | Use Case |
|---------|-------------------|----------|
| SQLite | `sqlite:///instance/buckpow.db` | Development, single-user |
| PostgreSQL | `postgresql://user:pass@host:5432/db` | Production, multi-user |
| MySQL | `mysql+pymysql://user:pass@host:3306/db` | Production alternative |

### Migrations

BuckPow uses Alembic for database migrations:

```bash
# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### SQLite Auto-Setup

For SQLite, tables are created automatically on first run:

```python
if 'sqlite' in settings.DATABASE_URL:
    Base.metadata.create_all(bind=engine)
    command.stamp(alembic_cfg, 'head')
```

## Error Handling

### Exception Handlers

| Handler | Status Code | Description |
|---------|-------------|-------------|
| `global_exception_handler` | 500 | Catches all unhandled exceptions |
| `http_exception_handler` | Various | FastAPI HTTPException |
| `not_found_handler` | 404 | Route not found |
| `method_not_allowed_handler` | 405 | Method not allowed |

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Middleware Stack

```mermaid
graph LR
    Request --> CORS[CORS Middleware]
    CORS --> RateLimit[Rate Limiter]
    RateLimit --> Router[FastAPI Router]
```

| Middleware | Purpose |
|-----------|---------|
| `CORSMiddleware` | Cross-origin resource sharing |
| `RateLimiterMiddleware` | Sliding window rate limiting |

## Deployment

### Docker Compose Stack

```mermaid
graph TB
    subgraph Docker
        Nginx[Nginx :80]
        App[BuckPow :8000]
        DB[PostgreSQL :5432]
    end

    Nginx --> App
    App --> DB
```

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `nginx` | `nginx:alpine` | 80 | Reverse proxy, static files |
| `app` | Custom build | 8000 | BuckPow application |
| `db` | `postgres:16-alpine` | 5432 | Database |

### Scaling Considerations

- **Horizontal**: Run multiple `app` instances behind Nginx
- **Database**: PostgreSQL supports concurrent connections
- **SQLite**: Single-writer limitation — not suitable for production scaling

## Security

### Authentication

- JWT tokens with configurable expiry
- API keys for device authentication
- Password hashing with bcrypt

### Authorization

- Owner-based access control for devices and projects
- Project ownership checks on mutations
- Rate limiting on sensitive endpoints

### Data Protection

- Secrets not logged or exposed in responses
- API keys masked in API responses (first 6 + `****` + last 4)
- CORS configured for same-origin in production

## Performance

### Optimizations

- **Connection pooling**: SQLAlchemy `pool_pre_ping`
- **Lazy loading**: Dynamic relationships on models
- **Pagination**: All list endpoints support pagination
- **Indexing**: Indexed columns on frequently queried fields

### Database Indexes

| Table | Index | Columns |
|-------|-------|---------|
| `devices` | `device_id` | Unique |
| `devices` | `api_key` | Unique |
| `measurements` | `device_created` | `(device_id, created_at)` |
| `measurements` | `session_created` | `(session_id, created_at)` |
| `alerts` | `device_id` | Standard |
| `audit_logs` | `created_at` | Standard |
| `audit_logs` | `action` | Standard |
