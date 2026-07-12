from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.session_service import SessionService
from app.services.audit_service import AuditService
from app.utils.client_ip import get_client_ip
from app.dependencies import require_user
from app.schemas import SessionCreate, SessionUpdate

router = APIRouter()


@router.get('/sessions')
def list_sessions(
    page: int = Query(1),
    per_page: int = Query(10),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    if page == 0:
        sessions = SessionService.get_all(db)
        session_ids = [s.id for s in sessions]
        stats = SessionService.get_stats_for_sessions(db, session_ids)
        result = []
        for s in sessions:
            d = s.to_dict()
            st = stats.get(s.id, {})
            d['avg_power'] = st.get('avg_power')
            d['total_energy'] = st.get('total_energy')
            result.append(d)
        return result
    pagination = SessionService.get_paginated(db, page=page, per_page=per_page)
    session_ids = [s.id for s in pagination.items]
    stats = SessionService.get_stats_for_sessions(db, session_ids)
    sessions = []
    for s in pagination.items:
        d = s.to_dict()
        st = stats.get(s.id, {})
        d['avg_power'] = st.get('avg_power')
        d['total_energy'] = st.get('total_energy')
        sessions.append(d)
    return {
        'sessions': sessions,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    }


@router.post('/sessions', status_code=201)
def create_session(body: SessionCreate, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    if not body.name or not body.device_id:
        raise HTTPException(status_code=400, detail='name and device_id are required')
    session = SessionService.create(
        db,
        device_id=body.device_id,
        name=body.name,
        target_device=body.target_device,
        description=body.description,
        project_id=body.project_id,
    )
    return session.to_dict()


@router.get('/sessions/{session_id}')
def get_session(session_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    session = SessionService.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    return session.to_dict()


@router.put('/sessions/{session_id}')
def update_session(session_id: int, body: SessionUpdate, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    session = SessionService.update(
        db, session_id,
        name=body.name,
        target_device=body.target_device,
        description=body.description,
        project_id=body.project_id,
    )
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    return session.to_dict()


@router.delete('/sessions/{session_id}')
def delete_session(session_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    if SessionService.delete(db, session_id):
        return {'status': 'deleted'}
    raise HTTPException(status_code=404, detail='Session not found')


@router.post('/sessions/{session_id}/start')
def start_session(session_id: int, request: Request, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    session, error = SessionService.start(db, session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    ip = get_client_ip(request)
    AuditService.log(db, 'session.start', user_id=_current_user.id, target_type='session', target_id=session_id, ip_address=ip)
    return session.to_dict()


@router.post('/sessions/{session_id}/stop')
def stop_session(session_id: int, request: Request, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    session, error = SessionService.stop(db, session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    ip = get_client_ip(request)
    AuditService.log(db, 'session.stop', user_id=_current_user.id, target_type='session', target_id=session_id, ip_address=ip)
    return session.to_dict()
