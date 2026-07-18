# Backend

FastAPI application structure, middleware, authentication, and service layer.

---

## Application Structure

```
app/
├── __init__.py              # App factory, lifespan, middleware, exception handlers
├── main.py                  # Entrypoint: `fastapi run app/main.py`
├── config.py                # Settings via pydantic-settings
├── database.py              # SQLAlchemy engine, SessionLocal, Base
├── auth.py                  # JWT creation/verification, dependency functions
├── dependencies.py          # Canonical re-export of all FastAPI dependencies
├── models/                  # SQLAlchemy ORM models (7 tables)
├── schemas/                 # Pydantic request/response models
├── services/                # Business logic layer (8 services)
├── api/                     # FastAPI APIRouters (11 modules)
├── dashboard/               # Server-rendered page routes (Jinja2)
├── middleware/               # ASGI middleware (rate limiter)
└── utils/                   # Utility functions
```

## Application Factory

The app is created in `app/__init__.py`:

```python
app = FastAPI(
    title='BuckPow',
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=None if settings.DISABLE_API_DOCS else '/docs',
    redoc_url=None if settings.DISABLE_API_DOCS else '/redoc',
    openapi_url=None if settings.DISABLE_API_DOCS else '/openapi.json',
)
```

### Lifespan

The `lifespan` context manager runs at startup:

1. **Logging** — Configures stdout logging
2. **Database** — Creates tables for SQLite, stamps Alembic revision
3. **Admin seed** — Creates default admin user if none exists

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    # ...
    yield
    # Shutdown
```

### Middleware Stack

Middleware is added in order (outermost first):

```python
# 1. Rate limiter (custom ASGI)
app.add_middleware(
    RateLimiterMiddleware,
    limits=[
        ('POST', '/api/v1/auth/login', 5, 60),
        ('POST', '/api/v1/measurements', 60, 60, bearer_token_key),
        ('GET', '/api/v1/measurements/export/csv', 10, 60),
        ('GET', '/api/v1/measurements/export/xlsx', 10, 60),
    ],
)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 3. Static files
app.mount('/static', StaticFiles(directory='app/static'), name='static')
```

### Router Mounting

```python
app.include_router(api_router, prefix='/api/v1')
app.include_router(dashboard_router)
```

## Configuration

Settings via `pydantic-settings` BaseSettings in `app/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | `buckpow-dev-key-change-in-production` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | Token TTL |
| `DATABASE_URL` | `sqlite:///instance/buckpow.db` | Database connection |
| `APP_HOST` | `0.0.0.0` | Server bind host |
| `APP_PORT` | `8000` | Server bind port |
| `ADMIN_EMAIL` | `""` | Default admin email |
| `ADMIN_PASSWORD` | `""` | Default admin password |
| `DEVICE_ONLINE_TIMEOUT` | `30` | Seconds before device is offline |
| `DEVICE_AUTH_ENABLED` | `True` | Require API key for device auth |
| `DISABLE_API_DOCS` | `False` | Disable `/docs` and `/redoc` |
| `APP_ENV` | `development` | Environment (dev/prod) |

### Environment Loading

```python
class Settings(BaseSettings):
    model_config = {'env_file': '.env', 'extra': 'ignore'}
```

Settings load from `.env` file and environment variables. The `DEBUG` flag is derived from `APP_ENV`.

## Database Layer

### Engine & Session

```python
# app/database.py
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Dependency Injection

FastAPI uses `Depends(get_db)` for automatic session management:

```python
@router.get('/devices')
def list_devices(db: Session = Depends(get_db)):
    devices = DeviceService.get_all(db)
    return devices
```

### SQLite Auto-Creation

For SQLite, the database directory is created automatically:

```python
db_path = settings.DATABASE_URL.removeprefix("sqlite:///")
if db_path != settings.DATABASE_URL:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
```

## Authentication

### JWT Tokens

Tokens are created with `PyJWT`:

```python
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### Dependency Functions

Three authentication dependencies in `app/auth.py`:

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_current_user` | Optional auth (cookie or Bearer) | `User \| None` |
| `require_user` | Required auth (raises 401) | `User` |
| `get_api_key_device` | Device API key auth | `Device \| None` |

### Dashboard Auth (Cookie)

Dashboard routes use cookie-based JWT:

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    request: Request = None,
    db: Session = Depends(get_db),
) -> User | None:
    token = credentials.credentials if credentials else None
    if token is None and request is not None:
        token = request.cookies.get('access_token')
    return _decode_user(token, db)
```

### Device Auth (Bearer)

Device API uses Bearer token with API key:

```python
def get_api_key_device(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if not settings.DEVICE_AUTH_ENABLED:
        return None
    api_key = credentials.credentials
    device = DeviceService.get_by_api_key(db, api_key)
    if not device:
        raise HTTPException(status_code=401, detail='Invalid API key')
    return device
```

