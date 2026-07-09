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
