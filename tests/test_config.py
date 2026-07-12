import os
from unittest.mock import patch

from app.config import Settings


class TestSettings:

    def test_defaults(self):
        s = Settings()
        assert s.ALGORITHM == 'HS256'
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

    def test_secret_key_override(self):
        s = Settings(SECRET_KEY='my-secret')
        assert s.SECRET_KEY == 'my-secret'

    def test_admin_fields(self):
        s = Settings(ADMIN_EMAIL='admin@test.com', ADMIN_PASSWORD='pass123')
        assert s.ADMIN_EMAIL == 'admin@test.com'
        assert s.ADMIN_PASSWORD == 'pass123'
