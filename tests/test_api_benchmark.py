class TestBenchmarkAPI:
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
        assert resp.status_code == 404

    def test_compare_valid(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
        from app.services.session_service import SessionService
        from app.services.measurement_service import MeasurementService
        db = SessionLocal()
        d = DeviceService.create(db, 'esp32-bench')
        s1 = SessionService.create(db, d.id, 'Bench 1')
        s2 = SessionService.create(db, d.id, 'Bench 2')
        SessionService.start(db, s1.id)
        SessionService.start(db, s2.id)
        MeasurementService.create(db, 'esp32-bench', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService.create(db, 'esp32-bench', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id = s1.id, s2.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions={s1_id},{s2_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['sessions']) == 2

    def test_compare_three_sessions(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
        from app.services.session_service import SessionService
        from app.services.measurement_service import MeasurementService
        db = SessionLocal()
        d = DeviceService.create(db, 'esp32-bench3')
        s1 = SessionService.create(db, d.id, 'Bench A')
        s2 = SessionService.create(db, d.id, 'Bench B')
        s3 = SessionService.create(db, d.id, 'Bench C')
        SessionService.start(db, s1.id)
        SessionService.start(db, s2.id)
        SessionService.start(db, s3.id)
        MeasurementService.create(db, 'esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService.create(db, 'esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService.create(db, 'esp32-bench3', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id, s3_id = s1.id, s2.id, s3.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions={s1_id},{s2_id},{s3_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['sessions']) == 3

    def test_compare_non_numeric_skipped(self, client, app):
        from app.database import SessionLocal
        from app.services.device_service import DeviceService
        from app.services.session_service import SessionService
        from app.services.measurement_service import MeasurementService
        db = SessionLocal()
        d = DeviceService.create(db, 'esp32-bench2')
        s1 = SessionService.create(db, d.id, 'Bench A')
        s2 = SessionService.create(db, d.id, 'Bench B')
        SessionService.start(db, s1.id)
        SessionService.start(db, s2.id)
        MeasurementService.create(db, 'esp32-bench2', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        s1_id, s2_id = s1.id, s2.id
        db.close()
        resp = client.get(f'/api/v1/benchmark/compare?sessions=abc,{s1_id},{s2_id}')
        assert resp.status_code == 200
        assert len(resp.json()['sessions']) == 2
