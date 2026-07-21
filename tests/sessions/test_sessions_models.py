from datetime import datetime, timezone, timedelta

from src.database import SessionLocal
from src.models import Device, Session, Measurement
from src.utils.calculations import calc_load_voltage, calc_energy_increment

class TestSessionModel:
    def test_to_dict(self, app):
        db = SessionLocal()
        device = Device(device_id='esp32-sess', alias='Session Device')
        db.add(device)
        db.flush()
        s = Session(device_id=device.id, name='Test', status='draft')
        db.add(s)
        db.commit()
        data = s.to_dict()
        assert data['id'] == s.id
        assert data['device_id'] == device.id
        assert data['device_name'] == 'Session Device'
        assert data['name'] == 'Test'
        assert data['status'] == 'draft'
        assert data['started_at'] is None
        assert data['ended_at'] is None
        db.close()

    def test_to_dict_device_name_fallback(self, app):
        db = SessionLocal()
        device = Device(device_id='esp32-noalias')
        db.add(device)
        db.flush()
        s = Session(device_id=device.id, name='Test')
        db.add(s)
        db.commit()
        data = s.to_dict()
        assert data['device_name'] == 'esp32-noalias'
        db.close()

    def test_to_dict_no_device(self, app):
        db = SessionLocal()
        s = Session(device_id=999, name='Orphan')
        db.add(s)
        db.commit()
        data = s.to_dict()
        assert data['device_name'] is None
        db.close()

    def test_to_dict_with_timestamps(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-ts')
        db.add(d)
        db.flush()
        now = datetime.now(timezone.utc)
        s = Session(device_id=d.id, name='Running', status='running',
                    started_at=now, ended_at=now + timedelta(hours=1))
        db.add(s)
        db.commit()
        data = s.to_dict()
        assert data['started_at'] is not None
        assert data['ended_at'] is not None
        assert data['status'] == 'running'
        db.close()

    def test_session_repr(self, app):
        db = SessionLocal()
        s = Session(device_id=1, name='My Session')
        assert repr(s) == '<Session My Session>'
        db.close()

    def test_session_created_at_is_recent(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-sess-ts')
        db.add(d)
        db.flush()
        before = datetime.now(timezone.utc)
        s = Session(device_id=d.id, name='TS Session')
        db.add(s)
        db.commit()
        after = datetime.now(timezone.utc)
        assert before <= s.created_at.replace(tzinfo=timezone.utc) <= after
        db.close()

    def test_session_updated_at_updates_on_change(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-sess-upd')
        db.add(d)
        db.flush()
        s = Session(device_id=d.id, name='Original')
        db.add(s)
        db.commit()
        original = s.updated_at
        s.name = 'Changed'
        db.commit()
        assert s.updated_at > original
        db.close()



