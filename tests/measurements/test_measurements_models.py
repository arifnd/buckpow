from datetime import datetime, timezone, timedelta

from src.database import SessionLocal
from src.models import Device, Session, Measurement
from src.utils.calculations import calc_load_voltage, calc_energy_increment

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

    def test_measurement_created_at_is_recent(self, app):
        db = SessionLocal()
        d = Device(device_id='esp32-meas-ts')
        db.add(d)
        db.flush()
        before = datetime.now(timezone.utc)
        m = Measurement(device_id=d.id, bus_voltage=5.0, shunt_voltage=80.0,
                        load_voltage=5.08, current=0.24, power=1.2)
        db.add(m)
        db.commit()
        after = datetime.now(timezone.utc)
        assert before <= m.created_at.replace(tzinfo=timezone.utc) <= after
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


