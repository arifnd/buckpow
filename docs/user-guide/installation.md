# Installation

Full installation guide for BuckPow with all configuration options.

---

## System Requirements

<!-- TODO: Replace with system requirements diagram -->

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 256 MB | 512 MB+ |
| Disk | 100 MB | 1 GB+ (depends on measurement volume) |
| Python | 3.12+ | 3.12+ |
| Docker | 20.10+ | 24+ (for containerized deployment) |

## Installation Methods

=== "Docker (Recommended)"

    ### Docker Compose

    The recommended way to run BuckPow in production.

    **1. Clone the repository**

    ```bash
    git clone https://github.com/arifnd/buckpow.git
    cd buckpow
    ```

    **2. Create environment file**

    ```bash
    cp .env.example .env
    ```

    **3. Configure environment variables**

    Edit `.env` with your settings:

    ```env
    APP_ENV=production
    JWT_SECRET=your-strong-random-secret-key-min-32-chars
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=your-secure-password
    DATABASE_URL=postgresql://buckpow:buckpow@db:5432/buckpow
    DISABLE_API_DOCS=true
    ```

    **4. Start services**

    ```bash
    docker compose up -d
    ```

    **5. Verify**

    ```bash
    docker compose ps
    curl http://localhost:8000/api/v1/health
    ```

=== "Local Development"

    ### Virtual Environment

    Best for development and testing.

    **1. Clone and setup**

    ```bash
    git clone https://github.com/arifnd/buckpow.git
    cd buckpow
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    **2. Create environment file (optional)**

    ```bash
    cp .env.example .env
    ```

    Edit `.env` to set admin credentials:

    ```env
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=your-secure-password
    ```

    **3. Start development server**

    ```bash
    fastapi dev app/main.py --port 8000
    ```

    !!! info "Auto-reload"
        The development server auto-reloads when code changes.

=== "Local Production"

    ### Production Server

    For self-hosted production without Docker.

    **1. Clone and setup**

    ```bash
    git clone https://github.com/arifnd/buckpow.git
    cd buckpow
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    **2. Configure environment**

    ```bash
    cp .env.example .env
    ```

    Edit `.env`:

    ```env
    APP_ENV=production
    JWT_SECRET=your-strong-random-secret-key-min-32-chars
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=your-secure-password
    DATABASE_URL=postgresql://user:pass@localhost:5432/buckpow
    ```

    **3. Run migrations**

    ```bash
    alembic upgrade head
    ```

    **4. Start production server**

    ```bash
    fastapi run app/main.py --proxy-headers
    ```

## Environment Variables

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment mode: `development` or `production` |
| `JWT_SECRET` | `buckpow-dev-key-change-in-production` | JWT signing key. **Required in production** (min 32 chars) |
| `APP_HOST` | `0.0.0.0` | Server bind address |
| `APP_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `info` | Python logging level: `debug`, `info`, `warning`, `error` |

### Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///instance/buckpow.db` | Database connection string |

BuckPow supports three database backends:

```env title="SQLite (default)"
DATABASE_URL=sqlite:///instance/buckpow.db
```

```env title="PostgreSQL"
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

```env title="MySQL / MariaDB"
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
```

!!! info "SQLite"
    SQLite requires no configuration. The database file is created automatically at `instance/buckpow.db`.

!!! info "PostgreSQL / MySQL"
    Requires the corresponding driver. Both are included in `requirements.txt`.

### Admin Account

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_EMAIL` | *(empty)* | Admin email for auto-creation on first run |
| `ADMIN_PASSWORD` | *(empty)* | Admin password for auto-creation on first run |

!!! tip "Auto-creation"
    The admin account is created automatically on first startup when **both** `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set.

### Device Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVICE_ONLINE_TIMEOUT` | `30` | Seconds before a device is marked offline |
| `DEFAULT_SAMPLING_INTERVAL` | `1` | Default sampling interval in seconds for new devices |
| `DEVICE_AUTH_ENABLED` | `true` | Require API keys for device authentication |

### API Documentation

| Variable | Default | Description |
|----------|---------|-------------|
| `DISABLE_API_DOCS` | `false` | Disable `/docs`, `/redoc`, and `/openapi.json` |

!!! warning "Production"
    Set `DISABLE_API_DOCS=true` in production to hide API documentation endpoints.

### Advanced Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | JWT token expiry time |

## Database Setup

### SQLite

No setup required. The database file is created automatically on first startup.

### PostgreSQL

**1. Install PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@16

# Docker (standalone)
docker run -d --name postgres \
  -e POSTGRES_USER=buckpow \
  -e POSTGRES_PASSWORD=buckpow \
  -e POSTGRES_DB=buckpow \
  -p 5432:5432 \
  postgres:16-alpine
```

**2. Create database**

```bash
createdb buckpow
```

**3. Set connection string**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/buckpow
```

**4. Run migrations**

```bash
alembic upgrade head
```

### MySQL / MariaDB

**1. Install MySQL**

```bash
# Ubuntu/Debian
sudo apt install mysql-server

# macOS
brew install mysql

# Docker (standalone)
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=buckpow \
  -e MYSQL_USER=buckpow \
  -e MYSQL_PASSWORD=buckpow \
  -p 3306:3306 \
  mysql:8
```

**2. Set connection string**

```env
DATABASE_URL=mysql+pymysql://buckpow:buckpow@localhost:3306/buckpow
```

**3. Run migrations**

```bash
alembic upgrade head
```

## Reverse Proxy Configuration

### Nginx

For production deployments, use Nginx as a reverse proxy:

```nginx title="nginx.conf"
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com
```

## Firewall Rules

Open the required ports:

```bash
# Docker Compose setup (Nginx on 80, direct on 8000)
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp

# Or just the direct port
sudo ufw allow 8000/tcp
```

## Verifying Installation

<!-- TODO: Replace with verification screenshot -->

**1. Health check**

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "min_firmware_version": "1.0.0"
}
```

**2. Open dashboard**

Navigate to `http://localhost:8000` in your browser.

**3. Login**

Use the admin credentials you configured.

**4. Send test measurement**

```bash
curl -X POST http://localhost:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"test-01","bus_voltage":5.0,"shunt_voltage":50,"current":150,"power":750}'
```

## Updating BuckPow

=== "Docker"

    ```bash
    cd buckpow
    git pull
    docker compose up -d --build
    ```

=== "Local"

    ```bash
    cd buckpow
    git pull
    source venv/bin/activate
    pip install -r requirements.txt
    alembic upgrade head
    ```

## Backup and Restore

### SQLite

```bash
# Backup
cp instance/buckpow.db instance/buckpow backup.db

# Restore
cp instance/buckpow backup.db instance/buckpow.db
```

### PostgreSQL

```bash
# Backup
pg_dump -U buckpow buckpow > backup.sql

# Restore
psql -U buckpow buckpow < backup.sql
```

BuckPow also provides a backup endpoint through the Settings API. See [Settings](../developer-guide/api.md) for details.
