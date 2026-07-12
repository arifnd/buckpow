from app.dependencies import (
    create_access_token,
    get_current_user,
    require_user,
    get_api_key_device,
    get_db,
)
from app.auth import (
    create_access_token as auth_create,
    get_current_user as auth_current,
    require_user as auth_require,
    get_api_key_device as auth_apikey,
)
from app.database import get_db as db_get_db


class TestDependenciesReExports:

    def test_create_access_token(self):
        assert create_access_token is auth_create

    def test_get_current_user(self):
        assert get_current_user is auth_current

    def test_require_user(self):
        assert require_user is auth_require

    def test_get_api_key_device(self):
        assert get_api_key_device is auth_apikey

    def test_get_db(self):
        assert get_db is db_get_db
