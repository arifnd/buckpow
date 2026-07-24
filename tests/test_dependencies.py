from src.auth import (
    create_access_token as auth_create,
)
from src.auth import (
    get_api_key_device as auth_apikey,
)
from src.auth import (
    get_current_user as auth_current,
)
from src.auth import (
    require_user as auth_require,
)
from src.database import get_db as db_get_db
from src.dependencies import (
    create_access_token,
    get_api_key_device,
    get_current_user,
    get_db,
    require_user,
)


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