### Re-exported Dependencies

`app/dependencies.py` re-exports all dependencies for clean imports:

```python
from app.dependencies import get_db, require_user, get_current_user, get_api_key_device
```

## Middleware

### Rate Limiter

Custom ASGI middleware with sliding window:

```python
class RateLimiterMiddleware:
    def __init__(self, app, limits=None):
        self.limits = limits or []
        self.requests = defaultdict(list)

    async def __call__(self, scope, receive, send):
        # Extract client identity
        # Check rate limit
        # Return 429 if exceeded
```

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /api/v1/auth/login` | 5 requests | 60s |
| `POST /api/v1/measurements` | 60 requests | 60s (per API key) |
| `GET /api/v1/measurements/export/csv` | 10 requests | 60s |
| `GET /api/v1/measurements/export/xlsx` | 10 requests | 60s |

### Key Function

Device rate limiting uses the Bearer token as identity:

```python
def bearer_token_key(scope):
    for name, value in scope.get('headers', []):
        if name == b'authorization':
            auth = value.decode()
            if auth.startswith('Bearer '):
                return auth[7:]
    return None
```

## Service Layer

All business logic lives in `app/services/`. Services accept `db: Session` and return domain objects.

### Service Classes

| Service | Purpose |
|---------|---------|
| `UserService` | User CRUD, password hashing |
| `DeviceService` | Device CRUD, API key management |
| `SessionService` | Session lifecycle, start/stop |
| `MeasurementService` | Measurement creation, energy calculation |
| `AlertService` | Alert generation, threshold checking |
| `DashboardService` | Dashboard stats, summary data |
| `ProjectService` | Project CRUD |
| `AuditService` | Audit log queries |

### Service Pattern

```python
class AlertService:
    @staticmethod
    def create(db: Session, device_id, level, message):
        alert = Alert(device_id=device_id, level=level, message=message)
        db.add(alert)
        db.commit()
        return alert

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10, **filters):
        q = db.query(Alert)
        # Apply filters
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        return PaginatedResult(items=items, ...)
```

## Exception Handling

### Custom Exceptions

Defined in `app/utils/errors.py`:

```python
class AppError(Exception):
    def __init__(self, message, status_code=400, code=None):
        self.message = message
        self.status_code = status_code
        self.code = code

class ValidationError(AppError): ...  # 400
class NotFoundError(AppError): ...    # 404
class AuthError(AppError): ...        # 401
```

### Global Handlers

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': exc.message, 'code': exc.code},
        )
    return JSONResponse(status_code=500, content={'error': 'Internal server error'})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={'error': exc.detail})
```

## Dashboard Routes

Server-rendered pages in `app/dashboard/routes.py`:

### Route Pattern

```python
@dashboard_router.get('/devices')
def devices_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(
        _render('devices/index.html', current_user=current_user, active_page='devices')
    )
```

### Jinja2 Environment

```python
templates = Environment(loader=FileSystemLoader('app/templates'), autoescape=True)
templates.globals['url_for'] = _url_for
templates.globals['app_version'] = APP_VERSION
```

### Anonymous User

A sentinel object is used for unauthenticated template rendering:

```python
class _AnonymousUser:
    is_authenticated = False
    settings = {}
    name = ''
```

## API Routes

### Router Registration

All 11 API routers in `app/api/__init__.py`:

```python
api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(measurements_router)
api_router.include_router(dashboard_router)
api_router.include_router(devices_router)
api_router.include_router(sessions_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(alerts_router)
api_router.include_router(benchmark_router)
api_router.include_router(settings_router)
api_router.include_router(audit_router)
```

### Route Dependencies

```python
from app.dependencies import get_db, require_user, get_api_key_device

@router.get('/devices')
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    ...
```

## Pagination

All list endpoints use `PaginatedResult`:

```python
@dataclass
class PaginatedResult:
    items: list
    page: int
    pages: int
    total: int
    per_page: int
```

### Usage

```python
def get_paginated(db: Session, page=1, per_page=10):
    q = db.query(Model)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)
```

## Adding a New API Endpoint

### 1. Create Service Method

```python
# app/services/my_service.py
class MyService:
    @staticmethod
    def get_all(db: Session):
        return db.query(MyModel).all()
```

### 2. Create Schema (if needed)

```python
# app/schemas/my_schema.py
class MyResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
```

### 3. Add Route

```python
# app/api/my_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user

router = APIRouter()

@router.get('/my-endpoint')
def my_handler(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    items = MyService.get_all(db)
    return items
```

### 4. Register Router

```python
# app/api/__init__.py
from .my_endpoint import router as my_router
api_router.include_router(my_router)
```

## Running the Server

### Development

```bash
fastapi run app/main.py --reload
```

### Production

```bash
fastapi run app/main.py --port 8000 --proxy-headers
```

### Docker

```bash
docker compose up
```
