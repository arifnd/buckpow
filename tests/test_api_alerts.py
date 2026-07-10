class TestAlertsAPI:
    def test_create_alert(self, client, sample_device_id):
        resp = client.post('/api/v1/alerts', json={
            'device_id': sample_device_id,
            'level': 'critical',
            'message': 'High power detected',
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data['level'] == 'critical'
        assert data['message'] == 'High power detected'

    def test_create_alert_missing_fields(self, client):
        resp = client.post('/api/v1/alerts', json={'device_id': 1})
        assert resp.status_code == 422

    def test_list_alerts(self, client, sample_device_id):
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'A'})
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'B'})
        resp = client.get('/api/v1/alerts')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] >= 2

    def test_list_alerts_filter_device(self, client, sample_device_id, app):
        from app.database import SessionLocal
        from app.models import Device
        from app.services.device_service import DeviceService
        db = SessionLocal()
        d2 = DeviceService.create(db, 'esp32-alert-other')
        d2_id = d2.id
        db.close()
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'Dev1'})
        client.post('/api/v1/alerts', json={'device_id': d2_id, 'message': 'Dev2'})
        resp = client.get(f'/api/v1/alerts?device_id={sample_device_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1

    def test_list_alerts_filter_level(self, client, sample_device_id):
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'W',
                                             'level': 'warning'})
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'I',
                                             'level': 'info'})
        resp = client.get('/api/v1/alerts?level=warning')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1

    def test_list_alerts_filter_resolved(self, client, sample_device_id):
        created = client.post('/api/v1/alerts', json={
            'device_id': sample_device_id, 'message': 'Resolve me'
        }).json()
        client.patch(f'/api/v1/alerts/{created["id"]}/resolve')
        resp = client.get('/api/v1/alerts?resolved=true')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] >= 1

    def test_list_alerts_unresolved_count(self, client, sample_device_id):
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'Urgent'})
        resp = client.get('/api/v1/alerts')
        assert resp.status_code == 200
        data = resp.json()
        assert data['unresolved_count'] >= 1

    def test_resolve_alert(self, client, sample_device_id):
        created = client.post('/api/v1/alerts', json={
            'device_id': sample_device_id, 'message': 'To resolve'
        }).json()
        resp = client.patch(f'/api/v1/alerts/{created["id"]}/resolve')
        assert resp.status_code == 200
        assert resp.json()['resolved_at'] is not None

    def test_resolve_alert_not_found(self, client):
        resp = client.patch('/api/v1/alerts/99999/resolve')
        assert resp.status_code == 404

    def test_resolve_all(self, client, sample_device_id):
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'A'})
        client.post('/api/v1/alerts', json={'device_id': sample_device_id, 'message': 'B'})
        resp = client.post('/api/v1/alerts/resolve-all')
        assert resp.status_code == 200
        assert resp.json() == {'status': 'ok'}
        resp = client.get('/api/v1/alerts')
        assert resp.json()['unresolved_count'] == 0
