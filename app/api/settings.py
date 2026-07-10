from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.auth import require_user
from app.models import User

router = APIRouter()


class SettingsUpdate(BaseModel):
    high_power_threshold: float | str | None = None
    high_current_threshold: float | str | None = None
    low_voltage_threshold: float | str | None = None
    brand: str | None = None
    timestamp_format: str | None = None
    timezone: str | None = None
    device_watchdog_timeout: int | str | None = None


ALLOWED = {'high_power_threshold', 'high_current_threshold', 'low_voltage_threshold',
           'brand', 'timestamp_format', 'timezone', 'device_watchdog_timeout'}


@router.get('/settings')
def get_settings(current_user: User = Depends(require_user)):
    return current_user.settings or {}


@router.put('/settings')
def update_settings(
    body: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    current = dict(current_user.settings or {})
    data = body.model_dump(exclude_none=True)
    for key, value in data.items():
        if key in ALLOWED:
            if value == '' or value is None:
                current.pop(key, None)
            else:
                current[key] = value
    current_user.settings = current
    db.commit()
    return current


@router.get('/settings/backup')
def backup_database(current_user: User = Depends(require_user)):
    db_url = str(engine.url)
    if db_url.startswith('sqlite:///'):
        db_path = db_url[10:]
    elif db_url.startswith('sqlite://'):
        db_path = db_url[9:]
    else:
        raise HTTPException(status_code=400, detail='Backup only supported for SQLite')

    if not os.path.isabs(db_path):
        from app.config import settings as app_settings
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', db_path)

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail='Database file not found')

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    with open(db_path, 'rb') as f:
        content = f.read()
    return Response(
        content=content,
        media_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename=buckpow-backup-{ts}.db'},
    )
