from pydantic import ValidationError


from src.projects.schemas import ProjectCreate, ProjectUpdate

class TestProjectCreateSchema:

    def test_valid(self):
        p = ProjectCreate(name='Test Project')
        assert p.name == 'Test Project'
        assert p.description == ''

    def test_with_description(self):
        p = ProjectCreate(name='P', description='desc')
        assert p.description == 'desc'



class TestProjectUpdateSchema:

    def test_all_optional(self):
        p = ProjectUpdate()
        assert p.name is None
        assert p.description is None


