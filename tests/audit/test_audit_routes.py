

class TestAuditExtra:
    def test_audit_logs_endpoint(self, client, sample_device):
        resp = client.get('/api/v1/audit/logs')
        assert resp.status_code == 200
        data = resp.json()
        assert 'logs' in data
        assert 'actions' in data

    def test_firmware_version_outdated(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
            'firmware_version': '0.5.0',
        }, headers=device_auth_header)
        assert resp.status_code == 201
        assert resp.headers.get('X-Firmware-Outdated') == 'true'

    def test_firmware_version_current(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
            'firmware_version': '1.0.0',
        }, headers=device_auth_header)
        assert resp.status_code == 201
        assert 'X-Firmware-Outdated' not in resp.headers

    def test_firmware_version_invalid_format(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
            'firmware_version': 'not-a-version',
        }, headers=device_auth_header)
        assert resp.status_code == 201

    def test_firmware_version_missing_sets_unknown(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        from src.database import SessionLocal
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-auth').first()
        assert d.firmware_version == 'unknown'
        db.close()

    def test_firmware_version_missing_sets_unknown(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        from src.database import SessionLocal
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-auth').first()
        assert d.firmware_version == 'unknown'
        db.close()

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
        from src.auth.models import User
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.projects.models import Project
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
