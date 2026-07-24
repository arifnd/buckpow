from fastapi import APIRouter, Query, HTTPException

from src.alerts.service import AlertService
from src.dependencies import DbDep, RequiredUserDep
from src.alerts.schemas import AlertCreate

router = APIRouter()


@router.get("/alerts")
def list_alerts(
    db: DbDep,
    _current_user: RequiredUserDep,
    page: int = Query(1),
    per_page: int = Query(10),
    device_id: int | None = Query(None),
    level: str | None = Query(None),
    resolved: str | None = Query(None),
):
    resolved_bool = None
    if resolved is not None:
        resolved_bool = resolved.lower() in ("true", "1")
    pagination = AlertService(db).get_paginated(
        page=page,
        per_page=per_page,
        device_id=device_id,
        level=level,
        resolved=resolved_bool,
    )
    return {
        "alerts": [a.to_dict() for a in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
        "unresolved_count": AlertService(db).get_unresolved_count(),
    }


@router.post("/alerts", status_code=201)
def create_alert(
    body: AlertCreate,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    alert = AlertService(db).create(body.device_id, body.level, body.message)
    return alert.to_dict()


@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    alert = AlertService(db).resolve(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert.to_dict()


@router.post("/alerts/resolve-all")
def resolve_all(
    db: DbDep,
    _current_user: RequiredUserDep,
    device_id: int | None = Query(None),
):
    AlertService(db).resolve_all(device_id=device_id)
    return {"status": "ok"}
