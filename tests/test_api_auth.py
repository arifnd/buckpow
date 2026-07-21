class TestAuthAPI:
    def test_login_success(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={
            'email': 'admin@example.com',
            'password': 'password',
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert data['user']['email'] == 'admin@example.com'
        assert 'token' in data

    def test_login_wrong_password(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={
            'email': 'admin@example.com',
            'password': 'wrong',
        })
        assert resp.status_code == 401
        assert 'Invalid' in resp.json()['error']

    def test_login_missing_fields(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={'email': 'admin@example.com'})
        assert resp.status_code == 422

    def test_login_no_json(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', content=b'{}')
        assert resp.status_code == 422

    def test_logout(self, client):
        resp = client.post('/api/v1/auth/logout')
        assert resp.status_code == 200
        assert resp.json() == {'status': 'ok'}

    def test_me_authenticated(self, client):
        resp = client.get('/api/v1/auth/me')
        assert resp.status_code == 200
        data = resp.json()
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
        data = resp.json()
        assert data['user']['name'] == 'Updated Admin'

    def test_update_profile_no_json(self, client):
        resp = client.put('/api/v1/auth/profile', content=b'{}')
        assert resp.status_code == 422

    def test_update_profile_email_taken(self, client, app):
        from app.database import SessionLocal
        from app.services.user_service import UserService
        db = SessionLocal()
        UserService(db).create(name='Other', email='other@example.com', password='x')
        db.close()
        resp = client.put('/api/v1/auth/profile', json={
            'email': 'other@example.com',
        })
        assert resp.status_code == 409

    def test_update_profile_with_password(self, client):
        resp = client.put('/api/v1/auth/profile', json={'password': 'newpass'})
        assert resp.status_code == 200

    def test_me_with_invalid_token(self, unauth_client):
        resp = unauth_client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer invalid.jwt.token'})
        assert resp.status_code == 401

    def test_me_with_missing_sub(self, unauth_client, app):
        from app.auth import create_access_token
        token = create_access_token(data={})
        resp = unauth_client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 401

    def test_me_with_non_numeric_sub(self, unauth_client, app):
        from app.auth import create_access_token
        token = create_access_token(data={'sub': 'not-a-number'})
        resp = unauth_client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 401

    def test_login_empty_fields(self, unauth_client):
        resp = unauth_client.post('/api/v1/auth/login', json={
            'email': '',
            'password': '',
        })
        assert resp.status_code == 400
