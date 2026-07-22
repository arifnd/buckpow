from src import MIN_FIRMWARE_VERSION


class TestHealthAPI:
    def test_health_endpoint(self, client):
        resp = client.get('/api/v1/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert data['min_firmware_version'] == MIN_FIRMWARE_VERSION
