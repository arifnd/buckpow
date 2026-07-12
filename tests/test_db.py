from sqlalchemy import inspect
from app.database import SessionLocal, engine
from app.models import Device, Session, Measurement, User, Project, Alert


def test_init_db_creates_tables(app):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert 'devices' in tables
    assert 'sessions' in tables
    assert 'measurements' in tables
    assert 'users' in tables
    assert 'projects' in tables
    assert 'alerts' in tables
    assert 'audit_logs' in tables


def test_create_device(app):
    db = SessionLocal()
    d = Device(device_id='test-device', alias='Test', sampling_interval=1)
    db.add(d)
    db.commit()
    assert d.id is not None
    assert d.status == 'offline'
    db.close()


def test_create_session(app):
    db = SessionLocal()
    d = Device(device_id='test-device', alias='Test', sampling_interval=1)
    db.add(d)
    db.commit()

    s = Session(device_id=d.id, name='Test Session', status='draft')
    db.add(s)
    db.commit()
    assert s.id is not None
    db.close()


def test_create_measurement(app):
    db = SessionLocal()
    d = Device(device_id='test-device', alias='Test', sampling_interval=1)
    db.add(d)
    db.commit()

    m = Measurement(
        device_id=d.id, bus_voltage=5.0, shunt_voltage=80.0,
        load_voltage=5.08, current=0.24, power=1.2
    )
    db.add(m)
    db.commit()
    assert m.id is not None
    assert m.load_voltage == 5.08
    db.close()


def test_device_relationships(app):
    db = SessionLocal()
    d = Device(device_id='test-device', alias='Test', sampling_interval=1)
    db.add(d)
    db.commit()

    s = Session(device_id=d.id, name='Test Session', status='running')
    db.add(s)
    db.flush()

    m = Measurement(
        device_id=d.id, session_id=s.id, bus_voltage=5.0,
        shunt_voltage=80.0, load_voltage=5.08, current=0.24, power=1.2
    )
    db.add(m)
    db.commit()

    assert len(d.sessions.all()) == 1
    assert len(d.measurements.all()) == 1
    assert db.query(Measurement).filter_by(session_id=s.id).count() == 1
    db.close()
