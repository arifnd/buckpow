import secrets
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session, selectinload

from app.models import Device
from app.config import settings


class DeviceService:

    @staticmethod
    def get_all(db: Session):
        return db.query(Device).options(selectinload(Device.project)).order_by(Device.created_at.desc()).all()

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10):
        q = db.query(Device).options(selectinload(Device.project)).order_by(Device.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return type('Pagination', (), {'items': items, 'page': page, 'pages': pages, 'total': total, 'per_page': per_page})()

    @staticmethod
    def get_by_id(db: Session, device_id):
        return db.get(Device, device_id)

    @staticmethod
    def get_by_device_id(db: Session, device_id_str):
        return db.query(Device).filter_by(device_id=device_id_str).first()

    @staticmethod
    def get_by_api_key(db: Session, api_key):
        return db.query(Device).filter_by(api_key=api_key).first()

    @staticmethod
    def regenerate_api_key(db: Session, device_id):
        device = db.get(Device, device_id)
        if not device:
            return None
        device.api_key = DeviceService.generate_api_key()
        db.commit()
        return device

    @staticmethod
    def generate_api_key():
        return secrets.token_hex(32)

    @staticmethod
    def create(db: Session, device_id, alias='', description='', sampling_interval=None, project_id=None, firmware_version='',
               high_current_threshold=None, high_power_threshold=None, low_voltage_threshold=None):
        device = Device(
            device_id=device_id,
            alias=alias,
            description=description,
            sampling_interval=sampling_interval or settings.DEFAULT_SAMPLING_INTERVAL,
            status='offline',
            enabled=True,
            firmware_version=firmware_version,
            project_id=project_id,
            api_key=DeviceService.generate_api_key(),
            high_current_threshold=high_current_threshold,
            high_power_threshold=high_power_threshold,
            low_voltage_threshold=low_voltage_threshold,
        )
        db.add(device)
        db.commit()
        return device

    @staticmethod
    def update(db: Session, device_id, **kwargs):
        device = db.get(Device, device_id)
        if not device:
            return None
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        db.commit()
        return device

    @staticmethod
    def toggle_enabled(db: Session, device_id):
        device = db.get(Device, device_id)
        if not device:
            return None
        device.enabled = not device.enabled
        db.commit()
        return device

    @staticmethod
    def delete(db: Session, device_id):
        device = db.get(Device, device_id)
        if not device:
            return False
        db.delete(device)
        db.commit()
        return True

    @staticmethod
    def touch(db: Session, device_id_str):
        device = DeviceService.get_by_device_id(db, device_id_str)
        if not device:
            return None
        device.last_seen = datetime.now(timezone.utc)
        device.status = 'online'
        db.commit()
        return device

    @staticmethod
    def get_online_status(device):
        if not device or not device.last_seen:
            return 'offline'
        last_seen = device.last_seen
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last_seen < timedelta(seconds=settings.DEVICE_ONLINE_TIMEOUT):
            return 'online'
        return 'offline'

    @staticmethod
    def get_or_create(db: Session, device_id_str, alias='', description='', sampling_interval=None):
        device = DeviceService.get_by_device_id(db, device_id_str)
        if not device:
            device = DeviceService.create(db, device_id_str, alias, description, sampling_interval)
        return device
