class TestHealthAPI:
    def test_health_endpoint(self, client):
        resp = client.get('/api/v1/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert data['min_firmware_version'] == '1.0.0'
