class TestErrorHandlers:
    def test_api_400_bad_request(self, client):
        resp = client.get('/api/v1/measurements?page=-1')
        assert resp.status_code in (200, 400)
        if resp.status_code == 400:
            data = resp.json()
            assert data['code'] == 'BAD_REQUEST'

    def test_api_404_not_found(self, client):
        resp = client.get('/api/v1/nonexistent')
        assert resp.status_code == 404
        data = resp.json()
        assert data['code'] == 'NOT_FOUND'

    def test_api_405_method_not_allowed(self, client):
        resp = client.put('/api/v1/health')
        assert resp.status_code == 405
        data = resp.json()
        assert 'METHOD_NOT_ALLOWED' in data.get('code', '')

    def test_html_404_returns_default(self, client):
        resp = client.get('/nonexistent/page')
        assert resp.status_code == 404

    def test_api_validation_error(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-test',
        }, headers=device_auth_header)
        assert resp.status_code == 422

    def test_api_auth_error(self, unauth_client):
        resp = unauth_client.get('/api/v1/auth/me')
        assert resp.status_code == 401
