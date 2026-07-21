# Docker

Get BuckPow running with Docker Compose in 5 minutes.

---

## Prerequisites

- [Docker Engine](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+

<!-- TODO: Replace with Docker Compose architecture diagram -->

## Step 1 — Clone and Configure

```bash
git clone https://github.com/arifnd/buckpow.git
cd buckpow
cp .env.example .env
```

Edit `.env`:

```env title=".env"
APP_ENV=production
JWT_SECRET=replace-this-with-a-strong-random-string
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-password
DISABLE_API_DOCS=true
```

!!! warning "Production"
    In production mode, `JWT_SECRET` is **required**. The application will not start without it.

## Step 2 — Start Services

```bash
docker compose up -d
```

This starts three services:

| Service | Port | Description |
|---------|------|-------------|
| `db` | *(internal)* | PostgreSQL 16 |
| `app` | `8000` | BuckPow API + Dashboard |
| `nginx` | `80` | Reverse proxy |

Verify all services are running:

```bash
docker compose ps
```

## Step 3 — Open the Dashboard

Navigate to `http://localhost` (port 80) or `http://localhost:8000` (direct).

<!-- TODO: Replace with actual login screenshot -->

Log in with the admin credentials from your `.env`.

## Step 4 — Send Your First Measurement

```bash
curl -X POST http://localhost:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your-api-key>' \
  -d '{
    "device_id": "esp32-01",
    "bus_voltage": 5.12,
    "shunt_voltage": 82,
    "current": 241,
    "power": 1234
  }'
```

The device will appear on the dashboard with a live status indicator.

## Step 5 — Generate Dummy Data (Optional)

```bash
docker compose exec app python scripts/send_dummy.py --interval 1 --api-key <your-api-key>
```

---

## Stopping Services

```bash
docker compose down
```

To remove all data including the database:

```bash
docker compose down -v
```

## Troubleshooting

### Container won't start

Check the logs:

```bash
docker compose logs app
docker compose logs db
```

### Database connection refused

Ensure the `db` container is healthy before `app` starts:

```bash
docker compose ps
```

The `app` service waits for the `db` healthcheck to pass before starting.

### Port already in use

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:80"   # nginx
  - "8001:8000" # app
```
