from app import db
from app.models import Project, User, Device, Session


class TestProjectModel:
    def test_create_project(self, app):
        with app.app_context():
            user = User.query.first()
            p = Project(name='Test Project', description='A project', owner_id=user.id)
            db.session.add(p)
            db.session.commit()
            assert p.id is not None
            assert p.name == 'Test Project'

    def test_to_dict(self, app):
        with app.app_context():
            user = User.query.first()
            p = Project(name='Dict Proj', description='Desc', owner_id=user.id)
            db.session.add(p)
            db.session.commit()
            data = p.to_dict()
            assert data['id'] == p.id
            assert data['name'] == 'Dict Proj'
            assert data['description'] == 'Desc'
            assert data['owner_id'] == user.id
            assert data['owner_name'] == 'Admin'
            assert data['device_count'] == 0
            assert data['session_count'] == 0
            assert data['created_at'] is not None

    def test_to_dict_with_devices_and_sessions(self, app):
        with app.app_context():
            user = User.query.first()
            p = Project(name='Full Proj', owner_id=user.id)
            db.session.add(p)
            db.session.flush()
            d = Device(device_id='esp32-proj', project_id=p.id)
            db.session.add(d)
            db.session.flush()
            s = Session(device_id=d.id, name='Proj Session', project_id=p.id)
            db.session.add(s)
            db.session.commit()
            data = p.to_dict()
            assert data['device_count'] == 1
            assert data['session_count'] == 1

    def test_repr(self, app):
        with app.app_context():
            p = Project(name='My Project')
            assert repr(p) == '<Project My Project>'

    def test_to_dict_no_owner(self, app):
        with app.app_context():
            p = Project(name='No Owner')
            db.session.add(p)
            db.session.commit()
            data = p.to_dict()
            assert data['owner_name'] is None

    def test_description_default_empty(self, app):
        with app.app_context():
            p = Project(name='No Desc')
            db.session.add(p)
            db.session.commit()
            assert p.description == ''
