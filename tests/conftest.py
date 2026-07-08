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


from app.models import Device, Measurement, Session


@pytest.fixture(autouse=True)
def reset_db():
    yield
    for m in [Measurement, Session, Device]:
        db.session.query(m).delete()
    db.session.commit()


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_device(app):
    with app.app_context():
        d = Device(device_id='esp32-test', alias='Test Device', sampling_interval=1)
        db.session.add(d)
        db.session.commit()
        return d


def pytest_unconfigure():
    shutil.rmtree(_tmp, ignore_errors=True)
