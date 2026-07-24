


from src.auth.service import UserService
from src.database import SessionLocal


class TestUserService:

    def _db(self, app):

        return SessionLocal()



    def test_create_user(self, app):

        db = self._db(app)

        u = UserService(db).create(name='Test', email='test@example.com', password='secret')

        assert u.id is not None

        assert u.name == 'Test'

        assert u.email == 'test@example.com'

        assert u.check_password('secret')

        db.close()



    def test_create_duplicate_email(self, app):

        import pytest

        db = self._db(app)

        UserService(db).create(name='A', email='dup@example.com', password='x')

        with pytest.raises(ValueError, match='already exists'):

            UserService(db).create(name='B', email='dup@example.com', password='y')

        db.close()



    def test_authenticate_success(self, app):

        db = self._db(app)

        UserService(db).create(name='Auth', email='auth@example.com', password='pass')

        u = UserService(db).authenticate('auth@example.com', 'pass')

        assert u is not None

        assert u.name == 'Auth'

        db.close()



    def test_authenticate_wrong_password(self, app):

        db = self._db(app)

        UserService(db).create(name='Auth', email='auth2@example.com', password='pass')

        u = UserService(db).authenticate('auth2@example.com', 'wrong')

        assert u is None

        db.close()



    def test_authenticate_nonexistent(self, app):

        db = self._db(app)

        u = UserService(db).authenticate('nobody@example.com', 'pass')

        assert u is None

        db.close()



    def test_update_user(self, app):

        db = self._db(app)

        u = UserService(db).create(name='Old', email='old@example.com', password='x')

        updated = UserService(db).update(u.id, name='New', email='new@example.com')

        assert updated.name == 'New'

        assert updated.email == 'new@example.com'

        db.close()



    def test_update_email_already_in_use(self, app):

        import pytest

        db = self._db(app)

        UserService(db).create(name='A', email='a@example.com', password='x')

        b = UserService(db).create(name='B', email='b@example.com', password='x')

        with pytest.raises(ValueError, match='already in use'):

            UserService(db).update(b.id, email='a@example.com')

        db.close()



    def test_update_nonexistent(self, app):

        db = self._db(app)

        result = UserService(db).update(99999, name='Ghost')

        assert result is None

        db.close()



    def test_update_password(self, app):

        db = self._db(app)

        u = UserService(db).create(name='Pwd', email='pwd@example.com', password='old')

        UserService(db).update(u.id, password='new')

        assert u.check_password('new')

        db.close()



    def test_get_by_id(self, app):

        db = self._db(app)

        u = UserService(db).create(name='ByID', email='byid@example.com', password='x')

        found = UserService(db).get_by_id(u.id)

        assert found is not None

        assert found.email == 'byid@example.com'

        db.close()



    def test_get_by_email(self, app):

        db = self._db(app)

        UserService(db).create(name='ByEmail', email='byemail@example.com', password='x')

        found = UserService(db).get_by_email('byemail@example.com')

        assert found is not None

        db.close()





