class TestDashboardRoutes:
    def test_login_page_returns_form(self, unauth_client):
        resp = unauth_client.get('/auth/login')
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'login' in html.lower() or 'email' in html.lower()

    def test_login_page_redirects_when_authenticated(self, client):
        resp = client.get('/auth/login')
        assert resp.status_code == 302

    def test_logout(self, client):
        resp = client.post('/auth/logout')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}

    def test_dashboard_requires_login(self, unauth_client):
        resp = unauth_client.get('/')
        assert resp.status_code == 302

    def test_devices_requires_login(self, unauth_client):
        resp = unauth_client.get('/devices')
        assert resp.status_code == 302

    def test_sessions_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions')
        assert resp.status_code == 302

    def test_measurements_requires_login(self, unauth_client):
        resp = unauth_client.get('/measurements')
        assert resp.status_code == 302

    def test_devices_new_requires_login(self, unauth_client):
        resp = unauth_client.get('/devices/new')
        assert resp.status_code == 302

    def test_devices_new_page(self, client):
        resp = client.get('/devices/new')
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'form' in html.lower() or 'device' in html.lower()

    def test_devices_edit_not_found(self, client):
        resp = client.get('/devices/99999/edit')
        assert resp.status_code == 200

    def test_sessions_new_page(self, client):
        resp = client.get('/sessions/new')
        assert resp.status_code == 200

    def test_sessions_edit_not_found(self, client):
        resp = client.get('/sessions/99999/edit')
        assert resp.status_code == 200

    def test_projects_page(self, client):
        resp = client.get('/projects')
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'project' in html.lower()

    def test_projects_requires_login(self, unauth_client):
        resp = unauth_client.get('/projects')
        assert resp.status_code == 302

    def test_benchmark_page(self, client):
        resp = client.get('/benchmark')
        assert resp.status_code == 200

    def test_benchmark_requires_login(self, unauth_client):
        resp = unauth_client.get('/benchmark')
        assert resp.status_code == 302

    def test_profile_page(self, client):
        resp = client.get('/profile')
        assert resp.status_code == 200

    def test_profile_requires_login(self, unauth_client):
        resp = unauth_client.get('/profile')
        assert resp.status_code == 302

    def test_alerts_page(self, client):
        resp = client.get('/alerts')
        assert resp.status_code == 200

    def test_alerts_requires_login(self, unauth_client):
        resp = unauth_client.get('/alerts')
        assert resp.status_code == 302

    def test_settings_page(self, client):
        resp = client.get('/settings')
        assert resp.status_code == 200

    def test_settings_requires_login(self, unauth_client):
        resp = unauth_client.get('/settings')
        assert resp.status_code == 302

    def test_sessions_new_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions/new')
        assert resp.status_code == 302

    def test_sessions_edit_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions/1/edit')
        assert resp.status_code == 302
