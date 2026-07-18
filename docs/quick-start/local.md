# Local

Get BuckPow running locally with Python in 5 minutes.

---

## Prerequisites

- Python 3.12+
- pip

<!-- TODO: Replace with local development diagram -->

## Step 1 — Clone and Install

```bash
git clone https://github.com/arifnd/buckpow.git
cd buckpow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2 — Configure Environment (Optional)

```bash
cp .env.example .env
```

Edit `.env` to set admin credentials:

```env title=".env"
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-password
```

!!! info "SQLite Default"
    No database configuration needed. Tables are created automatically on first startup.

## Step 3 — Start the Server

```bash title="Development (with auto-reload)"
fastapi dev app/main.py --port 8000
```

```bash title="Production"
alembic upgrade head
fastapi run app/main.py --proxy-headers
```

## Step 4 — Open the Dashboard

Navigate to `http://localhost:8000`.

<!-- TODO: Replace with actual dashboard screenshot -->

Log in with the admin credentials from your `.env`.

!!! tip "Default Credentials"
    If no `ADMIN_EMAIL` / `ADMIN_PASSWORD` is configured, you can still access the dashboard in development mode. Set these environment variables to auto-create an admin account on first run.

## Step 5 — Send Your First Measurement

Without API key (dev mode):

```bash
curl -X POST http://localhost:8000/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "esp32-01",
    "bus_voltage": 5.12,
    "shunt_voltage": 82,
    "current": 241,
    "power": 1234
  }'
```

With API key:

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

!!! info "Auto-registration"
    Unknown `device_id` values are registered automatically as new devices.

## Step 6 — Generate Dummy Data (Optional)

```bash
python scripts/send_dummy.py --interval 1
```

```bash title="With API key"
python scripts/send_dummy.py --interval 1 --api-key <your-api-key>
```

---

## Using PostgreSQL Locally

If you prefer PostgreSQL over SQLite:

1. Install and start PostgreSQL
2. Create a database:

```bash
createdb buckpow
```

3. Set the connection string in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/buckpow
```

4. Run migrations:

```bash
alembic upgrade head
```

## Troubleshooting

### Port already in use

```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
fastapi dev app/main.py --port 8001
```

### Module not found

Ensure your virtual environment is activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database errors

```bash
# For SQLite, delete the database and restart
rm -f instance/buckpow.db
```

### Admin account not created

Ensure **both** `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set in your environment or `.env` file. The admin is only auto-created on first startup when both are present.
