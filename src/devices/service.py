import secrets
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session, selectinload

from src.devices.models import Device
from src.config import settings
from src.utils.pagination import PaginatedResult


class DeviceService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Device).options(selectinload(Device.project)).order_by(Device.created_at.desc()).all()

    def get_paginated(self, page=1, per_page=10):
        q = self.db.query(Device).options(selectinload(Device.project)).order_by(Device.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)

    def get_by_id(self, device_id):
        return self.db.get(Device, device_id)

    def get_by_device_id(self, device_id_str):
        return self.db.query(Device).filter_by(device_id=device_id_str).first()

    def get_by_api_key(self, api_key):
        return self.db.query(Device).filter_by(api_key=api_key).first()

    def regenerate_api_key(self, device_id):
        device = self.db.get(Device, device_id)
        if not device:
            return None
        device.api_key = self.generate_api_key()
        self.db.commit()
        return device

    @staticmethod
    def generate_api_key():
        return secrets.token_hex(32)

    def create(self, device_id, alias='', description='', sampling_interval=None, project_id=None, firmware_version='',
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
            api_key=self.generate_api_key(),
            high_current_threshold=high_current_threshold,
            high_power_threshold=high_power_threshold,
            low_voltage_threshold=low_voltage_threshold,
        )
        self.db.add(device)
        self.db.commit()
        return device

    def update(self, device_id, **kwargs):
        device = self.db.get(Device, device_id)
        if not device:
            return None
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        self.db.commit()
        return device

    def toggle_enabled(self, device_id):
        device = self.db.get(Device, device_id)
        if not device:
            return None
        device.enabled = not device.enabled
        self.db.commit()
        return device

    def delete(self, device_id):
        device = self.db.get(Device, device_id)
        if not device:
            return False
        self.db.delete(device)
        self.db.commit()
        return True

    def touch(self, device_id_str):
        device = self.get_by_device_id(device_id_str)
        if not device:
            return None
        device.last_seen = datetime.now(timezone.utc)
        device.status = 'online'
        self.db.commit()
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

    def get_or_create(self, device_id_str, alias='', description='', sampling_interval=None):
        device = self.get_by_device_id(device_id_str)
        if not device:
            device = self.create(device_id_str, alias, description, sampling_interval)
        return device