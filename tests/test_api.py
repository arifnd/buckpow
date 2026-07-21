class TestAPI:
    def test_post_measurement_success(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth',
            'bus_voltage': 5.12,
            'shunt_voltage': 82,
            'current': 241,
            'power': 1234,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        data = resp.json()
        assert data['status'] == 'success'

    def test_post_pzem_measurement_no_shunt(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth',
            'bus_voltage': 230.5,
            'current': 4500,
            'power': 1035000,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        data = resp.json()
        assert data['status'] == 'success'

    def test_post_pzem_ac_voltage_range(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth',
            'bus_voltage': 220.0,
            'current': 10000,
            'power': 2200000,
        }, headers=device_auth_header)
        assert resp.status_code == 201

    def test_post_pzem_load_voltage_equals_bus(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth',
            'bus_voltage': 230.0,
            'current': 5000,
            'power': 1150000,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        from app.database import SessionLocal
        from app.models import Measurement
        db = SessionLocal()
        m = db.query(Measurement).order_by(Measurement.id.desc()).first()
        assert m.load_voltage == 230.0
        assert m.shunt_voltage == 0.0
        db.close()

    def test_post_pzem_multiple_readings_energy_accumulates(self, client, device_auth_header):
        for i in range(3):
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth',
                'bus_voltage': 230.0 + i,
                'current': 5000,
                'power': 1150000,
            }, headers=device_auth_header)
            assert resp.status_code == 201
        from app.database import SessionLocal
        from app.models import Measurement
        db = SessionLocal()
        rows = db.query(Measurement).filter_by(device_id=1).order_by(Measurement.id).all()
        assert len(rows) >= 3
        assert rows[-1].energy >= rows[0].energy
        db.close()

    def test_post_measurement_missing_fields(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={'device_id': 'esp32-auth'},
                           headers=device_auth_header)
        assert resp.status_code == 422

    def test_post_measurement_no_json(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', content=b'{}', headers=device_auth_header)
        assert resp.status_code == 422

    def test_get_measurements_paginated(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0, 'shunt_voltage': 80,
            'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements?per_page=10')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['measurements']) >= 1
        assert data['total'] >= 1

    def test_get_dashboard(self, client):
        resp = client.get('/api/v1/dashboard')
        assert resp.status_code == 200
        data = resp.json()
        assert 'devices' in data
        assert 'stats' in data

    def test_get_chart_data(self, client):
        resp = client.get('/api/v1/chart?limit=10')
        assert resp.status_code == 200
        data = resp.json()
        assert 'labels' in data
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data
        assert 'energy' in data

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

    def test_dashboard_page(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'BuckPow' in resp.content

    def test_devices_page(self, client):
        resp = client.get('/devices')
        assert resp.status_code == 200

    def test_sessions_page(self, client):
        resp = client.get('/sessions')
        assert resp.status_code == 200

    def test_measurements_page(self, client):
        resp = client.get('/measurements')
        assert resp.status_code == 200

    # ── Device API edge cases ──

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
        from app.database import SessionLocal
        from app.models import Device
        from app.services.device_service import DeviceService
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
        assert data['page'] == 1

    def test_device_page_zero_returns_all(self, client, app):
        from sqlalchemy import insert
        from app.database import SessionLocal
        from app.models import Device
        from app.services.device_service import DeviceService
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

    # ── Session API edge cases ──

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
        from app.database import SessionLocal
        from app.models import Device, Session as SessionModel
        from app.services.device_service import DeviceService
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
        from app.database import SessionLocal
        from app.models import Device, Session as SessionModel
        from app.services.device_service import DeviceService
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

    # ── Measurements API edge cases ──

    def test_measurements_empty(self, client):
        resp = client.get('/api/v1/measurements')
        assert resp.status_code == 200
        data = resp.json()
        assert data['measurements'] == []
        assert data['total'] == 0

    def test_measurements_filter_by_device(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
        db = SessionLocal()
        da = DeviceService(db).create('esp32-filt-a')
        db_ = DeviceService(db).create('esp32-filt-b')
        ka = da.api_key
        kb = db_.api_key
        db.close()
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-filt-a', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {ka}'})
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-filt-b', 'bus_voltage': 6.0,
            'shunt_voltage': 90, 'current': 300, 'power': 2000,
        }, headers={'Authorization': f'Bearer {kb}'})
        resp = client.get(f'/api/v1/measurements?device_id={db_.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['measurements']) == 1

    def test_csv_export(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements/export/csv')
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers['content-type']
        assert b'Node' in resp.content
        assert b'esp32-auth' in resp.content

    def test_csv_export_empty(self, client):
        resp = client.get('/api/v1/measurements/export/csv')
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers['content-type']
        lines = resp.content.decode().strip().split('\n')
        assert len(lines) == 1

    def test_chart_data_with_filters(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-chart')
        key = d.api_key
        db.close()
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-chart', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers={'Authorization': f'Bearer {key}'})
        resp = client.get(f'/api/v1/chart?limit=5&device_id={d.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['labels']) == 1

    def test_get_measurements_with_date_range(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements?start_date=2000-01-01&end_date=2099-12-31')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['measurements']) >= 1

    # ── XLSX export ──

    def test_xlsx_export(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements/export/xlsx')
        assert resp.status_code == 200
        assert 'spreadsheetml' in resp.headers['content-type'] or 'octet-stream' in resp.headers['content-type']

    def test_xlsx_export_empty(self, client):
        resp = client.get('/api/v1/measurements/export/xlsx')
        assert resp.status_code == 200

    # ── Measurement API auth ──

    def test_post_measurement_no_auth(self, unauth_client):
        from app.config import settings
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
        from app.config import settings
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
        from app.config import settings
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
        from app.config import settings
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
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
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

    # ── Chart with granularity and time_range ──

    def test_chart_granularity_second(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/chart?granularity=s')
        assert resp.status_code == 200
        data = resp.json()
        assert 'labels' in data

    def test_chart_granularity_day(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/chart?granularity=d')
        assert resp.status_code == 200

    def test_chart_time_range_1h(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-auth', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/chart?range=1h')
        assert resp.status_code == 200

    def test_chart_time_range_24h(self, client, device_auth_header):
        resp = client.get('/api/v1/chart?range=24h')
        assert resp.status_code == 200

    def test_chart_time_range_7d(self, client, device_auth_header):
        resp = client.get('/api/v1/chart?range=7d')
        assert resp.status_code == 200

    def test_chart_time_range_30d(self, client, device_auth_header):
        resp = client.get('/api/v1/chart?range=30d')
        assert resp.status_code == 200

    def test_chart_invalid_granularity(self, client):
        resp = client.get('/api/v1/chart?granularity=x')
        assert resp.status_code == 200
        data = resp.json()
        assert 'voltage' in data

    # ── Device API extras ──

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

    # ── Dashboard API extras ──

    def test_dashboard_summary(self, client):
        resp = client.get('/api/v1/dashboard/summary')
        assert resp.status_code == 200
        data = resp.json()
        assert 'online_devices' in data
        assert 'offline_devices' in data
        assert 'active_sessions' in data

    def test_dashboard_statistics(self, client):
        resp = client.get('/api/v1/dashboard/statistics')
        assert resp.status_code == 200
        data = resp.json()
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data
        assert 'energy' in data

    def test_dashboard_statistics_with_filters(self, client):
        resp = client.get('/api/v1/dashboard/statistics?start_date=2000-01-01&end_date=2099-12-31')
        assert resp.status_code == 200

    def test_dashboard_no_measurements(self, client):
        resp = client.get('/api/v1/dashboard')
        assert resp.status_code == 200
        data = resp.json()
        assert data['stats']['energy']['total'] == 0


class TestFirmwareCompatibility:

    def _create_device(self, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
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
        from app.database import SessionLocal
        from app.models import Device
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
        from app.database import SessionLocal
        from app.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == '0.9.0'
        db.close()


class TestOwnerChecks:

    def _second_user_client(self, app):
        from app.database import SessionLocal
        from app.services.user_service import UserService
        from app.auth import create_access_token
        from fastapi.testclient import TestClient
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
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
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
        from app.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == 'unknown'
        db.close()

    def test_firmware_upgrade(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
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
        from app.models import Device
        db = SessionLocal()
        d = db.query(Device).filter_by(device_id='esp32-fw').first()
        assert d.firmware_version == '1.0.0'
        db.close()


class TestDeviceAuthDisabled:

    def test_measurement_no_auth_succeeds(self, unauth_client, app):
        from app.config import settings
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
        from app.config import settings
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
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
        from app.config import settings
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
        from app.config import settings
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


class TestApiExtras:

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
        from app.database import SessionLocal
        from app.models import Device
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
        from app.database import SessionLocal
        from app.models import Device
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
        from app.database import SessionLocal
        from app.models import Device, Project, User
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

    def test_post_measurement_service_error(self, client, device_auth_header):
        from unittest.mock import patch
        with patch('app.api.measurements.MeasurementService.create', side_effect=RuntimeError('db error')):
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth',
                'bus_voltage': 5.0,
                'shunt_voltage': 80,
                'current': 200,
                'power': 1000,
            }, headers=device_auth_header)
        assert resp.status_code == 500
        assert resp.json()['error'] == 'db error'
