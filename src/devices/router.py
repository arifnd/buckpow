from fastapi import APIRouter, HTTPException, Query, Request

from src.audit.service import AuditService
from src.dependencies import DbDep, RequiredUserDep
from src.devices.models import Device
from src.devices.schemas import DeviceCreate, DeviceUpdate
from src.devices.service import DeviceService
from src.projects.models import Project
from src.utils.client_ip import get_client_ip

router = APIRouter()


def _check_device_owner(db, device_id, user_id):
    device = db.get(Device, device_id)
    if not device or not device.project_id:
        return True
    project = db.get(Project, device.project_id)
    if project and project.owner_id and project.owner_id != user_id:
        return False
    return True


@router.get("/devices")
def list_devices(
    db: DbDep,
    _current_user: RequiredUserDep,
    page: int = Query(1),
    per_page: int = Query(10),
):
    if page == 0:
        devices = DeviceService(db).get_all()
        return [d.to_dict() for d in devices]
    pagination = DeviceService(db).get_paginated(page=page, per_page=per_page)
    return {
        "devices": [d.to_dict() for d in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
    }


@router.post("/devices", status_code=201)
def create_device(
    body: DeviceCreate,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    device = DeviceService(db).create(
        device_id=body.device_id,
        alias=body.alias,
        description=body.description,
        sampling_interval=body.sampling_interval,
        project_id=body.project_id,
        firmware_version=body.firmware_version,
        high_current_threshold=body.high_current_threshold,
        high_power_threshold=body.high_power_threshold,
        low_voltage_threshold=body.low_voltage_threshold,
    )
    ip = get_client_ip(request)
    AuditService(db).log(
        "device.create",
        user_id=_current_user.id,
        target_type="device",
        target_id=device.id,
        ip_address=ip,
    )
    return device.to_dict()


@router.get("/devices/{device_id}")
def get_device(
    device_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    device = DeviceService(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device.to_dict()


@router.put("/devices/{device_id}")
def update_device(
    device_id: int,
    body: DeviceUpdate,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if not _check_device_owner(db, device_id, _current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this device"
        )
    kwargs = {}
    for key in (
        "alias",
        "description",
        "sampling_interval",
        "project_id",
        "firmware_version",
        "high_current_threshold",
        "high_power_threshold",
        "low_voltage_threshold",
    ):
        val = getattr(body, key, None)
        if val is not None:
            kwargs[key] = val
    if body.enabled is not None:
        kwargs["enabled"] = body.enabled
    device = DeviceService(db).update(device_id, **kwargs)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = get_client_ip(request)
    AuditService(db).log(
        "device.update",
        user_id=_current_user.id,
        target_type="device",
        target_id=device_id,
        ip_address=ip,
    )
    return device.to_dict()


@router.get("/devices/{device_id}/key")
def get_device_key(
    device_id: int,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    device = db.get(Device, device_id)
    if not device or not device.api_key:
        raise HTTPException(status_code=404, detail="Device not found or no API key")
    return {"api_key": device.api_key, "id": device.id}


@router.patch("/devices/{device_id}/toggle")
def toggle_device(
    device_id: int,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if not _check_device_owner(db, device_id, _current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to toggle this device"
        )
    device = DeviceService(db).toggle_enabled(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = get_client_ip(request)
    AuditService(db).log(
        f"device.{'enable' if device.enabled else 'disable'}",
        user_id=_current_user.id,
        target_type="device",
        target_id=device_id,
        ip_address=ip,
    )
    return device.to_dict()


@router.post("/devices/{device_id}/regenerate-key")
def regenerate_key(
    device_id: int,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if not _check_device_owner(db, device_id, _current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to regenerate key for this device"
        )
    device = DeviceService(db).regenerate_api_key(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = get_client_ip(request)
    AuditService(db).log(
        "api_key.regenerate",
        user_id=_current_user.id,
        target_type="device",
        target_id=device_id,
        ip_address=ip,
    )
    return {"api_key": device.api_key, "id": device.id}


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: int,
    request: Request,
    db: DbDep,
    _current_user: RequiredUserDep,
):
    if not _check_device_owner(db, device_id, _current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this device"
        )
    if DeviceService(db).delete(device_id):
        ip = get_client_ip(request)
        AuditService(db).log(
            "device.delete",
            user_id=_current_user.id,
            target_type="device",
            target_id=device_id,
            ip_address=ip,
        )
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Device not found")
