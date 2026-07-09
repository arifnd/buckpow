from datetime import datetime, timezone

from app import db
from app.models import Alert, Device


class TestAlertModel:
    def test_create_alert(self, app):
        with app.app_context():
            d = Device(device_id='esp32-alert-model')
            db.session.add(d)
            db.session.flush()
            a = Alert(device_id=d.id, level='warning', message='Test alert message')
            db.session.add(a)
            db.session.commit()
            assert a.id is not None
            assert a.device_id == d.id
            assert a.level == 'warning'
            assert a.message == 'Test alert message'

    def test_to_dict(self, app):
        with app.app_context():
            d = Device(device_id='esp32-alert-dict')
            db.session.add(d)
            db.session.flush()
            a = Alert(device_id=d.id, level='critical', message='Critical alert')
            db.session.add(a)
            db.session.commit()
            data = a.to_dict()
            assert data['id'] == a.id
            assert data['device_id'] == d.id
            assert data['device_name'] == 'esp32-alert-dict'
            assert data['level'] == 'critical'
            assert data['message'] == 'Critical alert'
            assert data['created_at'] is not None
            assert data['resolved_at'] is None

    def test_to_dict_resolved(self, app):
        with app.app_context():
            d = Device(device_id='esp32-alert-res')
            db.session.add(d)
            db.session.flush()
            a = Alert(device_id=d.id, level='info', message='Resolved',
                      resolved_at=datetime.now(timezone.utc))
            db.session.add(a)
            db.session.commit()
            data = a.to_dict()
            assert data['resolved_at'] is not None

    def test_repr(self, app):
        with app.app_context():
            d = Device(device_id='esp32-alert-repr')
            db.session.add(d)
            db.session.flush()
            a = Alert(device_id=d.id, level='warning', message='Short msg')
            assert repr(a) == '<Alert warning: Short msg>'

    def test_repr_long_message(self, app):
        with app.app_context():
            d = Device(device_id='esp32-alert-long')
            db.session.add(d)
            db.session.flush()
            long_msg = 'x' * 100
            a = Alert(device_id=d.id, level='critical', message=long_msg)
            assert len(repr(a)) < 80
