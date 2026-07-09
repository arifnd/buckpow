import os
import sys
import shutil
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_tmp = tempfile.mkdtemp()
os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(_tmp, "test.db")}'

from app import create_app, db
from app.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(_tmp, "test.db")}'
    DEBUG = False
    SECRET_KEY = 'test-secret'
    WTF_CSRF_ENABLED = False


from app.models import Device, Measurement, Session, User, Project, Alert
from app.services.user_service import UserService
from app.services.device_service import DeviceService
from app.services.project_service import ProjectService
from app.services.alert_service import AlertService


@pytest.fixture(autouse=True)
def reset_db():
    yield
    try:
        for m in [Alert, Measurement, Session, Device, Project, User]:
            db.session.query(m).delete()
        db.session.commit()
    except RuntimeError:
        pass


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        db.session.expire_on_commit = False
        if not User.query.first():
            UserService.create(name='Admin', email='admin@example.com', password='password')
    return app


@pytest.fixture
def client(app):
    client = app.test_client()
    client.post('/api/v1/auth/login', json={
        'email': 'admin@example.com',
        'password': 'password',
    })
    return client


@pytest.fixture
def unauth_client(app):
    return app.test_client()


@pytest.fixture
def sample_device(app):
    with app.app_context():
        d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
                   api_key=DeviceService.generate_api_key())
        db.session.add(d)
        db.session.commit()
        return {'id': d.id, 'device_id': d.device_id, 'api_key': d.api_key}


@pytest.fixture
def sample_device_id(app):
    with app.app_context():
        d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1,
                   api_key=DeviceService.generate_api_key())
        db.session.add(d)
        db.session.commit()
        return d.id


@pytest.fixture
def device_auth_header(app):
    with app.app_context():
        d = Device(device_id='esp32-auth', alias='Auth Device', sampling_interval=1,
                   api_key=DeviceService.generate_api_key())
        db.session.add(d)
        db.session.commit()
        key = d.api_key
    return {'Authorization': f'Bearer {key}'}


@pytest.fixture
def sample_project(app):
    with app.app_context():
        user = User.query.first()
        p = ProjectService.create(name='Test Project', description='A test project', owner_id=user.id)
        return {'id': p.id, 'name': p.name}


@pytest.fixture
def sample_alert(app, sample_device_id):
    with app.app_context():
        alert = AlertService.create(device_id=sample_device_id, level='warning', message='Test alert')
        return {'id': alert.id, 'device_id': alert.device_id}


def pytest_unconfigure():
    shutil.rmtree(_tmp, ignore_errors=True)
