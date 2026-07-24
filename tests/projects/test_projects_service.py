


from src.auth.models import User
from src.database import SessionLocal
from src.projects.models import Project
from src.projects.service import ProjectService


class TestProjectService:

    def _db(self, app):

        return SessionLocal()



    def test_create_project(self, app):

        db = self._db(app)

        p = ProjectService(db).create(name='Test Project', description='Desc')

        assert p.id is not None

        assert p.name == 'Test Project'

        db.close()



    def test_create_with_owner(self, app):

        db = self._db(app)

        user = db.query(User).first()

        p = ProjectService(db).create(name='Owned', owner_id=user.id)

        assert p.owner_id == user.id

        db.close()



    def test_get_by_id(self, app):

        db = self._db(app)

        p = ProjectService(db).create(name='Find Me')

        found = ProjectService(db).get_by_id(p.id)

        assert found is not None

        db.close()



    def test_get_by_id_nonexistent(self, app):

        db = self._db(app)

        p = ProjectService(db).get_by_id(99999)

        assert p is None

        db.close()



    def test_get_all(self, app):

        db = self._db(app)

        ProjectService(db).create(name='A')

        ProjectService(db).create(name='B')

        assert len(ProjectService(db).get_all()) >= 2

        db.close()



    def test_get_paginated(self, app):

        from sqlalchemy import insert


        db = self._db(app)

        db.execute(insert(Project), [{'name': f'Project {i}'} for i in range(5)])

        db.commit()

        p = ProjectService(db).get_paginated(page=1, per_page=2)

        assert len(p.items) == 2

        assert p.total >= 5

        db.close()



    def test_update(self, app):

        db = self._db(app)

        p = ProjectService(db).create(name='Original')

        ProjectService(db).update(p.id, name='Updated', description='New desc')

        assert p.name == 'Updated'

        assert p.description == 'New desc'

        db.close()



    def test_update_nonexistent(self, app):

        db = self._db(app)

        result = ProjectService(db).update(99999, name='Ghost')

        assert result is None

        db.close()



    def test_delete(self, app):

        db = self._db(app)

        p = ProjectService(db).create(name='To Delete')

        pid = p.id

        assert ProjectService(db).delete(pid) is True

        assert ProjectService(db).get_by_id(pid) is None

        db.close()



    def test_delete_nonexistent(self, app):

        db = self._db(app)

        assert ProjectService(db).delete(99999) is False

        db.close()





