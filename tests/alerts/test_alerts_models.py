from datetime import datetime, timezone

from src.alerts.models import Alert
from src.database import SessionLocal
from src.devices.models import Device


class TestAlertModel:
    def test_create_alert(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-alert-model')
        db.add(d)
        db.flush()
        a = Alert(device_id=d.id, level='warning', message='Test alert message')
        db.add(a)
        db.commit()
        assert a.id is not None
        assert a.device_id == d.id
        assert a.level == 'warning'
        assert a.message == 'Test alert message'
        db.close()

    def test_to_dict(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-alert-dict')
        db.add(d)
        db.flush()
        a = Alert(device_id=d.id, level='critical', message='Critical alert')
        db.add(a)
        db.commit()
        data = a.to_dict()
        assert data['id'] == a.id
        assert data['device_id'] == d.id
        assert data['device_name'] == 'esp32-alert-dict'
        assert data['level'] == 'critical'
        assert data['message'] == 'Critical alert'
        assert data['created_at'] is not None
        assert data['resolved_at'] is None
        db.close()

    def test_to_dict_resolved(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-alert-res')
        db.add(d)
        db.flush()
        a = Alert(device_id=d.id, level='info', message='Resolved',
                  resolved_at=datetime.now(timezone.utc))
        db.add(a)
        db.commit()
        data = a.to_dict()
        assert data['resolved_at'] is not None
        db.close()

    def test_repr(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-alert-repr')
        db.add(d)
        db.flush()
        a = Alert(device_id=d.id, level='warning', message='Short msg')
        assert repr(a) == '<Alert warning: Short msg>'
        db.close()

    def test_repr_long_message(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-alert-long')
        db.add(d)
        db.flush()
        long_msg = 'x' * 100
        a = Alert(device_id=d.id, level='critical', message=long_msg)
        assert len(repr(a)) < 80
        db.close()
