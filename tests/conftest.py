import os

import pytest
import src.database as db_module
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src import app as fastapi_app
from src.alerts.models import Alert
from src.alerts.service import AlertService
from src.audit.models import AuditLog
from src.auth import create_access_token
from src.auth.models import User
from src.auth.service import UserService
from src.database import Base, get_db
from src.devices.models import Device
from src.devices.service import DeviceService
from src.measurements.models import Measurement
from src.projects.models import Project
from src.projects.service import ProjectService
from src.sessions.models import Session

# Override engine with in-memory SQLite + StaticPool for test isolation
db_module.engine = create_engine(
    'sqlite://',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_module.engine)


def override_get_db():
    db = db_module.SessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    yield
    try:
        db = db_module.SessionLocal()
        for m in [Alert, Measurement, Session, Device, Project, User, AuditLog]:
            db.query(m).delete()
        db.commit()
        db.close()
    except Exception:
        pass


@pytest.fixture
def app():
    Base.metadata.create_all(bind=db_module.engine)
    db = db_module.SessionLocal()
    if not db.query(User).first():
        UserService(db).create(name='Admin', email='admin@example.com', password='password')
    db.close()
    return fastapi_app


@pytest.fixture
def client(app):
    db = db_module.SessionLocal()
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
def db(app):
    session = db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_device(app):
    db = db_module.SessionLocal()
    d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    result = {'id': d.id, 'device_id': d.device_id, 'api_key': d.api_key}
    db.close()
    return result


@pytest.fixture
def sample_device_id(app):
    db = db_module.SessionLocal()
    d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    result = d.id
    db.close()
    return result


@pytest.fixture
def device_auth_header(app):
    db = db_module.SessionLocal()
    d = Device(device_id='esp32-auth', alias='Auth Device', sampling_interval=1,
               api_key=DeviceService.generate_api_key())
    db.add(d)
    db.commit()
    key = d.api_key
    db.close()
    return {'Authorization': f'Bearer {key}'}


@pytest.fixture
def sample_project(app):
    db = db_module.SessionLocal()
    user = db.query(User).first()
    p = ProjectService(db).create(name='Test Project', description='A test project', owner_id=user.id)
    result = {'id': p.id, 'name': p.name}
    db.close()
    return result


@pytest.fixture
def sample_alert(app, sample_device_id):
    db = db_module.SessionLocal()
    alert = AlertService(db).create(device_id=sample_device_id, level='warning', message='Test alert')
    result = {'id': alert.id, 'device_id': alert.device_id}
    db.close()
    return result


@pytest.fixture()
def file_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'test_buckpow.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    file_engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(bind=file_engine)
    file_engine.dispose()
    old_url = db_module.engine.url
    db_module.engine.url = create_engine(f'sqlite:///{db_path}').url
    try:
        yield db_path
    finally:
        db_module.engine.url = old_url
        if os.path.exists(db_path):
            os.remove(db_path)
