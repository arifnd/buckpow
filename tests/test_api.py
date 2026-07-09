import json


class TestAPI:
    def test_post_measurement_success(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-test',
            'bus_voltage': 5.12,
            'shunt_voltage': 82,
            'current': 241,
            'power': 1234,
        }, headers=device_auth_header)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'success'

    def test_post_measurement_missing_fields(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', json={'device_id': 'esp32-test'},
                           headers=device_auth_header)
        assert resp.status_code == 400

    def test_post_measurement_no_json(self, client, device_auth_header):
        resp = client.post('/api/v1/measurements', data=b'{}', content_type='application/json',
                           headers=device_auth_header)
        assert resp.status_code == 400

    def test_get_measurements_paginated(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-test', 'bus_voltage': 5.0, 'shunt_voltage': 80,
            'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements?per_page=10')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['measurements']) >= 1
        assert data['total'] >= 1

    def test_get_dashboard(self, client):
        resp = client.get('/api/v1/dashboard')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'devices' in data
        assert 'stats' in data

    def test_get_chart_data(self, client):
        resp = client.get('/api/v1/chart?limit=10')
        assert resp.status_code == 200
        data = resp.get_json()
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
        d = resp.get_json()
        assert d['device_id'] == 'esp32-crud'

        resp = client.get('/api/v1/devices')
        assert resp.status_code == 200
        data = resp.get_json()
        assert any(dev['device_id'] == 'esp32-crud' for dev in data['devices'])

        resp = client.put(f'/api/v1/devices/{d["id"]}', json={'alias': 'Updated Alias'})
        assert resp.status_code == 200
        assert resp.get_json()['alias'] == 'Updated Alias'

        resp = client.delete(f'/api/v1/devices/{d["id"]}')
        assert resp.status_code == 200

    def test_session_crud(self, client):
        d = client.post('/api/v1/devices', json={
            'device_id': 'esp32-session',
            'alias': 'Session Device',
        }).get_json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'],
            'name': 'Test Session',
            'target_device': 'esp32-session',
        })
        assert resp.status_code == 201
        s = resp.get_json()
        assert s['name'] == 'Test Session'
        assert s['status'] == 'draft'

        resp = client.post(f'/api/v1/sessions/{s["id"]}/start')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'running'

        resp = client.post(f'/api/v1/sessions/{s["id"]}/stop')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'finished'

    def test_dashboard_page(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'BakPow' in resp.data

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
        d = resp.get_json()
        resp = client.get(f'/api/v1/devices/{d["id"]}')
        assert resp.status_code == 200
        assert resp.get_json()['device_id'] == 'esp32-single'

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
        assert resp.status_code == 400
        assert 'device_id is required' in resp.get_json()['error']

    def test_device_create_no_json(self, client):
        resp = client.post('/api/v1/devices', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_device_pagination(self, client):
        for i in range(15):
            client.post('/api/v1/devices', json={'device_id': f'esp32-page-{i}'})
        resp = client.get('/api/v1/devices?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['devices']) == 5
        assert data['total'] == 15
        assert data['pages'] == 3
        assert data['page'] == 1

    def test_device_page_zero_returns_all(self, client):
        for i in range(3):
            client.post('/api/v1/devices', json={'device_id': f'esp32-all-{i}'})
        resp = client.get('/api/v1/devices?page=0')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

    # ── Session API edge cases ──

    def test_session_get_single(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-single-sess'}).get_json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Single Session',
        })
        s = resp.get_json()
        resp = client.get(f'/api/v1/sessions/{s["id"]}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Single Session'

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
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-missing-name'}).get_json()
        resp = client.post('/api/v1/sessions', json={'device_id': d['id']})
        assert resp.status_code == 400
        assert 'name' in resp.get_json()['error']

    def test_session_create_missing_device_id(self, client):
        resp = client.post('/api/v1/sessions', json={'name': 'No Device'})
        assert resp.status_code == 400

    def test_session_create_no_json(self, client):
        resp = client.post('/api/v1/sessions', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_session_start_nonexistent(self, client):
        resp = client.post('/api/v1/sessions/99999/start')
        assert resp.status_code == 400

    def test_session_stop_nonexistent(self, client):
        resp = client.post('/api/v1/sessions/99999/stop')
        assert resp.status_code == 400

    def test_session_stop_not_running(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-stop'}).get_json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Draft Session',
        })
        s = resp.get_json()
        assert s['status'] == 'draft'
        resp = client.post(f'/api/v1/sessions/{s["id"]}/stop')
        assert resp.status_code == 400

    def test_session_start_already_running(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-start'}).get_json()
        resp = client.post('/api/v1/sessions', json={
            'device_id': d['id'], 'name': 'Session A',
        })
        a = resp.get_json()
        resp = client.post(f'/api/v1/sessions/{a["id"]}/start')
        assert resp.status_code == 200
        resp = client.post(f'/api/v1/sessions/{a["id"]}/start')
        assert resp.status_code == 400

    def test_session_pagination(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-sess-page'}).get_json()
        for i in range(15):
            client.post('/api/v1/sessions', json={
                'device_id': d['id'], 'name': f'Session {i}',
            })
        resp = client.get('/api/v1/sessions?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['sessions']) == 5
        assert data['total'] == 15
        assert data['pages'] == 3

    def test_session_page_zero_returns_all(self, client):
        d = client.post('/api/v1/devices', json={'device_id': 'esp32-sess-all'}).get_json()
        for i in range(3):
            client.post('/api/v1/sessions', json={
                'device_id': d['id'], 'name': f'Sess {i}',
            })
        resp = client.get('/api/v1/sessions?page=0')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

    # ── Measurements API edge cases ──

    def test_measurements_empty(self, client):
        resp = client.get('/api/v1/measurements')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['measurements'] == []
        assert data['total'] == 0

    def test_measurements_filter_by_device(self, client, device_auth_header):
        ra = client.post('/api/v1/devices', json={'device_id': 'esp32-filt-a'})
        rb = client.post('/api/v1/devices', json={'device_id': 'esp32-filt-b'})
        dev_a_id = ra.get_json()['id']
        dev_b_id = rb.get_json()['id']
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-filt-a', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-filt-b', 'bus_voltage': 6.0,
            'shunt_voltage': 90, 'current': 300, 'power': 2000,
        }, headers=device_auth_header)
        resp = client.get(f'/api/v1/measurements?device_id={dev_b_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['measurements']) == 1

    def test_csv_export(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-csv', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements/export/csv')
        assert resp.status_code == 200
        assert resp.content_type == 'text/csv; charset=utf-8'
        assert b'Device' in resp.data
        assert b'esp32-csv' in resp.data

    def test_csv_export_empty(self, client):
        resp = client.get('/api/v1/measurements/export/csv')
        assert resp.status_code == 200
        assert resp.content_type == 'text/csv; charset=utf-8'
        lines = resp.data.decode().strip().split('\n')
        assert len(lines) == 1

    def test_chart_data_with_filters(self, client, device_auth_header):
        dev_resp = client.post('/api/v1/devices', json={'device_id': 'esp32-chart'})
        dev_id = dev_resp.get_json()['id']
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-chart', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get(f'/api/v1/chart?limit=5&device_id={dev_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['labels']) == 1

    def test_get_measurements_with_date_range(self, client, device_auth_header):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-date', 'bus_voltage': 5.0,
            'shunt_voltage': 80, 'current': 200, 'power': 1000,
        }, headers=device_auth_header)
        resp = client.get('/api/v1/measurements?start_date=2000-01-01&end_date=2099-12-31')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['measurements']) >= 1

    # ── Dashboard ──

    def test_dashboard_no_measurements(self, client):
        resp = client.get('/api/v1/dashboard')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['stats']['energy']['total'] == 0
