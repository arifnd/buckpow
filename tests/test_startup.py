import subprocess
import sys
import time

from src import APP_VERSION


class TestAppStartup:
    def test_app_imports_and_config(self):
        code = """
import sys
sys.path.insert(0, '.')

# Test 1: App imports without error
from src import app, APP_VERSION, MIN_FIRMWARE_VERSION
from src.config import settings as config
assert hasattr(config, 'DATABASE_URL')
assert hasattr(config, 'JWT_SECRET')
assert hasattr(config, 'DISABLE_API_DOCS')
assert config.DATABASE_URL.startswith('sqlite')
assert config.JWT_SECRET is not None
assert app.title == 'BuckPow'
assert isinstance(APP_VERSION, str) and len(APP_VERSION) > 0
assert isinstance(MIN_FIRMWARE_VERSION, str) and len(MIN_FIRMWARE_VERSION) > 0

# Test 2: No name collision between config and settings package
from src.config import settings as config_obj
import src.settings as settings_pkg
assert 'settings' not in type(config_obj).__module__
assert config_obj.DATABASE_URL is not None

print('OK')
"""
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise AssertionError(f'App import failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
        assert result.stdout.strip() == 'OK'

    def test_api_docs_disabled_with_env_var(self):
        code = """
import os, sys
sys.path.insert(0, os.getcwd())
os.environ['DISABLE_API_DOCS'] = 'true'
import importlib
import src.config as _
importlib.reload(sys.modules['src.config'])
for mod in list(sys.modules.keys()):
    if mod.startswith('app') or mod.startswith('src'):
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
            raise AssertionError(f'Subprocess failed:\n{result.stderr}')
        assert result.stdout.strip() == 'OK'

    def test_fastapi_run_command_starts(self):
        proc = subprocess.Popen(
            [sys.executable, '-m', 'fastapi', 'run', 'src/main.py', '--port', '8899'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                time.sleep(0.2)
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(('127.0.0.1', 8899))
                    s.close()
                    break
                except (ConnectionRefusedError, OSError):
                    s.close()
            else:
                proc.kill()
                raise AssertionError('Server did not start within 5s')

            import urllib.request
            resp = urllib.request.urlopen('http://127.0.0.1:8899/api/v1/health', timeout=5)
            import json
            data = json.loads(resp.read())
            assert data['status'] == 'ok'
            assert data['version'] == APP_VERSION
        finally:
            proc.kill()
            proc.wait()
