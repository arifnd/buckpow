class TestSessionsAPI:
    def test_session_crud(self, client):
        d = client.post('/api/v1/devices', json={
            'device_id': 'esp32-session',
            'alias': 'Session Device',
        }).json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'],
            'name': 'Test Session',
            'target_device': 'esp32-session',
        })
        assert resp.status_code == 201
        s = resp.json()
        assert s['name'] == 'Test Session'
        assert s['status'] == 'draft'

        resp = client.post(f'/api/v1/sessions/{s["id"]}/start')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'running'

        resp = client.post(f'/api/v1/sessions/{s["id"]}/stop')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'finished'

    def test_session_list_includes_stats(self, client, app):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-sess-list'}).json()
        resp = client.post('/api/v1/sessions', json={'device_id': d['id'], 'name': 'Stats List'})
        s = resp.json()
        resp = client.get('/api/v1/sessions?page=1')
        data = resp.json()
        session_data = [x for x in data['sessions'] if x['id'] == s['id']][0]
        assert 'avg_power' in session_data
        assert 'total_energy' in session_data

    def test_session_stats_with_measurements(self, client, app):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-sess-stats'}).json()
        resp = client.post('/api/v1/sessions', json={'device_id': d['id'], 'name': 'Stats Session'})
        s = resp.json()
        client.post(f'/api/v1/sessions/{s["id"]}/start')
        client.post(f'/api/v1/sessions/{s["id"]}/stop')
        resp = client.get('/api/v1/sessions?page=1')
        data = resp.json()
        session_data = [x for x in data['sessions'] if x['id'] == s['id']][0]
        assert session_data['avg_power'] is None
        assert session_data['total_energy'] is None

    def test_session_stats_api(self, client, app):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-stats-api'}).json()
        resp = client.post('/api/v1/sessions', json={'device_id': d['id'], 'name': 'Stats API Session'})
        s = resp.json()
        resp = client.get(f'/api/v1/sessions/{s["id"]}/stats')
        assert resp.status_code == 200
        data = resp.json()
        assert 'avg_power' in data
        assert 'peak_power' in data
        assert 'total_energy' in data
        assert 'measurement_count' in data
        assert data['measurement_count'] == 0

    def test_session_stats_api_not_found(self, client):
        resp = client.get('/api/v1/sessions/99999/stats')
        assert resp.status_code == 404

    def test_session_stats_api_with_measurements(self, client, app):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-stats-m'}).json()
        key_resp = client.get(f'/api/v1/devices/{d["id"]}/key')
        api_key = key_resp.json()['api_key']
        device_headers = {'Authorization': f'Bearer {api_key}'}
        resp = client.post('/api/v1/sessions', json={'device_id': d['id'], 'name': 'Stats M Session'})
        s = resp.json()
        client.post(f'/api/v1/sessions/{s["id"]}/start')
        for i in range(5):
            client.post('/api/v1/measurements', json={
                'device_id': 'esp32-stats-m',
                'bus_voltage': 5.0 + i * 0.1,
                'shunt_voltage': 80 + i,
                'current': 200 + i * 10,
                'power': 1000 + i * 50,
            }, headers=device_headers)
        client.post(f'/api/v1/sessions/{s["id"]}/stop')
        resp = client.get(f'/api/v1/sessions/{s["id"]}/stats')
        assert resp.status_code == 200
        data = resp.json()
        assert data['measurement_count'] == 5
        assert data['avg_power'] > 0
        assert data['peak_power'] >= data['avg_power']

    def test_sessions_page(self, client):
        resp = client.get('/sessions')
        assert resp.status_code == 200

    def test_session_get_single(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-single-sess'}).json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Single Session',
        })
        s = resp.json()
        resp = client.get(f'/api/v1/sessions/{s["id"]}')
        assert resp.status_code == 200
        assert resp.json()['name'] == 'Single Session'

    def test_session_get_not_found(self, client):
        resp = client.get('/api/v1/sessions/99999')
        assert resp.status_code == 404

    def test_session_update_not_found(self, client):
        resp = client.put('/api/v1/sessions/99999', json={'name': 'Ghost'})
        assert resp.status_code == 404

    def test_session_delete_not_found(self, client):
        resp = client.delete('/api/v1/sessions/99999')
        assert resp.status_code == 404

    def test_session_create_missing_name(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-missing-name'}).json()
        resp = client.post('/api/v1/sessions', json={'device_id': d['id']})
        assert resp.status_code == 422
        assert 'name' in str(resp.json()['detail'])

    def test_session_create_missing_device_id(self, client):
        resp = client.post('/api/v1/sessions', json={'name': 'No Device'})
        assert resp.status_code == 422

    def test_session_create_no_json(self, client):
        resp = client.post('/api/v1/sessions', content=b'{}')
        assert resp.status_code == 422

    def test_session_start_nonexistent(self, client):
        resp = client.post('/api/v1/sessions/99999/start')
        assert resp.status_code == 400

    def test_session_stop_nonexistent(self, client):
        resp = client.post('/api/v1/sessions/99999/stop')
        assert resp.status_code == 400

    def test_session_stop_not_running(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-stop'}).json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Draft Session',
        })
        s = resp.json()
        assert s['status'] == 'draft'
        resp = client.post(f'/api/v1/sessions/{s["id"]}/stop')
        assert resp.status_code == 400

    def test_session_start_already_running(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-start'}).json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Session A',
        })
        a = resp.json()
        resp = client.post(f'/api/v1/sessions/{a["id"]}/start')
        assert resp.status_code == 200
        resp = client.post(f'/api/v1/sessions/{a["id"]}/start')
        assert resp.status_code == 400

    def test_session_pagination(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.sessions.models import Session as SessionModel
        from src.devices.service import DeviceService
        db = SessionLocal()
        device = DeviceService(db).create('esp32-sess-page')
        db.execute(insert(SessionModel), [
            {'device_id': device.id, 'name': f'Session {i}'} for i in range(15)
        ])
        db.commit()
        db.close()
        resp = client.get('/api/v1/sessions?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['sessions']) == 5
        assert data['total'] == 15
        assert data['pages'] == 3

    def test_session_page_zero_returns_all(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.sessions.models import Session as SessionModel
        from src.devices.service import DeviceService
        db = SessionLocal()
        device = DeviceService(db).create('esp32-sess-all')
        db.execute(insert(SessionModel), [
            {'device_id': device.id, 'name': f'Sess {i}'} for i in range(3)
        ])
        db.commit()
        db.close()
        resp = client.get('/api/v1/sessions?page=0')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3



class TestSessionsExtra:
    def test_session_start_and_stop(self, client, sample_device):
        sid = client.post('/api/v1/sessions', json={
            'name': 'Start/Stop Test',
            'device_id': sample_device['id'],
        }).json()['id']
        resp = client.post(f'/api/v1/sessions/{sid}/start')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'running'
        resp = client.post(f'/api/v1/sessions/{sid}/stop')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'finished'

    def test_session_already_running_guard(self, client, sample_device):
        sid = client.post('/api/v1/sessions', json={
            'name': 'Already Running',
            'device_id': sample_device['id'],
        }).json()['id']
        client.post(f'/api/v1/sessions/{sid}/start')
        resp = client.post(f'/api/v1/sessions/{sid}/start')
        assert resp.status_code == 400

    def test_device_update_enabled_flag(self, client, sample_device):
        did = sample_device['id']
        resp = client.put(f'/api/v1/devices/{did}', json={'enabled': False})
        assert resp.status_code == 200
        assert resp.json()['enabled'] is False

    def test_measurements_empty_list(self, client):
        resp = client.get('/api/v1/measurements?per_page=10')
        assert resp.status_code == 200
        assert resp.json()['total'] == 0

    def test_device_owner_mismatch_forbidden(self, client, sample_device, sample_project):
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.projects.models import Project
        from src.auth.models import User
        db = SessionLocal()
        other_user = User(name='Other', email='other2@example.com', password='x')
        db.add(other_user)
        db.commit()
        other_proj = Project(name='Other Project', owner_id=other_user.id)
        db.add(other_proj)
        db.commit()
        d = db.query(Device).filter_by(id=sample_device['id']).first()
        d.project_id = other_proj.id
        db.commit()
        db.close()
        resp = client.put(f'/api/v1/devices/{sample_device["id"]}', json={'alias': 'hacked'})
        assert resp.status_code == 403

    def test_csv_export_with_session_name(self, client, sample_device):
        resp = client.post('/api/v1/sessions', json={
            'name': 'Export Session!',
            'device_id': sample_device['id'],
        })
        sid = resp.json()['id']
        resp = client.get(f'/api/v1/measurements/export/csv?session_id={sid}')
        assert resp.status_code == 200
        assert 'Export_Session_report.csv' in resp.headers['content-disposition']
