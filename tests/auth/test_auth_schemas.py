import pytest
from pydantic import ValidationError
from src.auth.schemas import LoginRequest, ProfileUpdate


class TestLoginRequestSchema:

    def test_valid(self):
        req = LoginRequest(email='user@test.com', password='pass')
        assert req.email == 'user@test.com'
        assert req.password == 'pass'

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest(email='user@test.com')



class TestProfileUpdateSchema:

    def test_all_optional(self):
        p = ProfileUpdate()
        assert p.name is None
        assert p.email is None
        assert p.password is None

    def test_partial(self):
        p = ProfileUpdate(name='New')
        assert p.name == 'New'
        assert p.email is None


