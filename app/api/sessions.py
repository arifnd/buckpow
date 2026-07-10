from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.session_service import SessionService

router = APIRouter()


class SessionCreate(BaseModel):
    device_id: int
    name: str
    target_device: str = ''
    description: str = ''
    project_id: int | None = None


class SessionUpdate(BaseModel):
    name: str | None = None
    target_device: str | None = None
    description: str | None = None
    project_id: int | None = None


@router.get('/sessions')
def list_sessions(
    page: int = Query(1),
    per_page: int = Query(10),
    db: Session = Depends(get_db),
):
    if page == 0:
        sessions = SessionService.get_all(db)
        return [s.to_dict() for s in sessions]
    pagination = SessionService.get_paginated(db, page=page, per_page=per_page)
    return {
        'sessions': [s.to_dict() for s in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    }


@router.post('/sessions', status_code=201)
def create_session(body: SessionCreate, db: Session = Depends(get_db)):
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
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = SessionService.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    return session.to_dict()


@router.put('/sessions/{session_id}')
def update_session(session_id: int, body: SessionUpdate, db: Session = Depends(get_db)):
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
def delete_session(session_id: int, db: Session = Depends(get_db)):
    if SessionService.delete(db, session_id):
        return {'status': 'deleted'}
    raise HTTPException(status_code=404, detail='Session not found')


@router.post('/sessions/{session_id}/start')
def start_session(session_id: int, db: Session = Depends(get_db)):
    session, error = SessionService.start(db, session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return session.to_dict()


@router.post('/sessions/{session_id}/stop')
def stop_session(session_id: int, db: Session = Depends(get_db)):
    session, error = SessionService.stop(db, session_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return session.to_dict()
