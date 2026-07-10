import os
import sys
import shutil
import tempfile

import pytest

# Must set DB path before any app imports
_tmp = tempfile.mkdtemp()
os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(_tmp, "test.db")}'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# These imports trigger app init, must come after env var is set
from app.database import engine, Base, SessionLocal, get_db
from app.config import settings
from app.models import Device, Measurement, Session, User, Project, Alert
from app.services.user_service import UserService
from app.services.device_service import DeviceService
from app.services.project_service import ProjectService
from app.services.alert_service import AlertService
from app.auth import create_access_token
from app import app as fastapi_app


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    yield
    try:
        db = SessionLocal()
        for m in [Alert, Measurement, Session, Device, Project, User]:
            db.query(m).delete()
        db.commit()
        db.close()
    except RuntimeError:
        pass


@pytest.fixture
def app():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).first():
        UserService.create(db, name='Admin', email='admin@example.com', password='password')
    db.close()
    return fastapi_app


@pytest.fixture
def client(app):
    db = SessionLocal()
    user = db.query(User).first()
    token = create_access_token(data={'sub': user.id})
    db.close()
    client = TestClient(app)
    client.headers.update({'Authorization': f'Bearer {token}'})
    return client


@pytest.fixture
def unauth_client(app):
    return TestClient(app)


@pytest.fixture
def sample_device(app):
    db = SessionLocal()
    d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    result = {'id': d.id, 'device_id': d.device_id, 'api_key': d.api_key}
    db.close()
    return result


@pytest.fixture
def sample_device_id(app):
    db = SessionLocal()
    d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    result = d.id
    db.close()
    return result


@pytest.fixture
def device_auth_header(app):
    db = SessionLocal()
    d = Device(device_id='esp32-auth', alias='Auth Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    key = d.api_key
    db.close()
    return {'Authorization': f'Bearer {key}'}


@pytest.fixture
def sample_project(app):
    db = SessionLocal()
    user = db.query(User).first()
    p = ProjectService.create(db, name='Test Project', description='A test project', owner_id=user.id)
    result = {'id': p.id, 'name': p.name}
    db.close()
    return result


@pytest.fixture
def sample_alert(app, sample_device_id):
    db = SessionLocal()
    alert = AlertService.create(db, device_id=sample_device_id, level='warning', message='Test alert')
    result = {'id': alert.id, 'device_id': alert.device_id}
    db.close()
    return result


def pytest_unconfigure():
    shutil.rmtree(_tmp, ignore_errors=True)
