from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Project, User, Device, Session


class TestProjectModel:
    def test_create_project(self, app):
        db = SessionLocal()
        user = db.query(User).first()
        p = Project(name='Test Project', description='A project', owner_id=user.id)
        db.add(p)
        db.commit()
        assert p.id is not None
        assert p.name == 'Test Project'
        db.close()

    def test_to_dict(self, app):
        db = SessionLocal()
        user = db.query(User).first()
        p = Project(name='Dict Proj', description='Desc', owner_id=user.id)
        db.add(p)
        db.commit()
        data = p.to_dict()
        assert data['id'] == p.id
        assert data['name'] == 'Dict Proj'
        assert data['description'] == 'Desc'
        assert data['owner_id'] == user.id
        assert data['owner_name'] == 'Admin'
        assert data['device_count'] == 0
        assert data['session_count'] == 0
        assert data['created_at'] is not None
        db.close()

    def test_to_dict_with_devices_and_sessions(self, app):
        db = SessionLocal()
        user = db.query(User).first()
        p = Project(name='Full Proj', owner_id=user.id)
        db.add(p)
        db.flush()
        d = Device(device_id='esp32-proj', project_id=p.id)
        db.add(d)
        db.flush()
        s = Session(device_id=d.id, name='Proj Session', project_id=p.id)
        db.add(s)
        db.commit()
        data = p.to_dict()
        assert data['device_count'] == 1
        assert data['session_count'] == 1
        db.close()

    def test_repr(self, app):
        db = SessionLocal()
        p = Project(name='My Project')
        assert repr(p) == '<Project My Project>'
        db.close()

    def test_to_dict_no_owner(self, app):
        db = SessionLocal()
        p = Project(name='No Owner')
        db.add(p)
        db.commit()
        data = p.to_dict()
        assert data['owner_name'] is None
        db.close()

    def test_description_default_empty(self, app):
        db = SessionLocal()
        p = Project(name='No Desc')
        db.add(p)
        db.commit()
        assert p.description == ''
        db.close()

    def test_created_at_is_recent(self, app):
        db = SessionLocal()
        before = datetime.now(timezone.utc)
        p = Project(name='TS Project')
        db.add(p)
        db.commit()
        after = datetime.now(timezone.utc)
        assert before <= p.created_at.replace(tzinfo=timezone.utc) <= after
        db.close()

    def test_updated_at_updates_on_change(self, app):
        db = SessionLocal()
        p = Project(name='TS Update')
        db.add(p)
        db.commit()
        original = p.updated_at
        p.name = 'Changed'
        db.commit()
        assert p.updated_at > original
        db.close()
