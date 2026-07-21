class TestMeasurementsAPI:
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
        from src.database import SessionLocal
        from src.measurements.models import Measurement
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
        from src.database import SessionLocal
        from src.measurements.models import Measurement
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

    def test_get_chart_data(self, client):
        resp = client.get('/api/v1/chart?limit=10')
        assert resp.status_code == 200
        data = resp.json()
        assert 'labels' in data
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data
        assert 'energy' in data

    def test_measurements_page(self, client):
        resp = client.get('/measurements')
        assert resp.status_code == 200

    def test_measurements_empty(self, client):
        resp = client.get('/api/v1/measurements')
        assert resp.status_code == 200
        data = resp.json()
        assert data['measurements'] == []
        assert data['total'] == 0

    def test_measurements_filter_by_device(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
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
        from src.database import SessionLocal
        from src.devices.service import DeviceService
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



class TestMeasurementsExtra:
    def test_post_measurement_service_error(self, client, device_auth_header):
        from unittest.mock import patch
        with patch('src.measurements.service.MeasurementService.create', side_effect=RuntimeError('db error')):
            resp = client.post('/api/v1/measurements', json={
                'device_id': 'esp32-auth',
                'bus_voltage': 5.0,
                'shunt_voltage': 80,
                'current': 200,
                'power': 1000,
            }, headers=device_auth_header)
        assert resp.status_code == 500
        assert resp.json()['error'] == 'db error'



class TestMeasurementsExtra:
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
