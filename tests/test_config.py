import os
from unittest.mock import patch

import pytest
from app.config import Settings


class TestSettings:

    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=False):
            s = Settings(_env_file=None)
        assert s.JWT_ALGORITHM == 'HS256'
        assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 7
        assert s.DEVICE_ONLINE_TIMEOUT == 30
        assert s.DEFAULT_SAMPLING_INTERVAL == 1
        assert s.DEVICE_AUTH_ENABLED is True
        assert s.DISABLE_API_DOCS is False

    def test_database_url_default(self):
        s = Settings(DATABASE_URL='sqlite:///instance/buckpow.db')
        assert 'buckpow.db' in s.DATABASE_URL

    def test_database_url_override(self):
        s = Settings(DATABASE_URL='postgresql://localhost/test')
        assert s.DATABASE_URL == 'postgresql://localhost/test'

    def test_debug_derivation(self):
        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            s = Settings()
            assert s.DEBUG is True

    def test_debug_production(self):
        with patch.dict(os.environ, {'APP_ENV': 'production'}):
            s = Settings()
            assert s.DEBUG is False

    def test_host_override(self):
        s = Settings(APP_HOST='127.0.0.1')
        assert s.HOST == '127.0.0.1'

    def test_port_override(self):
        s = Settings(APP_PORT='3000')
        assert s.PORT == 3000

    def test_jwt_secret_override(self):
        s = Settings(JWT_SECRET='my-secret-key-that-is-long-enough-for-testing')
        assert s.JWT_SECRET == 'my-secret-key-that-is-long-enough-for-testing'

    def test_secret_key_alias_backward_compat(self):
        s = Settings(SECRET_KEY='my-secret-key-that-is-long-enough-for-testing')
        assert s.JWT_SECRET == 'my-secret-key-that-is-long-enough-for-testing'

    def test_algorithm_alias_backward_compat(self):
        s = Settings(ALGORITHM='HS512')
        assert s.JWT_ALGORITHM == 'HS512'

    def test_admin_fields(self):
        s = Settings(ADMIN_EMAIL='admin@test.com', ADMIN_PASSWORD='pass123')
        assert s.ADMIN_EMAIL == 'admin@test.com'
        assert s.ADMIN_PASSWORD == 'pass123'

    def test_short_jwt_secret_warning(self):
        with pytest.warns(UserWarning, match='JWT_SECRET is'):
            Settings(JWT_SECRET='short', _env_file=None)

    def test_production_missing_jwt_secret_raises(self):
        with patch.dict(os.environ, {'APP_ENV': 'production', 'JWT_SECRET': ''}):
            with pytest.raises(RuntimeError, match='JWT_SECRET environment variable is required'):
                Settings(JWT_SECRET='', _env_file=None)
