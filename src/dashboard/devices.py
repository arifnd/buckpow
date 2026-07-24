from fastapi import APIRouter

from src.dependencies import CurrentUserDep, DbDep
from src.template_helpers import _render_or_redirect
from src.devices.service import DeviceService
from src.projects.service import ProjectService

router = APIRouter()


@router.get("/devices")
def devices_page(current_user: CurrentUserDep):
    return _render_or_redirect("devices/index.html", current_user, "devices")


@router.get("/devices/new")
def devices_new_page(
    current_user: CurrentUserDep,
    db: DbDep,
):
    redir = _render_or_redirect(
        "devices/form.html",
        current_user,
        "devices",
        device=None,
        projects=ProjectService(db).get_all(),
    )
    return redir


@router.get("/devices/{device_id}/edit")
def devices_edit_page(
    device_id: int,
    current_user: CurrentUserDep,
    db: DbDep,
):
    device = DeviceService(db).get_by_id(device_id)
    return _render_or_redirect(
        "devices/form.html",
        current_user,
        "devices",
        device=device,
        projects=ProjectService(db).get_all(),
    )
