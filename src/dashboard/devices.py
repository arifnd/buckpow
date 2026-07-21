from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_db
from src.models import User
from src.template_helpers import _render_or_redirect
from src.devices.service import DeviceService
from src.projects.service import ProjectService

router = APIRouter()


@router.get('/devices')
def devices_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect('devices/index.html', current_user, 'devices')


@router.get('/devices/new')
def devices_new_page(
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    redir = _render_or_redirect('devices/form.html', current_user, 'devices', device=None, projects=ProjectService(db).get_all())
    return redir


@router.get('/devices/{device_id}/edit')
def devices_edit_page(
    device_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    device = DeviceService(db).get_by_id(device_id)
    return _render_or_redirect('devices/form.html', current_user, 'devices', device=device, projects=ProjectService(db).get_all())
