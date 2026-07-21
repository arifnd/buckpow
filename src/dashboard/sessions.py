from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_db
from src.auth.models import User
from src.template_helpers import _render, _render_or_redirect, _require_dashboard_user
from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.projects.service import ProjectService

router = APIRouter()


@router.get('/sessions')
def sessions_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect('sessions/index.html', current_user, 'sessions')


@router.get('/sessions/new')
def sessions_new_page(
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    all_devices = DeviceService(db).get_all()
    devices = [d for d in all_devices if not SessionService(db).get_active_session(d.id)]
    return _render_or_redirect('sessions/form.html', current_user, 'sessions', session=None, devices=devices, projects=ProjectService(db).get_all())


@router.get('/sessions/{session_id}/edit')
def sessions_edit_page(
    session_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SessionService(db).get_by_id(session_id)
    return _render_or_redirect('sessions/form.html', current_user, 'sessions', session=session, devices=DeviceService(db).get_all(), projects=ProjectService(db).get_all())


@router.get('/sessions/{session_id}')
def sessions_detail_page(
    session_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    session = SessionService(db).get_by_id(session_id)
    if not session:
        return RedirectResponse(url='/sessions', status_code=302)
    return HTMLResponse(_render('sessions/detail.html', current_user=current_user, active_page='sessions', session=session))
