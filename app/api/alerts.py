from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.alert_service import AlertService
from app.auth import require_user

router = APIRouter()


class AlertCreate(BaseModel):
    device_id: int
    level: str = 'warning'
    message: str


@router.get('/alerts')
def list_alerts(
    page: int = Query(1),
    per_page: int = Query(10),
    device_id: int | None = Query(None),
    level: str | None = Query(None),
    resolved: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    resolved_bool = None
    if resolved is not None:
        resolved_bool = resolved.lower() in ('true', '1')
    pagination = AlertService.get_paginated(
        db, page=page, per_page=per_page,
        device_id=device_id, level=level, resolved=resolved_bool,
    )
    return {
        'alerts': [a.to_dict() for a in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
        'unresolved_count': AlertService.get_unresolved_count(db),
    }


@router.post('/alerts', status_code=201)
def create_alert(body: AlertCreate, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    alert = AlertService.create(db, body.device_id, body.level, body.message)
    return alert.to_dict()


@router.patch('/alerts/{alert_id}/resolve')
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    alert = AlertService.resolve(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    return alert.to_dict()


@router.post('/alerts/resolve-all')
def resolve_all(
    device_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    AlertService.resolve_all(db, device_id=device_id)
    return {'status': 'ok'}
