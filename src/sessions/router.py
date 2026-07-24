from fastapi import APIRouter, HTTPException, Query, Request

from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.audit.service import AuditService
from src.utils.client_ip import get_client_ip
from src.dependencies import DbDep, RequiredUserDep
from src.sessions.schemas import SessionCreate, SessionUpdate

router = APIRouter()


@router.get("/sessions")
def list_sessions(
    db: DbDep,
    _current_user: RequiredUserDep,
    page: int = Query(1),
    per_page: int = Query(10),
):
    if page == 0:
        sessions = SessionService(db).get_all()
        session_ids = [s.id for s in sessions]
        stats = SessionService.get_stats_for_sessions(db, session_ids)
        result = []
        for s in sessions:
            d = s.to_dict()
            st = stats.get(s.id, {})
            d["avg_power"] = st.get("avg_power")
            d["total_energy"] = st.get("total_energy")
            result.append(d)
        return result
    pagination = SessionService(db).get_paginated(page=page, per_page=per_page)
    session_ids = [s.id for s in pagination.items]
    stats = SessionService.get_stats_for_sessions(db, session_ids)
    sessions = []
    for s in pagination.items:
        d = s.to_dict()
        st = stats.get(s.id, {})
        d["avg_power"] = st.get("avg_power")
        d["total_energy"] = st.get("total_energy")
        sessions.append(d)
    return {
        "sessions": sessions,
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
    }


@router.post("/sessions", status_code=201)
def create_session(
    body: SessionCreate,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if not body.name or not body.device_id:
        raise HTTPException(status_code=400, detail="name and device_id are required")
    session = SessionService(db).create(
        device_id=body.device_id,
        name=body.name,
        target_device=body.target_device,
        description=body.description,
        project_id=body.project_id,
    )
    return session.to_dict()


@router.get("/sessions/{session_id}")
def get_session(
    session_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    session = SessionService(db).get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.put("/sessions/{session_id}")
def update_session(
    session_id: int,
    body: SessionUpdate,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    session = SessionService(db).update(
        session_id,
        name=body.name,
        target_device=body.target_device,
        description=body.description,
        project_id=body.project_id,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if SessionService(db).delete(session_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions/{session_id}/stats")
def session_stats(
    session_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    stats = MeasurementService.get_session_stats(db, session_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return stats


@router.post("/sessions/{session_id}/start")
def start_session(
    session_id: int,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    session, error = SessionService(db).start(session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    ip = get_client_ip(request)
    AuditService(db).log(
        "session.start",
        user_id=_current_user.id,
        target_type="session",
        target_id=session_id,
        ip_address=ip,
    )
    return session.to_dict()


@router.post("/sessions/{session_id}/stop")
def stop_session(
    session_id: int,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    session, error = SessionService(db).stop(session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    ip = get_client_ip(request)
    AuditService(db).log(
        "session.stop",
        user_id=_current_user.id,
        target_type="session",
        target_id=session_id,
        ip_address=ip,
    )
    return session.to_dict()
