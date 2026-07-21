class TestBenchmarkCompare:
    def test_compare_missing_sessions(self, client):
        resp = client.get('/api/v1/benchmark/compare')
        assert resp.status_code == 400
        assert 'sessions' in resp.json()['error']

    def test_compare_fewer_than_two(self, client):
        resp = client.get('/api/v1/benchmark/compare?sessions=1')
        assert resp.status_code == 400

    def test_compare_more_than_three(self, client):
        resp = client.get('/api/v1/benchmark/compare?sessions=1,2,3,4')
        assert resp.status_code == 400

    def test_compare_invalid_ids(self, client):
        resp = client.get('/api/v1/benchmark/compare?sessions=abc,def')
        assert resp.status_code == 400

    def test_compare_valid(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        from src.sessions.service import SessionService
        from src.measurements.service import MeasurementService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-bench')
        s1 = SessionService(db).create(d.id, 'Bench 1')
        s2 = SessionService(db).create(d.id, 'Bench 2')
        SessionService(db).start(s1.id)
        SessionService(db).start(s2.id)
        MeasurementService(db).create('esp32-bench', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService(db).create('esp32-bench', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id = s1.id, s2.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions={s1_id},{s2_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['sessions']) == 2
        for s in data['sessions']:
            assert 'avg_power' in s
            assert 'peak_power' in s
            assert 'total_energy' in s
            assert 'chart_data' in s
            assert 'labels' in s['chart_data']
            assert 'power' in s['chart_data']
            assert isinstance(s['chart_data']['labels'], list)
            assert isinstance(s['chart_data']['power'], list)

    def test_compare_three_sessions(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        from src.sessions.service import SessionService
        from src.measurements.service import MeasurementService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-bench3')
        s1 = SessionService(db).create(d.id, 'Bench A')
        s2 = SessionService(db).create(d.id, 'Bench B')
        s3 = SessionService(db).create(d.id, 'Bench C')
        SessionService(db).start(s1.id)
        SessionService(db).start(s2.id)
        SessionService(db).start(s3.id)
        MeasurementService(db).create('esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService(db).create('esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService(db).create('esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id, s3_id = s1.id, s2.id, s3.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions={s1_id},{s2_id},{s3_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['sessions']) == 3

    def test_compare_non_numeric_skipped(self, client, app):
        from src.database import SessionLocal
        from src.devices.service import DeviceService
        from src.sessions.service import SessionService
        from src.measurements.service import MeasurementService
        db = SessionLocal()
        d = DeviceService(db).create('esp32-bench2')
        s1 = SessionService(db).create(d.id, 'Bench A')
        s2 = SessionService(db).create(d.id, 'Bench B')
        SessionService(db).start(s1.id)
        SessionService(db).start(s2.id)
        MeasurementService(db).create('esp32-bench2', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id = s1.id, s2.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions=abc,{s1_id},{s2_id}')
        assert resp.status_code == 200
        assert len(resp.json()['sessions']) == 2
