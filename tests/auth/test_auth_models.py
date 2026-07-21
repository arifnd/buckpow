from src.database import SessionLocal
from src.models import User


class TestUserModel:
    def test_create_user(self, app):
        db = SessionLocal()
        u = User(name='Test User', email='test@example.com')
        u.set_password('secret123')
        db.add(u)
        db.commit()
        assert u.id is not None
        assert u.name == 'Test User'
        assert u.email == 'test@example.com'
        db.close()

    def test_set_password(self, app):
        db = SessionLocal()
        u = User(name='PW', email='pw@example.com')
        u.set_password('mypassword')
        assert u.password != 'mypassword'
        assert len(u.password) > 20
        db.close()

    def test_check_password_correct(self, app):
        db = SessionLocal()
        u = User(name='Check', email='check@example.com')
        u.set_password('correct')
        db.add(u)
        db.commit()
        assert u.check_password('correct') is True
        db.close()

    def test_check_password_incorrect(self, app):
        db = SessionLocal()
        u = User(name='Check2', email='check2@example.com')
        u.set_password('correct')
        assert u.check_password('wrong') is False
        db.close()

    def test_to_dict(self, app):
        db = SessionLocal()
        u = User(name='Dict', email='dict@example.com')
        u.set_password('x')
        db.add(u)
        db.commit()
        data = u.to_dict()
        assert data['id'] == u.id
        assert data['name'] == 'Dict'
        assert data['email'] == 'dict@example.com'
        assert 'password' not in data
        assert data['created_at'] is not None
        db.close()

    def test_repr(self, app):
        db = SessionLocal()
        u = User(name='Repr', email='repr@example.com')
        assert repr(u) == '<User repr@example.com>'
        db.close()

    def test_default_settings(self, app):
        db = SessionLocal()
        u = User(name='Settings', email='settings@example.com')
        u.set_password('x')
        db.add(u)
        db.commit()
        assert u.settings == {}
        db.close()
