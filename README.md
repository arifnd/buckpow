# BakPow

ESP32 power meter dashboard. Flask + SQLAlchemy + SQLite backend, Bootstrap 5 dashboard with Chart.js real-time charts.

```
ESP32 (INA219) ──HTTP POST──> Flask API ──> SQLite
                                    │
                             HTML Dashboard
                            (Chart.js, auto-refresh)
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
```

## Run

```bash
python run.py
```

Open http://localhost:5001. (Port 5000 is often taken by macOS AirPlay — `.env` defaults to 5001.)

## API

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/measurements` | Send a reading |
| GET | `/api/v1/measurements` | Paginated readings |
| GET | `/api/v1/dashboard` | Latest + stats + devices |
| GET | `/api/v1/chart` | Chart data (device/session filter) |
| GET/POST | `/api/v1/devices` | List / create devices |
| GET/PUT/DELETE | `/api/v1/devices/<id>` | Device CRUD |
| GET/POST | `/api/v1/sessions` | List / create sessions |
| GET/PUT/DELETE | `/api/v1/sessions/<id>` | Session CRUD |
| POST | `/api/v1/sessions/<id>/start` | Start session |
| POST | `/api/v1/sessions/<id>/stop` | Stop session |

### Send a reading

```bash
curl -X POST http://localhost:5001/api/v1/measurements \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"esp32-01","bus_voltage":5.12,"shunt_voltage":82,"current":241,"power":1234}'
```

## Pages

| Path | Page |
|---|---|
| `/` | Dashboard with real-time charts & summary cards |
| `/devices` | Device management |
| `/sessions` | Session management |
| `/measurements` | Paginated readings |

## Test

```bash
python -m pytest tests/ -v
```

## Send dummy data

```bash
python scripts/send_dummy.py --interval 1
```

## Config

`.env` supports `FLASK_HOST`, `FLASK_PORT` (default: 5001), `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `DEVICE_ONLINE_TIMEOUT`.
