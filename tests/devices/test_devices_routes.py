class TestDevicesAPI:
    def test_device_crud(self, client):
        resp = client.post('/api/v1/devices', json={
            'device_id': 'esp32-crud',
            'alias': 'CRUD Device',
        })
        assert resp.status_code == 201
        d = resp.json()
        assert d['device_id'] == 'esp32-crud'

        resp = client.get('/api/v1/devices')
        assert resp.status_code == 200
        data = resp.json()
        assert any(dev['device_id'] == 'esp32-crud' for dev in data['devices'])

        resp = client.put(f'/api/v1/devices/{d["id"]}', json={'alias': 'Updated Alias'})
        assert resp.status_code == 200
        assert resp.json()['alias'] == 'Updated Alias'

        resp = client.delete(f'/api/v1/devices/{d["id"]}')
        assert resp.status_code == 200

    def test_devices_page(self, client):
        resp = client.get('/devices')
        assert resp.status_code == 200

    def test_device_get_single(self, client):
        resp = client.post('/api/v1/devices', json={
            'device_id': 'esp32-single',
            'alias': 'Single Device',
        })
        d = resp.json()
        resp = client.get(f'/api/v1/devices/{d["id"]}')
        assert resp.status_code == 200
        assert resp.json()['device_id'] == 'esp32-single'

    def test_device_get_not_found(self, client):
        resp = client.get('/api/v1/devices/99999')
        assert resp.status_code == 404

    def test_device_update_not_found(self, client):
        resp = client.put('/api/v1/devices/99999', json={'alias': 'Ghost'})
        assert resp.status_code == 404

    def test_device_delete_not_found(self, client):
        resp = client.delete('/api/v1/devices/99999')
        assert resp.status_code == 404

    def test_device_create_missing_device_id(self, client):
        resp = client.post('/api/v1/devices', json={'alias': 'No ID'})
        assert resp.status_code == 422
        assert 'device_id' in str(resp.json()['detail'])

    def test_device_create_no_json(self, client):
        resp = client.post('/api/v1/devices', content=b'{}')
        assert resp.status_code == 422

    def test_device_pagination(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.devices.service import DeviceService
        db = SessionLocal()
        db.execute(insert(Device), [
            {'device_id': f'esp32-page-{i}', 'api_key': DeviceService.generate_api_key()}
            for i in range(15)
        ])
        db.commit()
        db.close()
        resp = client.get('/api/v1/devices?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['devices']) == 5
        assert data['total'] == 15
        assert data['pages'] == 3

    def test_device_page_zero_returns_all(self, client, app):
        from sqlalchemy import insert
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.devices.service import DeviceService
        db = SessionLocal()
        db.execute(insert(Device), [
            {'device_id': f'esp32-all-{i}', 'api_key': DeviceService.generate_api_key()}
            for i in range(3)
        ])
        db.commit()
        db.close()
        resp = client.get('/api/v1/devices?page=0')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_post_measurement_no_auth(self, unauth_client):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = True
        try:
            resp = unauth_client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            })
            assert resp.status_code == 401
            assert 'Authorization' in resp.json()['error']
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_post_measurement_malformed_auth(self, client):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = True
        try:
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            }, headers={'Authorization': 'Invalid'})
            assert resp.status_code == 401
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_post_measurement_invalid_key(self, client):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = True
        try:
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            }, headers={'Authorization': 'Bearer invalidkey123'})
            assert resp.status_code == 401
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_post_measurement_device_id_mismatch(self, client, device_auth_header):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = True
        try:
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'some-other-device', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            }, headers=device_auth_header)
            assert resp.status_code == 403
            assert b'does not match' in resp.content
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_post_measurement_disabled_device(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-disabled')
        d.enabled = False
        db.commit()
        key = d.api_key
        db.close()
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-disabled', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {key}'})
        assert resp.status_code == 403

    def test_device_get_key(self, client):
        created = client.post('/api/v1/devices', json={'device_id': 'esp32-getkey'}).json()
        resp = client.get(f'/api/v1/devices/{created["id"]}/key')
        assert resp.status_code == 200
        data = resp.json()
        assert 'api_key' in data
        assert len(data['api_key']) == 64

    def test_device_get_key_not_found(self, client):
        resp = client.get('/api/v1/devices/99999/key')
        assert resp.status_code == 404

    def test_device_toggle(self, client):
        created = client.post('/api/v1/devices', json={'device_id': 'esp32-toggle'}).json()
        assert created['enabled'] is True
        resp = client.patch(f'/api/v1/devices/{created["id"]}/toggle')
        assert resp.status_code == 200
        assert resp.json()['enabled'] is False

    def test_device_toggle_not_found(self, client):
        resp = client.patch('/api/v1/devices/99999/toggle')
        assert resp.status_code == 404

    def test_device_regenerate_key(self, client):
        created = client.post('/api/v1/devices', json={'device_id': 'esp32-regkey'}).json()
        old_key = created['api_key']
        resp = client.post(f'/api/v1/devices/{created["id"]}/regenerate-key')
        assert resp.status_code == 200
        data = resp.json()
        assert data['api_key'] != old_key

    def test_device_regenerate_key_not_found(self, client):
        resp = client.post('/api/v1/devices/99999/regenerate-key')
        assert resp.status_code == 404

    def test_device_update_no_json(self, client):
        resp = client.put('/api/v1/devices/1', content=b'{}')
        assert resp.status_code == 422

    def test_device_create_with_all_fields(self, client, sample_project):
        resp = client.post('/api/v1/devices', json={
            'device_id': 'esp32-full',
            'alias': 'Full',
            'description': 'All fields',
            'sampling_interval': 5,
            'project_id': sample_project['id'],
            'firmware_version': 'v2.0',
            'high_current_threshold': 0.5,
            'high_power_threshold': 3.0,
            'low_voltage_threshold': 4.0,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data['device_id'] == 'esp32-full'
        assert data['sampling_interval'] == 5
        assert data['firmware_version'] == 'v2.0'

    def test_device_update_with_thresholds(self, client):
        created = client.post('/api/v1/devices', json={'device_id': 'esp32-upd-thresh'}).json()
        resp = client.put(f'/api/v1/devices/{created["id"]}', json={
            'high_current_threshold': 0.8,
            'high_power_threshold': 5.0,
            'firmware_version': 'v3.0',
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['firmware_version'] == 'v3.0'



class TestDeviceAuthDisabled:

    def test_measurement_no_auth_succeeds(self, unauth_client, app):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = False
        try:
            resp = unauth_client.post('/api/v1/measurements', json={
                'device_id': 'esp32-nodev', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            })
            assert resp.status_code == 201
            assert resp.json()['status'] == 'success'
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_disabled_device_rejected_when_auth_off(self, unauth_client, app):
        from src.config import settings
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = False
        try:
            db = SessionLocal()
            d = DeviceService(db).create('esp32-disabled-off')
            d.enabled = False
            db.commit()
            db.close()
            resp = unauth_client.post('/api/v1/measurements', json={
                'device_id': 'esp32-disabled-off', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            })
            assert resp.status_code == 403
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_auth_still_works_when_enabled(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        assert resp.status_code == 201

    def test_no_auth_rejected_when_enabled(self, unauth_client):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = True
        try:
            resp = unauth_client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            })
            assert resp.status_code == 401
        finally:
            settings.DEVICE_AUTH_ENABLED = old

    def test_auth_ignored_when_disabled(self, client, device_auth_header):
        from src.config import settings
        old = settings.DEVICE_AUTH_ENABLED
        settings.DEVICE_AUTH_ENABLED = False
        try:
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth', 'bus_voltage': 5.0,
                'shunt_voltage': 80, 'current': 200, 'power': 1000,
            }, headers=device_auth_header)
            assert resp.status_code == 201
        finally:
            settings.DEVICE_AUTH_ENABLED = old




class TestDevicesExtra:
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
class TestFirmwareCompatibility:

    def _create_device(self, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-fw')
        key = d.api_key
        d.firmware_version = ''
        db.commit()
        db.close()
        return key

    def _auth_header(self, key):
        return {'Authorization': f'Bearer {key}'}

    def test_compatible_firmware(self, client, app):
        key = self._create_device(app)
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-fw', 'firmware_version': '1.0.0',
            'bus_voltage': 5.0, 'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=self._auth_header(key))
        assert resp.status_code == 201
        assert resp.headers.get('x-firmware-outdated') is None
        from src.database import SessionLocal
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == '1.0.0'
        db.close()

    def test_outdated_firmware(self, client, app):
        key = self._create_device(app)
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-fw', 'firmware_version': '0.9.0',
            'bus_voltage': 5.0, 'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=self._auth_header(key))
        assert resp.status_code == 201
        assert resp.headers.get('x-firmware-outdated') == 'true'
        from src.database import SessionLocal
        from src.devices.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == '0.9.0'
        db.close()


