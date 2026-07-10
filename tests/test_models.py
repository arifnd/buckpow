from datetime import datetime, timezone, timedelta

from app.database import SessionLocal
from app.models import Device, Session, Measurement
from app.utils.calculations import calc_load_voltage, calc_energy_increment


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


class TestMeasurementModel:
    def test_to_dict(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-meas')
        db.add(d)
        db.flush()
        m = Measurement(device_id=d.id, bus_voltage=5.0, shunt_voltage=80.0,
                        load_voltage=5.08, current=0.24, power=1.2, energy=0.5)
        db.add(m)
        db.commit()
        data = m.to_dict()
        assert data['id'] == m.id
        assert data['device_id'] == d.id
        assert data['bus_voltage'] == 5.0
        assert data['shunt_voltage'] == 80.0
        assert data['load_voltage'] == 5.08
        assert data['current'] == 0.24
        assert data['power'] == 1.2
        assert data['energy'] == 0.5
        assert data['session_id'] is None
        assert data['session_name'] is None
        db.close()

    def test_to_dict_with_session(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-meas2')
        db.add(d)
        db.flush()
        s = Session(device_id=d.id, name='Meas Session')
        db.add(s)
        db.flush()
        m = Measurement(device_id=d.id, session_id=s.id,
                        bus_voltage=5.0, shunt_voltage=80.0,
                        load_voltage=5.08, current=0.24, power=1.2)
        db.add(m)
        db.commit()
        data = m.to_dict()
        assert data['session_id'] == s.id
        assert data['session_name'] == 'Meas Session'
        db.close()

    def test_to_dict_device_name(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-meas3', alias='My Sensor')
        db.add(d)
        db.flush()
        m = Measurement(device_id=d.id, bus_voltage=5.0, shunt_voltage=80.0,
                        load_voltage=5.08, current=0.24, power=1.2)
        db.add(m)
        db.commit()
        data = m.to_dict()
        assert data['device_name'] == 'My Sensor'
        db.close()

    def test_measurement_repr(self, app):
        db = SessionLocal()
        m = Measurement(device_id=1, bus_voltage=5.0, shunt_voltage=80.0,
                        load_voltage=5.08, current=0.24, power=1.2)
        assert repr(m) == '<Measurement None device=1>'
        db.close()


class TestCalculations:
    def test_calc_load_voltage(self):
        assert calc_load_voltage(5.0, 80.0) == 5.08
        assert calc_load_voltage(0, 0) == 0
        assert calc_load_voltage(12.0, 100) == 12.1

    def test_calc_energy_increment(self):
        assert calc_energy_increment(1.0, 1) == 1.0 / 3600
        assert calc_energy_increment(0, 60) == 0
        assert calc_energy_increment(100, 3600) == 100
