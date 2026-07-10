from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.auth import get_current_user
from app.models import User
from app.services.project_service import ProjectService
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.database import get_db
from sqlalchemy.orm import Session


dashboard_router = APIRouter()

templates = Environment(loader=FileSystemLoader('app/templates'), autoescape=True)


def _url_for(endpoint, **kwargs):
    if endpoint == 'static':
        return '/static/' + kwargs.get('filename', '')
    return '/'


templates.globals['url_for'] = _url_for
templates.globals['app_version'] = '0.1.0'


class _AnonymousUser:
    is_authenticated = False
    settings = {}
    name = ''


_ANONYMOUS = _AnonymousUser()


def _render(name, current_user=None, **kwargs):
    user = current_user if current_user is not None else _ANONYMOUS
    return templates.get_template(name).render(current_user=user, **kwargs)


def _require_dashboard_user(current_user):
    if current_user is None:
        return RedirectResponse(url='/auth/login', status_code=302)
    return current_user


@dashboard_router.get('/auth/login')
def login_page(current_user: User | None = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url='/', status_code=302)
    return HTMLResponse(_render('auth/login.html', current_user=current_user))


@dashboard_router.post('/auth/logout')
def logout_page():
    return {'status': 'ok'}


@dashboard_router.get('/')
def index(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('dashboard/index.html', current_user=current_user, active_page='dashboard'))


@dashboard_router.get('/devices')
def devices_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('devices/index.html', current_user=current_user, active_page='devices'))


@dashboard_router.get('/devices/new')
def devices_new_page(
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    projects = ProjectService.get_all(db)
    return HTMLResponse(_render('devices/form.html', current_user=current_user, active_page='devices', device=None, projects=projects))


@dashboard_router.get('/devices/{device_id}/edit')
def devices_edit_page(
    device_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    device = DeviceService.get_by_id(db, device_id)
    projects = ProjectService.get_all(db)
    return HTMLResponse(_render('devices/form.html', current_user=current_user, active_page='devices', device=device, projects=projects))


@dashboard_router.get('/sessions')
def sessions_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('sessions/index.html', current_user=current_user, active_page='sessions'))


@dashboard_router.get('/sessions/new')
def sessions_new_page(
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    all_devices = DeviceService.get_all(db)
    devices = [d for d in all_devices if not SessionService.get_active_session(db, d.id)]
    projects = ProjectService.get_all(db)
    return HTMLResponse(_render('sessions/form.html', current_user=current_user, active_page='sessions', session=None, devices=devices, projects=projects))


@dashboard_router.get('/sessions/{session_id}/edit')
def sessions_edit_page(
    session_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    session = SessionService.get_by_id(db, session_id)
    devices = DeviceService.get_all(db)
    projects = ProjectService.get_all(db)
    return HTMLResponse(_render('sessions/form.html', current_user=current_user, active_page='sessions', session=session, devices=devices, projects=projects))


@dashboard_router.get('/projects')
def projects_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('projects/index.html', current_user=current_user, active_page='projects'))


@dashboard_router.get('/measurements')
def measurements_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('measurements/index.html', current_user=current_user, active_page='measurements'))


@dashboard_router.get('/benchmark')
def benchmark_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('benchmark/index.html', current_user=current_user, active_page='benchmark'))


@dashboard_router.get('/profile')
def profile_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('auth/profile.html', current_user=current_user, active_page='profile'))


@dashboard_router.get('/alerts')
def alerts_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('alerts/index.html', current_user=current_user, active_page='alerts'))


@dashboard_router.get('/settings')
def settings_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(_render('settings/index.html', current_user=current_user, active_page='settings'))
