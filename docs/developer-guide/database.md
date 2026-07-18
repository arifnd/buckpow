# Database

Database schema, models, and migration guide.

---

## Overview

BuckPow uses SQLAlchemy ORM with support for three database backends:

| Backend | Default | Use Case |
|---------|---------|----------|
| **SQLite** | Yes | Development, single-user |
| **PostgreSQL** | No | Production, multi-user |
| **MySQL / MariaDB** | No | Production alternative |

<!-- TODO: Replace with ER diagram -->

## Configuration

Set the database connection in `.env`:

```env title="SQLite (default)"
DATABASE_URL=sqlite:///instance/buckpow.db
```

```env title="PostgreSQL"
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

```env title="MySQL"
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
```

## Tables

### Users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `name` | String(128) | NOT NULL | Display name |
| `email` | String(256) | UNIQUE, NOT NULL, indexed | Login email |
| `password` | String(256) | NOT NULL | Bcrypt hash |
| `settings` | JSON | NOT NULL, default `{}` | User preferences |
| `created_at` | DateTime | Default UTC now | Account creation |

### Devices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `device_id` | String(64) | UNIQUE, NOT NULL, indexed | Device identifier |
| `alias` | String(128) | Default `''` | Friendly name |
| `description` | Text | Default `''` | Notes |
| `sampling_interval` | Integer | Default `1` | Seconds between measurements |
| `last_seen` | DateTime | Nullable | Last measurement timestamp |
| `status` | String(16) | Default `'offline'` | Computed status |
| `enabled` | Boolean | Default `True` | Active flag |
| `firmware_version` | String(64) | Default `''` | Firmware version |
| `api_key` | String(64) | UNIQUE, nullable, indexed | API authentication key |
| `project_id` | Integer | FK → `projects.id`, nullable | Project assignment |
| `high_current_threshold` | Float | Nullable | Alert threshold (A) |
| `high_power_threshold` | Float | Nullable | Alert threshold (W) |
| `low_voltage_threshold` | Float | Nullable | Alert threshold (V) |
| `created_at` | DateTime | Default UTC now | Creation time |
| `updated_at` | DateTime | Default UTC now, auto-update | Last modification |

### Sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `device_id` | Integer | FK → `devices.id`, NOT NULL | Recording device |
| `name` | String(256) | NOT NULL | Session name |
| `target_device` | String(64) | Default `''` | Device under test |
| `description` | Text | Default `''` | Notes |
| `status` | String(16) | Default `'draft'` | `draft`, `running`, `finished` |
| `project_id` | Integer | FK → `projects.id`, nullable | Project assignment |
| `started_at` | DateTime | Nullable | Start timestamp |
| `ended_at` | DateTime | Nullable | End timestamp |
| `created_at` | DateTime | Default UTC now | Creation time |
| `updated_at` | DateTime | Default UTC now, auto-update | Last modification |

### Measurements

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `session_id` | Integer | FK → `sessions.id`, nullable | Session association |
| `device_id` | Integer | FK → `devices.id`, NOT NULL | Source device |
| `bus_voltage` | Float | NOT NULL | Bus voltage (V) |
| `shunt_voltage` | Float | Default `0.0` | Shunt voltage (V) |
| `load_voltage` | Float | NOT NULL | Load voltage (V) |
| `current` | Float | NOT NULL | Current (A) |
| `power` | Float | NOT NULL | Power (W) |
| `energy` | Float | Default `0.0` | Cumulative energy (Wh) |
| `created_at` | DateTime | Default UTC now | Measurement timestamp |

**Indexes:**

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_measurement_device_time` | `(device_id, created_at)` | Device history queries |
| `idx_measurement_session_time` | `(session_id, created_at)` | Session chart queries |

### Alerts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `device_id` | Integer | FK → `devices.id`, NOT NULL, indexed | Triggering device |
| `level` | String(16) | NOT NULL, default `'warning'` | `info`, `warning`, `critical` |
| `message` | String(256) | NOT NULL | Alert description |
| `created_at` | DateTime | Default UTC now | Creation time |
| `resolved_at` | DateTime | Nullable | Resolution time (null = unresolved) |

### Projects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `name` | String(256) | NOT NULL | Project name |
| `description` | Text | Default `''` | Notes |
| `owner_id` | Integer | FK → `users.id`, nullable | Owner user |
| `created_at` | DateTime | Default UTC now | Creation time |
| `updated_at` | DateTime | Default UTC now, auto-update | Last modification |

### Audit Logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK | Auto-increment ID |
| `user_id` | Integer | FK → `users.id`, nullable, indexed | Acting user |
| `action` | String(64) | NOT NULL, indexed | Action type |
| `target_type` | String(32) | Nullable | Resource type |
| `target_id` | Integer | Nullable | Resource ID |
| `details` | JSON | Nullable | Additional data |
| `ip_address` | String(45) | Nullable | Client IP |
| `created_at` | DateTime | Default UTC now, indexed | Action time |

## Relationships

