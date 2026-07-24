class TestProjectsAPI:
    def test_create_project(self, client):
        resp = client.post('/api/v1/projects', json={'name': 'New Project', 'description': 'Desc'})
        assert resp.status_code == 201
        data = resp.json()
        assert data['name'] == 'New Project'
        assert data['description'] == 'Desc'

    def test_create_project_no_name(self, client):
        resp = client.post('/api/v1/projects', json={'description': 'No name'})
        assert resp.status_code == 422

    def test_list_projects(self, client):
        client.post('/api/v1/projects', json={'name': 'Project A'})
        client.post('/api/v1/projects', json={'name': 'Project B'})
        resp = client.get('/api/v1/projects')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] >= 2
        assert len(data['projects']) >= 2

    def test_list_projects_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/projects')
        assert resp.status_code == 401

    def test_get_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Get Me'}).json()
        resp = client.get(f'/api/v1/projects/{created["id"]}')
        assert resp.status_code == 200
        assert resp.json()['name'] == 'Get Me'

    def test_get_project_not_found(self, client):
        resp = client.get('/api/v1/projects/99999')
        assert resp.status_code == 404

    def test_update_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Old'}).json()
        resp = client.put(f'/api/v1/projects/{created["id"]}', json={'name': 'New'})
        assert resp.status_code == 200
        assert resp.json()['name'] == 'New'

    def test_update_project_not_found(self, client):
        resp = client.put('/api/v1/projects/99999', json={'name': 'Ghost'})
        assert resp.status_code == 404

    def test_update_project_no_json(self, client):
        created = client.post('/api/v1/projects', json={'name': 'No JSON'}).json()
        resp = client.put(f'/api/v1/projects/{created["id"]}', content=b'{}')
        assert resp.status_code == 422

    def test_delete_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Delete Me'}).json()
        resp = client.delete(f'/api/v1/projects/{created["id"]}')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'deleted'

    def test_delete_project_not_found(self, client):
        resp = client.delete('/api/v1/projects/99999')
        assert resp.status_code == 404

    def test_list_page_zero(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.projects.models import Project
        db = SessionLocal()
        db.execute(insert(Project), [{'name': f'Project {i}'} for i in range(3)])
        db.commit()
        db.close()
        resp = client.get('/api/v1/projects?page=0')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_pagination(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.projects.models import Project
        db = SessionLocal()
        db.execute(insert(Project), [{'name': f'Pagination {i}'} for i in range(15)])
        db.commit()
        db.close()
        resp = client.get('/api/v1/projects?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.json()
        assert data['pages'] == 3
class TestOwnerChecks:

    def _second_user_client(self, app):
        from fastapi.testclient import TestClient
        from src.auth import create_access_token
        from src.auth.service import UserService
        from src.database import SessionLocal
        db = SessionLocal()
        user = UserService(db).create(name='Other', email='other@example.com', password='otherpass')
        token = create_access_token(data={'sub': user.id})
        db.close()
        client = TestClient(app)
        client.headers.update({'Authorization': f'Bearer {token}'})
        return client

    def test_other_user_cannot_update_project(self, client, app):
        other = self._second_user_client(app)
        created = client.post('/api/v1/projects', json={'name': 'My Project'}).json()
        resp = other.put(f'/api/v1/projects/{created["id"]}', json={'name': 'Hacked'})
        assert resp.status_code == 403

    def test_other_user_cannot_delete_project(self, client, app):
        other = self._second_user_client(app)
        created = client.post('/api/v1/projects', json={'name': 'My Project'}).json()
        resp = other.delete(f'/api/v1/projects/{created["id"]}')
        assert resp.status_code == 403

    def test_other_user_cannot_update_device_in_project(self, client, app, sample_project):
        other = self._second_user_client(app)
        created = client.post('/api/v1/devices', json={
            'device_id': 'esp32-owned',
            'project_id': sample_project['id'],
        }).json()
        resp = other.put(f'/api/v1/devices/{created["id"]}', json={'alias': 'Hacked'})
        assert resp.status_code == 403

    def test_other_user_cannot_delete_device_in_project(self, client, app, sample_project):
        other = self._second_user_client(app)
        created = client.post('/api/v1/devices', json={
            'device_id': 'esp32-owned-del',
            'project_id': sample_project['id'],
        }).json()
        resp = other.delete(f'/api/v1/devices/{created["id"]}')
        assert resp.status_code == 403

    def test_other_user_cannot_toggle_device_in_project(self, client, app, sample_project):
        other = self._second_user_client(app)
        created = client.post('/api/v1/devices', json={
            'device_id': 'esp32-owned-toggle',
            'project_id': sample_project['id'],
        }).json()
        resp = other.patch(f'/api/v1/devices/{created["id"]}/toggle')
        assert resp.status_code == 403

    def test_other_user_cannot_regenerate_key_in_project(self, client, app, sample_project):
        other = self._second_user_client(app)
        created = client.post('/api/v1/devices', json={
            'device_id': 'esp32-owned-key',
            'project_id': sample_project['id'],
        }).json()
        resp = other.post(f'/api/v1/devices/{created["id"]}/regenerate-key')
        assert resp.status_code == 403

    def test_device_without_project_still_accessible(self, client, app):
        other = self._second_user_client(app)
        created = client.post('/api/v1/devices', json={'device_id': 'esp32-no-project'}).json()
        resp = other.put(f'/api/v1/devices/{created["id"]}', json={'alias': 'Still OK'})
        assert resp.status_code == 200

    def test_no_firmware_sets_unknown(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-fw')
        key = d.api_key
        d.firmware_version = ''
        db.commit()
        db.close()
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-fw',
            'bus_voltage': 5.0, 'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {key}'})
        assert resp.status_code == 201
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == 'unknown'
        db.close()

    def test_firmware_upgrade(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-fw')
        key = d.api_key
        d.firmware_version = ''
        db.commit()
        db.close()
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-fw', 'firmware_version': '0.9.0',
            'bus_voltage': 5.0, 'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {key}'})
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-fw', 'firmware_version': '1.0.0',
            'bus_voltage': 5.0, 'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {key}'})
        assert resp.status_code == 201
        assert resp.headers.get('x-firmware-outdated') is None
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == '1.0.0'
        db.close()


