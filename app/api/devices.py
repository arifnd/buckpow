from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Device, User
from app.services.device_service import DeviceService
from app.auth import require_user

router = APIRouter()


class DeviceCreate(BaseModel):
    device_id: str
    alias: str = ''
    description: str = ''
    sampling_interval: int | None = None
    project_id: int | None = None
    firmware_version: str = ''
    high_current_threshold: float | None = None
    high_power_threshold: float | None = None
    low_voltage_threshold: float | None = None


class DeviceUpdate(BaseModel):
    alias: str | None = None
    description: str | None = None
    sampling_interval: int | None = None
    project_id: int | None = None
    firmware_version: str | None = None
    enabled: bool | None = None
    high_current_threshold: float | None = None
    high_power_threshold: float | None = None
    low_voltage_threshold: float | None = None


@router.get('/devices')
def list_devices(
    page: int = Query(1),
    per_page: int = Query(10),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    if page == 0:
        devices = DeviceService.get_all(db)
        return [d.to_dict() for d in devices]
    pagination = DeviceService.get_paginated(db, page=page, per_page=per_page)
    return {
        'devices': [d.to_dict() for d in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    }


@router.post('/devices', status_code=201)
def create_device(body: DeviceCreate, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    device = DeviceService.create(
        db,
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
    return device.to_dict()


@router.get('/devices/{device_id}')
def get_device(device_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    device = DeviceService.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    return device.to_dict()


@router.put('/devices/{device_id}')
def update_device(device_id: int, body: DeviceUpdate, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    kwargs = {}
    for key in ('alias', 'description', 'sampling_interval', 'project_id', 'firmware_version',
                'high_current_threshold', 'high_power_threshold', 'low_voltage_threshold'):
        val = getattr(body, key, None)
        if val is not None:
            kwargs[key] = val
    if body.enabled is not None:
        kwargs['enabled'] = body.enabled
    device = DeviceService.update(db, device_id, **kwargs)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    return device.to_dict()


@router.get('/devices/{device_id}/key')
def get_device_key(device_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    device = db.get(Device, device_id)
    if not device or not device.api_key:
        raise HTTPException(status_code=404, detail='Device not found or no API key')
    return {'api_key': device.api_key, 'id': device.id}


@router.patch('/devices/{device_id}/toggle')
def toggle_device(device_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    device = DeviceService.toggle_enabled(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    return device.to_dict()


@router.post('/devices/{device_id}/regenerate-key')
def regenerate_key(device_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    device = DeviceService.regenerate_api_key(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    return {'api_key': device.api_key, 'id': device.id}


@router.delete('/devices/{device_id}')
def delete_device(device_id: int, db: Session = Depends(get_db), _current_user: User = Depends(require_user)):
    if DeviceService.delete(db, device_id):
        return {'status': 'deleted'}
    raise HTTPException(status_code=404, detail='Device not found')
