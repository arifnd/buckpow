import os
import subprocess
import sys

import pytest
from src import app
from src.config import settings


class TestAPIDocsEnabled:
    def test_docs_returns_200(self, client):
        resp = client.get('/docs')
        assert resp.status_code == 200

    def test_redoc_returns_200(self, client):
        resp = client.get('/redoc')
        assert resp.status_code == 200

    def test_openapi_json_returns_200(self, client):
        resp = client.get('/openapi.json')
        assert resp.status_code == 200

    def test_config_disabled_default(self):
        assert settings.DISABLE_API_DOCS is False

    def test_app_has_docs_url(self):
        assert app.docs_url == '/docs'
        assert app.redoc_url == '/redoc'
        assert app.openapi_url == '/openapi.json'


class TestAPIDocsDisabled:
    def test_docs_redoc_disabled_with_env_var(self):
        code = """
import os, sys
sys.path.insert(0, os.getcwd())
os.environ['DISABLE_API_DOCS'] = 'true'
import importlib
import src.config
importlib.reload(src.config)
for mod in list(sys.modules.keys()):
    if mod.startswith('app'):
        del sys.modules[mod]
from src import app as _app
from fastapi.testclient import TestClient
c = TestClient(_app)
r1 = c.get('/docs')
r2 = c.get('/redoc')
r3 = c.get('/openapi.json')
assert r1.status_code == 404, '/docs returned ' + str(r1.status_code)
assert r2.status_code == 404, '/redoc returned ' + str(r2.status_code)
assert r3.status_code == 404, '/openapi.json returned ' + str(r3.status_code)
assert _app.docs_url is None
assert _app.redoc_url is None
assert _app.openapi_url is None
print('OK')
"""
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            pytest.fail(f'Subprocess failed: {result.stderr}')
        assert result.stdout.strip() == 'OK'
