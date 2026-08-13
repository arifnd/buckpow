# Changelog

## v0.1.0-beta.6 (2026-08-14)

### Features
- Migrated to a compiled Tailwind CSS pipeline — replaces the Tailwind CDN with a generated `static/css/app.css` (build via `npm run build:css`)
- Migrated dependency management to `uv` (lockfile, `uv sync`, two-stage Docker build)
- Rebuilt all page templates with native Tailwind utility classes, mobile-first layouts, soft pill tags, and inline SVG (heroicons) icons
- Sidebar toggle, user dropdown, and theme submenu now use Alpine.js
- Static assets moved from `src/static/` to the root `static/` directory
- Added GitHub issue templates (bug report, feature request, feature planning, documentation)

### Bug Fixes
- Password show/hide toggle on the login page — replaced corrupted eye/eye-off SVG paths with valid Material icons
- Browser autofill no longer forces a white/yellow background on inputs in dark mode

### UI Polish
- Session detail page: back link moved to the action bar as an outlined button
- Session detail buttons: Export CSV green, Edit blue

### CI/CD
- Matrix CI tests on Python 3.12-3.14
- Prerelease and release workflows improved: `uv sync --frozen`, shared version-check action, container health smoke test, provenance + SBOM attestations, auto-generated GitHub release notes
- Frontend tests updated for the compiled CSS and Alpine.js pipeline

### Chores
- Version sync script now keeps `package.json` and `package-lock.json` in sync with `src/version.py`
- Docs and `AGENTS.md` updated to reflect the compiled Tailwind, Alpine.js, and inline SVG approach

---

## v0.1.0-beta.5 (2026-07-28)

### Security (CRITICAL)
- **C1**: CORS origins now configurable via `ALLOWED_ORIGINS` env var (default: localhost only)
- **C2**: `JWT_SECRET` is now required — no hardcoded default
- **C3**: `.env` cleaned with placeholder values and documentation
- **C4**: JWT token removed from login response body (still set as httponly cookie)
- **C5**: Added ownership check to device API key endpoint

### Security (HIGH)
- **H1**: Add CSRF middleware for HTMX requests (double-submit cookie pattern)
- **H2**: Move MySQL password from command line to `MYSQL_PWD` env var
- **H3**: Sanitize DB error messages in backup responses (log internally)
- **H4**: Enable device auth by default + startup warning when disabled
- **H5**: Add `MAX_AUTO_REGISTERED_DEVICES` limit (50) with 503 response

### Features
- Add node local IP reporting — `PATCH /api/v1/devices/local-ip` endpoint (device auth)
- Firmware reports local IP once after WiFi connects + first successful API call
- `local_ip` column added to devices table with Alembic migration
- Devices page: show IP column, remove Description column
- Firmware version bumped 1.1.0 → 1.2.0

### Bug Fixes
- `device_id` fallback added to `PATCH /devices/local-ip` endpoint
- Rate limiter state cleared between tests to prevent 429 flakiness
- Fixed `JWT_SECRET` warnings by using 32+ char test keys

### Testing
- 20 new security tests added
- Optimized slow test suite: consolidated subprocess tests, replaced sleep polling with `time.monotonic()` deadline
- 6 tests for new local-ip endpoint (auth, validation, disabled device)

### Refactors & Chores
- Removed unused `src/auth/config.py` (duplicate of `src/config.py`)
- Fixed all ruff lint errors (unused imports, import sorting, nested with statements)
- `pyproject.toml` project metadata and `.fastapicloudignore` added

### Documentation
- Mermaid diagrams added for Docker Compose architecture, local development, and connection flow
- "Devices" renamed to "Nodes" in all user-facing docs, nav, and pages
- Multiple docs inaccuracies fixed across README, API docs, firmware docs, and contributing guide

---

## v0.1.0-beta.4 (2026-07-27)

### Features
- Ruff added to pre-commit hook and CI workflow
- Ruff auto-fixes applied across codebase
- CI upgraded to Node 24 compatible GitHub Actions versions
- Refactored test config: `pytest-env` + in-memory SQLite for faster tests
- `AppBaseModel` with `@field_serializer` for datetime serialization
- Per-domain `BaseSettings` configs replacing monolithic settings
- Legacy `Depends()` migrated to `Annotated[T, Depends(...)]`
- StrEnum validation for alert levels in Pydantic schemas
- API docs gating switched from `DISABLE_API_DOCS` bool to env-based
- MetaData naming convention for SQLAlchemy indexes
- Descriptive migration filenames configured in `alembic.ini`
- Docker image converted to `uv` for package management

### Bug Fixes
- `datetime.timezone.utc` replaced with `datetime.UTC` (UP017)
- All ruff lint errors resolved (B904, SIM102, SIM103, SIM117, F811, F841, B011, E741, E501, E402)

### CI
- Lint and test combined into single workflow
- GitHub Actions pin updates for Node 24 compatibility

### Documentation
- Raw FastAPI Best Practices for AI Agents added as `AGENTS.md`

---

## v0.1.0-beta.3 (2026-07-22)

### Bug Fixes
- Internal Server Error when deleting a node/device
- Benchmark charts rendering incorrectly
- Flowbite datepicker replaced with native date picker on measurements page

### Chores
- Code formatting applied with ruff

---

## v0.1.0-beta.2 (2026-07-21)

### Features
- Service Layer Refactor — business logic separated from HTTP handlers (7 services)
- Domain Organization — one package per bounded context
- Dashboard Routes Modernization
- Device label renamed to "Node" across all UI, firmware, and docs
- Session detail page load performance improved

### Testing & Quality Assurance
- Comprehensive test suite (696+ tests)
- FastAPI Best Practices document added for AI agents

---

## v0.1.0-beta.1 (2026-07-15)

Initial public beta release.

### Features
- Energy measurement ingestion via HTTP POST (ESP32/ESP8266 + INA219)
- Real-time dashboard with Chart.js and dark theme
- Device management with API key authentication
- Session management with start/stop and energy tracking
- Project management with device/session associations
- Alert system with info/warning/critical levels
- Benchmark comparison page (2-3 sessions)
- Measurement export (CSV + XLSX)
- User authentication (JWT, cookie-based for dashboard, Bearer for API)
- User profile and settings pages
- Audit logging
- Rate limiting middleware
- Database backup (compressed SQL dump)
- Tailwind CSS UI with light/dark theme toggle
- HTMX-powered SPA-like navigation
- Firmware sketches for ESP32/ESP8266 with captive portal
- Docker deployment (PostgreSQL + Nginx production stack)
- Migration-ready with Alembic / Flask-Migrate
- 696+ tests across all domains
