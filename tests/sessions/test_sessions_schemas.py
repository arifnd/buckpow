import pytest
from pydantic import ValidationError


from src.sessions.schemas import SessionCreate, SessionUpdate

class TestSessionCreateSchema:

    def test_valid(self):
        s = SessionCreate(device_id=1, name='Test Session')
        assert s.device_id == 1
        assert s.name == 'Test Session'
        assert s.target_device == ''
        assert s.description == ''
        assert s.project_id is None

    def test_with_all_fields(self):
        s = SessionCreate(device_id=1, name='S', target_device='D', description='desc', project_id=5)
        assert s.target_device == 'D'
        assert s.project_id == 5

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            SessionCreate(device_id=1)



class TestSessionUpdateSchema:

    def test_all_optional(self):
        s = SessionUpdate()
        assert s.name is None
        assert s.target_device is None
        assert s.description is None
        assert s.project_id is None

    def test_partial(self):
        s = SessionUpdate(name='New Name')
        assert s.name == 'New Name'
        assert s.description is None


