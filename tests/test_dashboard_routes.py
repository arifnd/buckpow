class TestDashboardRoutes:
    def test_login_page_returns_form(self, unauth_client):
        resp = unauth_client.get('/auth/login')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'login' in html.lower() or 'email' in html.lower()

    def test_login_page_redirects_when_authenticated(self, client):
        resp = client.get('/auth/login', follow_redirects=False)
        assert resp.status_code == 302

    def test_logout(self, client):
        resp = client.post('/auth/logout')
        assert resp.status_code == 200
        assert resp.json() == {'status': 'ok'}

    def test_devices_new_page(self, client):
        resp = client.get('/devices/new')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'form' in html.lower() or 'device' in html.lower()

    def test_devices_edit_not_found(self, client):
        resp = client.get('/devices/99999/edit')
        assert resp.status_code == 200

    def test_sessions_new_page(self, client):
        resp = client.get('/sessions/new')
        assert resp.status_code == 200

    def test_sessions_edit_not_found(self, client):
        resp = client.get('/sessions/1/edit')
        assert resp.status_code == 200

    def test_session_detail_page(self, client, app):
        from app.database import SessionLocal
        from app.models import Device, Session
        db = SessionLocal()
        d = Device(device_id='esp32-detail', alias='Detail Device', sampling_interval=1)
        db.add(d)
        db.commit()
        s = Session(name='Detail Session', device_id=d.id, status='draft')
        db.add(s)
        db.commit()
        sid = s.id
        db.close()
        resp = client.get(f'/sessions/{sid}')
        assert resp.status_code == 200
        assert b'Detail Session' in resp.content

    def test_session_detail_not_found(self, client):
        resp = client.get('/sessions/99999')
        assert resp.status_code == 200

    def test_projects_page(self, client):
        resp = client.get('/projects')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'project' in html.lower()

    def test_benchmark_page(self, client):
        resp = client.get('/benchmark')
        assert resp.status_code == 200

    def test_profile_page(self, client):
        resp = client.get('/profile')
        assert resp.status_code == 200

    def test_alerts_page(self, client):
        resp = client.get('/alerts')
        assert resp.status_code == 200

    def test_settings_page(self, client):
        resp = client.get('/settings')
        assert resp.status_code == 200


class TestAuthRedirects:
    def test_dashboard_requires_login(self, unauth_client):
        resp = unauth_client.get('/', follow_redirects=False)
        assert resp.status_code == 302

    def test_devices_requires_login(self, unauth_client):
        resp = unauth_client.get('/devices', follow_redirects=False)
        assert resp.status_code == 302

    def test_devices_new_requires_login(self, unauth_client):
        resp = unauth_client.get('/devices/new', follow_redirects=False)
        assert resp.status_code == 302

    def test_sessions_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions', follow_redirects=False)
        assert resp.status_code == 302

    def test_sessions_new_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions/new', follow_redirects=False)
        assert resp.status_code == 302

    def test_projects_requires_login(self, unauth_client):
        resp = unauth_client.get('/projects', follow_redirects=False)
        assert resp.status_code == 302

    def test_measurements_requires_login(self, unauth_client):
        resp = unauth_client.get('/measurements', follow_redirects=False)
        assert resp.status_code == 302

    def test_benchmark_requires_login(self, unauth_client):
        resp = unauth_client.get('/benchmark', follow_redirects=False)
        assert resp.status_code == 302

    def test_alerts_requires_login(self, unauth_client):
        resp = unauth_client.get('/alerts', follow_redirects=False)
        assert resp.status_code == 302

    def test_settings_requires_login(self, unauth_client):
        resp = unauth_client.get('/settings', follow_redirects=False)
        assert resp.status_code == 302

    def test_profile_requires_login(self, unauth_client):
        resp = unauth_client.get('/profile', follow_redirects=False)
        assert resp.status_code == 302

    def test_audit_requires_login(self, unauth_client):
        resp = unauth_client.get('/audit', follow_redirects=False)
        assert resp.status_code == 302

    def test_devices_edit_requires_login(self, unauth_client):
        resp = unauth_client.get('/devices/1/edit', follow_redirects=False)
        assert resp.status_code == 302

    def test_sessions_edit_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions/1/edit', follow_redirects=False)
        assert resp.status_code == 302

    def test_session_detail_requires_login(self, unauth_client):
        resp = unauth_client.get('/sessions/1', follow_redirects=False)
        assert resp.status_code == 302

    def test_dashboard_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_devices_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/devices', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_sessions_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/sessions', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_projects_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/projects', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_measurements_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/measurements', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_benchmark_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/benchmark', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_alerts_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/alerts', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_settings_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/settings', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_profile_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/profile', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_audit_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/audit', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_devices_edit_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/devices/1/edit', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_sessions_edit_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/sessions/1/edit', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_session_detail_redirect_target_is_login(self, unauth_client):
        resp = unauth_client.get('/sessions/1', follow_redirects=False)
        assert '/auth/login' in resp.headers.get('location', '')

    def test_authenticated_dashboard_returns_200(self, client):
        assert client.get('/').status_code == 200

    def test_authenticated_devices_returns_200(self, client):
        assert client.get('/devices').status_code == 200

    def test_authenticated_devices_new_returns_200(self, client):
        assert client.get('/devices/new').status_code == 200

    def test_authenticated_sessions_returns_200(self, client):
        assert client.get('/sessions').status_code == 200

    def test_authenticated_sessions_new_returns_200(self, client):
        assert client.get('/sessions/new').status_code == 200

    def test_authenticated_session_detail_returns_200(self, client, app):
        from app.database import SessionLocal
        from app.models import Device, Session
        db = SessionLocal()
        d = Device(device_id='esp32-auth-detail', alias='Auth Detail Device', sampling_interval=1)
        db.add(d)
        db.commit()
        s = Session(name='Auth Detail Session', device_id=d.id, status='draft')
        db.add(s)
        db.commit()
        sid = s.id
        db.close()
        assert client.get(f'/sessions/{sid}').status_code == 200

    def test_authenticated_projects_returns_200(self, client):
        assert client.get('/projects').status_code == 200

    def test_authenticated_measurements_returns_200(self, client):
        assert client.get('/measurements').status_code == 200

    def test_authenticated_benchmark_returns_200(self, client):
        assert client.get('/benchmark').status_code == 200

    def test_authenticated_alerts_returns_200(self, client):
        assert client.get('/alerts').status_code == 200

    def test_authenticated_settings_returns_200(self, client):
        assert client.get('/settings').status_code == 200

    def test_authenticated_profile_returns_200(self, client):
        assert client.get('/profile').status_code == 200

    def test_authenticated_audit_returns_200(self, client):
        assert client.get('/audit').status_code == 200
