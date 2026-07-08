import json


class TestAPI:
    def test_post_measurement_success(self, client):
        resp = client.post('/api/v1/measurements', json={
            'device_id': 'esp32-test',
            'bus_voltage': 5.12,
            'shunt_voltage': 82,
            'current': 241,
            'power': 1234,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'success'

    def test_post_measurement_missing_fields(self, client):
        resp = client.post('/api/v1/measurements', json={'device_id': 'esp32-test'})
        assert resp.status_code == 400

    def test_post_measurement_no_json(self, client):
        resp = client.post('/api/v1/measurements', data=b'{}', content_type='application/json')
        assert resp.status_code == 400

    def test_get_measurements_paginated(self, client):
        client.post('/api/v1/measurements', json={
            'device_id': 'esp32-test', 'bus_voltage': 5.0, 'shunt_voltage': 80,
            'current': 200, 'power': 1000,
        })
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
        devices = resp.get_json()
        assert any(dev['device_id'] == 'esp32-crud' for dev in devices)

        resp = client.put(f'/api/v1/devices/{d["id"]}', json={'alias': 'Updated Alias'})
        assert resp.status_code == 200
        assert resp.get_json()['alias'] == 'Updated Alias'

        resp = client.delete(f'/api/v1/devices/{d["id"]}')
        assert resp.status_code == 200

    def test_session_crud(self, client):
        client.post('/api/v1/devices', json={
            'device_id': 'esp32-session',
            'alias': 'Session Device',
        })
        resp = client.post('/api/v1/sessions', json={
            'device_id': 1,
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
        assert b'PowerDash' in resp.data

    def test_devices_page(self, client):
        resp = client.get('/devices')
        assert resp.status_code == 200

    def test_sessions_page(self, client):
        resp = client.get('/sessions')
        assert resp.status_code == 200

    def test_measurements_page(self, client):
        resp = client.get('/measurements')
        assert resp.status_code == 200