```mermaid
erDiagram
    users ||--o{ projects : owns
    projects ||--o{ devices : contains
    projects ||--o{ sessions : contains
    devices ||--o{ sessions : has
    devices ||--o{ measurements : produces
    devices ||--o{ alerts : triggers
    sessions ||--o{ measurements : contains
    users ||--o{ audit_logs : performs

    users {
        int id PK
        string email UK
    }

    projects {
        int id PK
        int owner_id FK
    }

    devices {
        int id PK
        string device_id UK
        int project_id FK
    }

    sessions {
        int id PK
        int device_id FK
        int project_id FK
    }

    measurements {
        int id PK
        int device_id FK
        int session_id FK
    }

    alerts {
        int id PK
        int device_id FK
    }

    audit_logs {
        int id PK
        int user_id FK
    }
```

## Indexes

| Table | Index | Columns | Type |
|-------|-------|---------|------|
| `devices` | `device_id` | `device_id` | Unique |
| `devices` | `api_key` | `api_key` | Unique |
| `measurements` | `idx_measurement_device_time` | `(device_id, created_at)` | Composite |
| `measurements` | `idx_measurement_session_time` | `(session_id, created_at)` | Composite |
| `alerts` | `device_id` | `device_id` | Standard |
| `audit_logs` | `created_at` | `created_at` | Standard |
| `audit_logs` | `action` | `action` | Standard |
| `users` | `email` | `email` | Unique |

## Migrations

BuckPow uses Alembic for database migrations.

### Creating Migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply one migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>
```

### Migration History

```bash
# Show migration history
alembic history

# Show current revision
alembic current

# Show pending migrations
alembic heads
```

### SQLite Auto-Setup

For SQLite, tables are created automatically on first run:

```python
if 'sqlite' in settings.DATABASE_URL:
    Base.metadata.create_all(bind=engine)
    command.stamp(alembic_cfg, 'head')
```

No manual migration step needed for SQLite.

### PostgreSQL Setup

For PostgreSQL, run migrations manually:

```bash
alembic upgrade head
```

## Connection Pool

### Engine Configuration

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)
```

| Setting | Value | Description |
|---------|-------|-------------|
| `pool_pre_ping` | `True` | Test connections before use |
| `echo` | `DEBUG` | Log SQL queries in development |

### Pool Settings

Default SQLAlchemy pool settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `pool_size` | 5 | Persistent connections |
| `max_overflow` | 10 | Extra connections |
| `pool_timeout` | 30 | Seconds to wait for connection |
| `pool_recycle` | 1800 | Recycle connections after 30 min |

## Data Types

### Voltage

- Stored as `Float` in **Volts (V)**
- Bus voltage: 0–26V range
- Shunt voltage: 0–0.32V range
- Load voltage: Computed (bus - shunt)

### Current

- Stored as `Float` in **Amperes (A)**
- Converted from mA (device) → A (database)
- Range: 0–3.2A

### Power

- Stored as `Float` in **Watts (W)**
- Converted from mW (device) → W (database)
- Range: 0–80W

### Energy

- Stored as `Float` in **Watt-hours (Wh)**
- Cumulative: `energy += power × sampling_interval / 3600`
- Precision: 6 decimal places

### Timestamps

- Stored as `DateTime` in **UTC**
- Converted to ISO 8601 for API responses
- User-configurable timezone offset in dashboard

## Schema Diagram

```mermaid
graph TD
    subgraph Core
        User[users]
        Project[projects]
        Device[devices]
        Session[sessions]
        Measurement[measurements]
        Alert[alerts]
        AuditLog[audit_logs]
    end

    User -->|owns| Project
    Project -->|contains| Device
    Project -->|contains| Session
    Device -->|has| Session
    Device -->|produces| Measurement
    Device -->|triggers| Alert
    Session -->|contains| Measurement
    User -->|performs| AuditLog
```

## Backup and Restore

### SQLite

```bash
# Backup
cp instance/buckpow.db backup/buckpow-$(date +%Y%m%d).db

# Restore
cp backup/buckpow-20260718.db instance/buckpow.db
```

### PostgreSQL

```bash
# Backup
pg_dump -U buckpow buckpow > backup/buckpow-$(date +%Y%m%d).sql

# Restore
psql -U buckpow buckpow < backup/buckpow-20260718.sql
```

### MySQL

```bash
# Backup
mysqldump -u buckpow -p buckpow > backup/buckpow-$(date +%Y%m%d).sql

# Restore
mysql -u buckpow -p buckpow < backup/buckpow-20260718.sql
```

### BuckPow API Backup

BuckPow provides a backup endpoint through the Settings API:

```bash
# SQLite
curl http://localhost:8000/api/v1/settings/backup \
  -H 'Authorization: Bearer <jwt-token>' \
  --output backup.db

# PostgreSQL (gzipped)
curl http://localhost:8000/api/v1/settings/backup \
  -H 'Authorization: Bearer <jwt-token>' \
  --output backup.sql.gz
```

## Performance Tips

### Query Optimization

- Use indexed columns in `WHERE` clauses
- Filter by `device_id` and `created_at` for measurement queries
- Use `session_id` filter for session-specific data

### Large Tables

The `measurements` table grows fastest. For high-frequency sampling:

- Monitor table size regularly
- Archive old data periodically
- Use PostgreSQL for better performance at scale

### Connection Management

- Always close sessions in `finally` blocks
- Use the `get_db()` dependency for automatic cleanup
- Enable `pool_pre_ping` for connection health checks
