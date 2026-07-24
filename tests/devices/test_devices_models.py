from datetime import datetime, timedelta, timezone

from src.database import SessionLocal
from src.devices.models import Device


class TestDeviceModel:
    def test_to_dict(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-001', alias='Sensor', description='Room A',
                   sampling_interval=2, last_seen=datetime.now(timezone.utc))
        db.add(d)
        db.commit()
        data = d.to_dict()
        assert data['id'] == d.id
        assert data['device_id'] == 'esp32-001'
        assert data['alias'] == 'Sensor'
        assert data['description'] == 'Room A'
        assert data['sampling_interval'] == 2
        assert data['last_seen'] is not None
        assert data['status'] in ('online', 'offline')
        assert data['created_at'] is not None
        db.close()

    def test_to_dict_no_last_seen(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-offline')
        db.add(d)
        db.commit()
        data = d.to_dict()
        assert data['last_seen'] is None
        assert data['status'] == 'offline'
        db.close()

    def test_compute_status_offline_no_last_seen(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-no-seen')
        db.add(d)
        db.commit()
        assert d._compute_status() == 'offline'
        db.close()

    def test_compute_status_online_recent(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-recent',
                   last_seen=datetime.now(timezone.utc) - timedelta(seconds=5))
        db.add(d)
        db.commit()
        assert d._compute_status() == 'online'
        db.close()

    def test_compute_status_offline_expired(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-expired',
                   last_seen=datetime.now(timezone.utc) - timedelta(seconds=60))
        db.add(d)
        db.commit()
        assert d._compute_status() == 'offline'
        db.close()

    def test_compute_status_naive_datetime(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-naive',
                   last_seen=datetime.now() - timedelta(seconds=5))
        db.add(d)
        db.commit()
        assert d._compute_status() == 'online'
        db.close()

    def test_device_repr(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-repr')
        assert repr(d) == '<Device esp32-repr>'
        db.close()

    def test_created_at_is_recent(self, app):
        db = SessionLocal()
        before = datetime.now(timezone.utc)
        d = Device(device_id='esp32-ts-created')
        db.add(d)
        db.commit()
        after = datetime.now(timezone.utc)
        assert before <= d.created_at.replace(tzinfo=timezone.utc) <= after
        db.close()

    def test_updated_at_updates_on_change(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-ts-updated')
        db.add(d)
        db.commit()
        original = d.updated_at
        d.alias = 'Changed'
        db.commit()
        assert d.updated_at > original
        db.close()



