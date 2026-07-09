class TestAuthAPI:
    def test_login_success(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={
            'email': 'admin@example.com',
            'password': 'password',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert data['user']['email'] == 'admin@example.com'

    def test_login_wrong_password(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={
            'email': 'admin@example.com',
            'password': 'wrong',
        })
        assert resp.status_code == 401
        assert 'Invalid' in resp.get_json()['error']

    def test_login_missing_fields(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={'email': 'admin@example.com'})
        assert resp.status_code == 400
        assert 'required' in resp.get_json()['error']

    def test_login_no_json(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_logout(self, client):
        resp = client.post('/api/v1/auth/logout')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}

    def test_me_authenticated(self, client):
        resp = client.get('/api/v1/auth/me')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['email'] == 'admin@example.com'

    def test_me_unauthenticated(self, unauth_client):
        resp = unauth_client.get('/api/v1/auth/me')
        assert resp.status_code == 401

    def test_update_profile(self, client):
        resp = client.put('/api/v1/auth/profile', json={
            'name': 'Updated Admin',
            'email': 'admin@example.com',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['name'] == 'Updated Admin'

    def test_update_profile_no_json(self, client):
        resp = client.put('/api/v1/auth/profile', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_update_profile_email_taken(self, client, app):
        from app import db
        from app.models import User
        from app.services.user_service import UserService
        with app.app_context():
            UserService.create(name='Other', email='other@example.com', password='x')
        resp = client.put('/api/v1/auth/profile', json={
            'email': 'other@example.com',
        })
        assert resp.status_code == 409

    def test_update_profile_with_password(self, client):
        resp = client.put('/api/v1/auth/profile', json={'password': 'newpass'})
        assert resp.status_code == 200
        resp = client.post('/api/v1/auth/logout')
        resp = client.post('/api/v1/auth/login', json={
            'email': 'admin@example.com',
            'password': 'newpass',
        })
        assert resp.status_code == 200
