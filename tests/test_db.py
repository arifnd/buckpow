from sqlalchemy import inspect
from app import db
from app.models import Device, Session, Measurement


def test_init_db_creates_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert 'devices' in tables
        assert 'sessions' in tables
        assert 'measurements' in tables


def test_create_device(app):
    with app.app_context():
        d = Device(device_id='test-device', alias='Test', sampling_interval=1)
        db.session.add(d)
        db.session.commit()
        assert d.id is not None
        assert d.status == 'offline'


def test_create_session(app):
    with app.app_context():
        d = Device(device_id='test-device', alias='Test', sampling_interval=1)
        db.session.add(d)
        db.session.commit()

        s = Session(device_id=d.id, name='Test Session', status='draft')
        db.session.add(s)
        db.session.commit()
        assert s.id is not None


def test_create_measurement(app):
    with app.app_context():
        d = Device(device_id='test-device', alias='Test', sampling_interval=1)
        db.session.add(d)
        db.session.commit()

        m = Measurement(
            device_id=d.id, bus_voltage=5.0, shunt_voltage=80.0,
            load_voltage=5.08, current=0.24, power=1.2
        )
        db.session.add(m)
        db.session.commit()
        assert m.id is not None
        assert m.load_voltage == 5.08


def test_device_relationships(app):
    with app.app_context():
        d = Device(device_id='test-device', alias='Test', sampling_interval=1)
        db.session.add(d)
        db.session.commit()

        s = Session(device_id=d.id, name='Test Session', status='running')
        db.session.add(s)
        db.session.flush()

        m = Measurement(
            device_id=d.id, session_id=s.id, bus_voltage=5.0,
            shunt_voltage=80.0, load_voltage=5.08, current=0.24, power=1.2
        )
        db.session.add(m)
        db.session.commit()

        assert len(d.sessions.all()) == 1
        assert len(d.measurements.all()) == 1
        assert Measurement.query.filter_by(session_id=s.id).count() == 1
