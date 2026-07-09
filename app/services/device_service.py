from datetime import datetime, timezone, timedelta

from app import db
from app.models import Device
from app.config import Config


class DeviceService:

    @staticmethod
    def get_all():
        return Device.query.order_by(Device.created_at.desc()).all()

    @staticmethod
    def get_paginated(page=1, per_page=10):
        q = Device.query.order_by(Device.created_at.desc())
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(device_id):
        return db.session.get(Device, device_id)

    @staticmethod
    def get_by_device_id(device_id_str):
        return Device.query.filter_by(device_id=device_id_str).first()

    @staticmethod
    def create(device_id, alias='', description='', sampling_interval=None):
        device = Device(
            device_id=device_id,
            alias=alias,
            description=description,
            sampling_interval=sampling_interval or Config.DEFAULT_SAMPLING_INTERVAL,
            status='offline',
        )
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def update(device_id, **kwargs):
        device = db.session.get(Device, device_id)
        if not device:
            return None
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        db.session.commit()
        return device

    @staticmethod
    def delete(device_id):
        device = db.session.get(Device, device_id)
        if not device:
            return False
        db.session.delete(device)
        db.session.commit()
        return True

    @staticmethod
    def touch(device_id_str):
        device = DeviceService.get_by_device_id(device_id_str)
        if not device:
            return None
        device.last_seen = datetime.now(timezone.utc)
        device.status = 'online'
        db.session.commit()
        return device

    @staticmethod
    def get_online_status(device):
        if not device or not device.last_seen:
            return 'offline'
        last_seen = device.last_seen
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last_seen < timedelta(seconds=Config.DEVICE_ONLINE_TIMEOUT):
            return 'online'
        return 'offline'

    @staticmethod
    def get_or_create(device_id_str, alias='', description='', sampling_interval=None):
        device = DeviceService.get_by_device_id(device_id_str)
        if not device:
            device = DeviceService.create(device_id_str, alias, description, sampling_interval)
        return device
