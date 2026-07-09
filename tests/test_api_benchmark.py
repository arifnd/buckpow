class TestBenchmarkAPI:
    def test_compare_missing_sessions(self, client):
        resp = client.get('/api/v1/benchmark/compare')
        assert resp.status_code == 400
        assert 'sessions' in resp.get_json()['error']

    def test_compare_fewer_than_two(self, client):
        resp = client.get('/api/v1/benchmark/compare?sessions=1')
        assert resp.status_code == 400

    def test_compare_invalid_ids(self, client):
        resp = client.get('/api/v1/benchmark/compare?sessions=abc,def')
        assert resp.status_code == 404

    def test_compare_valid(self, client, app):
        with app.app_context():
            from app import db
            from app.services.device_service import DeviceService
            from app.services.session_service import SessionService
            from app.services.measurement_service import MeasurementService
            db.session.expire_on_commit = False
            d = DeviceService.create('esp32-bench')
            s1 = SessionService.create(d.id, 'Bench 1')
            s2 = SessionService.create(d.id, 'Bench 2')
            SessionService.start(s1.id)
            SessionService.start(s2.id)
            MeasurementService.create('esp32-bench', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            MeasurementService.create('esp32-bench', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            s1_id, s2_id = s1.id, s2.id
        resp = client.get(f'/api/v1/benchmark/compare?sessions={s1_id},{s2_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['sessions']) == 2

    def test_compare_non_numeric_skipped(self, client, app):
        with app.app_context():
            from app import db
            from app.services.device_service import DeviceService
            from app.services.session_service import SessionService
            from app.services.measurement_service import MeasurementService
            db.session.expire_on_commit = False
            d = DeviceService.create('esp32-bench2')
            s1 = SessionService.create(d.id, 'Bench A')
            s2 = SessionService.create(d.id, 'Bench B')
            SessionService.start(s1.id)
            SessionService.start(s2.id)
            MeasurementService.create('esp32-bench2', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            s1_id, s2_id = s1.id, s2.id
        resp = client.get(f'/api/v1/benchmark/compare?sessions=abc,{s1_id},{s2_id}')
        assert resp.status_code == 200
        assert len(resp.get_json()['sessions']) == 2
