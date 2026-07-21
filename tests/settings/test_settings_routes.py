class TestSettingsAPI:
    def test_get_settings(self, client):
        resp = client.get('/api/v1/settings')
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_get_settings_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/settings')
        assert resp.status_code == 401

    def test_update_settings(self, client):
        resp = client.put('/api/v1/settings', json={
            'high_power_threshold': 3.0,
            'brand': 'MyApp',
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['high_power_threshold'] == 3.0
        assert data['brand'] == 'MyApp'

    def test_update_all_settings(self, client):
        resp = client.put('/api/v1/settings', json={
            'high_power_threshold': 5.0,
            'high_current_threshold': 2.5,
            'low_voltage_threshold': 3.0,
            'brand': 'Test',
            'timestamp_format': '12h',
            'date_format': 'DD/MM/YYYY',
            'timezone': '+7',
            'device_watchdog_timeout': 60,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['high_power_threshold'] == 5.0
        assert data['high_current_threshold'] == 2.5
        assert data['low_voltage_threshold'] == 3.0
        assert data['brand'] == 'Test'
        assert data['timestamp_format'] == '12h'
        assert data['date_format'] == 'DD/MM/YYYY'
        assert data['timezone'] == '+7'
        assert data['device_watchdog_timeout'] == 60

    def test_update_date_format(self, client):
        resp = client.put('/api/v1/settings', json={'date_format': 'MM/DD/YYYY'})
        assert resp.status_code == 200
        assert resp.json()['date_format'] == 'MM/DD/YYYY'
        resp = client.put('/api/v1/settings', json={'date_format': ''})
        assert 'date_format' not in resp.json()

    def test_get_date_format_default(self, client):
        resp = client.get('/api/v1/settings')
        assert resp.status_code == 200
        assert 'date_format' not in resp.json()

    def test_update_settings_clear_value(self, client):
        client.put('/api/v1/settings', json={'brand': 'Temp'})
        resp = client.put('/api/v1/settings', json={'brand': ''})
        assert resp.status_code == 200
        assert 'brand' not in resp.json()

    def test_update_settings_ignores_invalid_keys(self, client):
        resp = client.put('/api/v1/settings', json={'invalid_key': 'value', 'brand': 'Valid'})
        assert resp.status_code == 200
        data = resp.json()
        assert 'invalid_key' not in data
        assert data['brand'] == 'Valid'

    def test_update_settings_no_json(self, client):
        resp = client.put('/api/v1/settings', content=b'{}')
        assert resp.status_code == 422

    def test_update_settings_unauthorized(self, unauth_client):
        resp = unauth_client.put('/api/v1/settings', json={'brand': 'X'})
        assert resp.status_code == 401

    def test_backup_database(self, client):
        resp = client.get('/api/v1/settings/backup')
        assert resp.status_code == 200
        assert resp.headers['content-type'] == 'application/octet-stream'
        disp = resp.headers['content-disposition']
        assert 'attachment' in disp
        assert '.db' in disp
        assert len(resp.content) > 0

    def test_backup_database_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/settings/backup')
        assert resp.status_code == 401

    def test_db_info(self, client):
        resp = client.get('/api/v1/settings/db-info')
        assert resp.status_code == 200
        data = resp.json()
        assert data['type'] == 'sqlite'
        assert data['size'] is not None
        assert data['backup_formats']['sqlite'] is True
        assert data['backup_formats']['sql_dump'] is False

    def test_detect_db_type_sqlite(self):
        from src.settings.router import _detect_db_type
        assert _detect_db_type() == 'sqlite'

    def test_detect_db_type_postgresql(self):
        from src.settings.router import _detect_db_type
        from src import database
        old = database.engine.url
        try:
            database.engine.url = database.engine.url.set(host='localhost', database='test')
            from sqlalchemy.engine import make_url
            database.engine.url = make_url('postgresql://user:pass@localhost/test')
            assert _detect_db_type() == 'postgresql'
        finally:
            database.engine.url = old

    def test_detect_db_type_mysql(self):
        from src.settings.router import _detect_db_type
        from src import database
        from sqlalchemy.engine import make_url
        old = database.engine.url
        try:
            database.engine.url = make_url('mysql+pymysql://user:pass@localhost/test')
            assert _detect_db_type() == 'mysql'
        finally:
            database.engine.url = old

    def test_detect_db_type_unknown(self):
        from src.settings.router import _detect_db_type
        from src import database
        from sqlalchemy.engine import make_url
        old = database.engine.url
        try:
            database.engine.url = make_url('oracle://user:pass@localhost/test')
            assert _detect_db_type() == 'unknown'
        finally:
            database.engine.url = old

    def test_get_db_size_sqlite(self):
        from src.settings.router import _get_db_size
        size = _get_db_size()
        assert size is not None
        assert size > 0

    def test_backup_postgresql_no_tool(self, client):
        from unittest.mock import patch
        from src.settings.router import _backup_postgresql
        with patch('src.settings.router.shutil.which', return_value=None):
            resp = client.get('/api/v1/settings/backup')
            # Since actual db is sqlite, this won't hit postgresql path
            # Test the function directly
            from fastapi.exceptions import HTTPException
            try:
                _backup_postgresql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'pg_dump not found' in str(e.detail)

    def test_backup_mysql_no_tool(self):
        from unittest.mock import patch
        from src.settings.router import _backup_mysql
        from fastapi.exceptions import HTTPException
        with patch('src.settings.router.shutil.which', return_value=None):
            try:
                _backup_mysql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'mysqldump not found' in str(e.detail)

    def test_backup_postgresql_timeout(self):
        from unittest.mock import patch, MagicMock
        import subprocess
        from src.settings.router import _backup_postgresql
        from fastapi.exceptions import HTTPException
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b'dump data'
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/pg_dump'), \
             patch('src.settings.router.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='pg_dump', timeout=120)):
            try:
                _backup_postgresql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'timed out' in str(e.detail)

    def test_backup_mysql_timeout(self):
        from unittest.mock import patch
        import subprocess
        from src.settings.router import _backup_mysql
        from fastapi.exceptions import HTTPException
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/mysqldump'), \
             patch('src.settings.router.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='mysqldump', timeout=120)):
            try:
                _backup_mysql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'timed out' in str(e.detail)

    def test_backup_postgresql_dump_error(self):
        from unittest.mock import patch, MagicMock
        from src.settings.router import _backup_postgresql
        from fastapi.exceptions import HTTPException
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b'permission denied'
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/pg_dump'), \
             patch('src.settings.router.subprocess.run', return_value=mock_result):
            try:
                _backup_postgresql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'pg_dump failed' in str(e.detail)

    def test_backup_mysql_dump_error(self):
        from unittest.mock import patch, MagicMock
        from src.settings.router import _backup_mysql
        from fastapi.exceptions import HTTPException
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b'access denied'
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/mysqldump'), \
             patch('src.settings.router.subprocess.run', return_value=mock_result):
            try:
                _backup_mysql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'mysqldump failed' in str(e.detail)

    def test_backup_postgresql_file_not_found(self):
        from unittest.mock import patch
        from src.settings.router import _backup_postgresql
        from fastapi.exceptions import HTTPException
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/pg_dump'), \
             patch('src.settings.router.subprocess.run', side_effect=FileNotFoundError):
            try:
                _backup_postgresql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'not found' in str(e.detail).lower()

    def test_backup_mysql_file_not_found(self):
        from unittest.mock import patch
        from src.settings.router import _backup_mysql
        from fastapi.exceptions import HTTPException
        with patch('src.settings.router.shutil.which', return_value='/usr/bin/mysqldump'), \
             patch('src.settings.router.subprocess.run', side_effect=FileNotFoundError):
            try:
                _backup_mysql('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert 'not found' in str(e.detail).lower()

    def test_parse_pg_url(self):
        from src.settings.router import _parse_pg_url
        from src import database
        from sqlalchemy.engine import make_url
        old = database.engine.url
        try:
            database.engine.url = make_url('postgresql://admin:secret@db.example.com:5432/mydb')
            result = _parse_pg_url()
            assert result['host'] == 'db.example.com'
            assert result['port'] == 5432
            assert result['dbname'] == 'mydb'
            assert result['user'] == 'admin'
            # SQLAlchemy masks passwords in URL representation
            assert result['password'] is not None
        finally:
            database.engine.url = old

    def test_parse_mysql_url(self):
        from src.settings.router import _parse_mysql_url
        from src import database
        from sqlalchemy.engine import make_url
        old = database.engine.url
        try:
            database.engine.url = make_url('mysql+pymysql://root:pass@db.example.com:3306/mydb')
            result = _parse_mysql_url()
            assert result['host'] == 'db.example.com'
            assert result['port'] == 3306
            assert result['dbname'] == 'mydb'
            assert result['user'] == 'root'
            assert result['password'] is not None
        finally:
            database.engine.url = old

    def test_backup_sqlite_relative_path(self):
        from unittest.mock import patch, MagicMock
        from src.settings.router import _backup_sqlite
        from fastapi.exceptions import HTTPException
        mock_engine = MagicMock()
        mock_engine.url = 'sqlite:///relative/path/test.db'
        with patch('src.settings.router.engine', mock_engine):
            try:
                _backup_sqlite('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert e.status_code == 404

    def test_backup_sqlite_file_not_found(self):
        from unittest.mock import patch, MagicMock
        from src.settings.router import _backup_sqlite
        from fastapi.exceptions import HTTPException
        mock_engine = MagicMock()
        mock_engine.url = 'sqlite:////nonexistent/path/buckpow.db'
        with patch('src.settings.router.engine', mock_engine):
            try:
                _backup_sqlite('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert e.status_code == 404

    def test_backup_sqlite_invalid_url(self):
        from unittest.mock import patch, MagicMock
        from src.settings.router import _backup_sqlite
        from fastapi.exceptions import HTTPException
        mock_engine = MagicMock()
        mock_engine.url = 'mysql://localhost/test'
        with patch('src.settings.router.engine', mock_engine):
            try:
                _backup_sqlite('2025-01-01-000000')
                assert False, "Should have raised"
            except HTTPException as e:
                assert e.status_code == 400
                assert 'Invalid SQLite URL' in str(e.detail)
