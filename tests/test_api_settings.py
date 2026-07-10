class TestSettingsAPI:
    def test_get_settings(self, client):
        resp = client.get('/api/v1/settings')
        assert resp.status_code == 200
        assert resp.get_json() == {}

    def test_get_settings_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/settings')
        assert resp.status_code == 302

    def test_update_settings(self, client):
        resp = client.put('/api/v1/settings', json={
            'high_power_threshold': 3.0,
            'brand': 'MyApp',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['high_power_threshold'] == 3.0
        assert data['brand'] == 'MyApp'

    def test_update_all_settings(self, client):
        resp = client.put('/api/v1/settings', json={
            'high_power_threshold': 5.0,
            'high_current_threshold': 2.5,
            'low_voltage_threshold': 3.0,
            'brand': 'Test',
            'timestamp_format': '12h',
            'timezone': '+7',
            'device_watchdog_timeout': 60,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['high_power_threshold'] == 5.0
        assert data['high_current_threshold'] == 2.5
        assert data['low_voltage_threshold'] == 3.0
        assert data['brand'] == 'Test'
        assert data['timestamp_format'] == '12h'
        assert data['timezone'] == '+7'
        assert data['device_watchdog_timeout'] == 60

    def test_update_settings_clear_value(self, client):
        client.put('/api/v1/settings', json={'brand': 'Temp'})
        resp = client.put('/api/v1/settings', json={'brand': ''})
        assert resp.status_code == 200
        assert 'brand' not in resp.get_json()

    def test_update_settings_ignores_invalid_keys(self, client):
        resp = client.put('/api/v1/settings', json={'invalid_key': 'value', 'brand': 'Valid'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'invalid_key' not in data
        assert data['brand'] == 'Valid'

    def test_update_settings_no_json(self, client):
        resp = client.put('/api/v1/settings', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_update_settings_unauthorized(self, unauth_client):
        resp = unauth_client.put('/api/v1/settings', json={'brand': 'X'})
        assert resp.status_code == 302

    def test_backup_database(self, client):
        resp = client.get('/api/v1/settings/backup')
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'application/octet-stream'
        disp = resp.headers['Content-Disposition']
        assert 'attachment' in disp
        assert '.db' in disp
        assert len(resp.data) > 0

    def test_backup_database_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/settings/backup')
        assert resp.status_code == 302
