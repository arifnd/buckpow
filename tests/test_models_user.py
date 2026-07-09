from app import db
from app.models import User


class TestUserModel:
    def test_create_user(self, app):
        with app.app_context():
            u = User(name='Test User', email='test@example.com')
            u.set_password('secret123')
            db.session.add(u)
            db.session.commit()
            assert u.id is not None
            assert u.name == 'Test User'
            assert u.email == 'test@example.com'

    def test_set_password(self, app):
        with app.app_context():
            u = User(name='PW', email='pw@example.com')
            u.set_password('mypassword')
            assert u.password != 'mypassword'
            assert len(u.password) > 20

    def test_check_password_correct(self, app):
        with app.app_context():
            u = User(name='Check', email='check@example.com')
            u.set_password('correct')
            db.session.add(u)
            db.session.commit()
            assert u.check_password('correct') is True

    def test_check_password_incorrect(self, app):
        with app.app_context():
            u = User(name='Check2', email='check2@example.com')
            u.set_password('correct')
            assert u.check_password('wrong') is False

    def test_to_dict(self, app):
        with app.app_context():
            u = User(name='Dict', email='dict@example.com')
            u.set_password('x')
            db.session.add(u)
            db.session.commit()
            data = u.to_dict()
            assert data['id'] == u.id
            assert data['name'] == 'Dict'
            assert data['email'] == 'dict@example.com'
            assert 'password' not in data
            assert data['created_at'] is not None

    def test_repr(self, app):
        with app.app_context():
            u = User(name='Repr', email='repr@example.com')
            assert repr(u) == '<User repr@example.com>'

    def test_default_settings(self, app):
        with app.app_context():
            u = User(name='Settings', email='settings@example.com')
            u.set_password('x')
            db.session.add(u)
            db.session.commit()
            assert u.settings == {}
