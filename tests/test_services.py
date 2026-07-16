from datetime import datetime, timezone, timedelta

from app.database import SessionLocal
from app.models import Device, Session, Measurement, User, Project, Alert
from app.services.user_service import UserService
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.services.measurement_service import MeasurementService
from app.services.alert_service import AlertService
from app.services.project_service import ProjectService
from app.services.dashboard_service import DashboardService


class TestUserService:
    def _db(self, app):
        return SessionLocal()

    def test_create_user(self, app):
        db = self._db(app)
        u = UserService.create(db, name='Test', email='test@example.com', password='secret')
        assert u.id is not None
        assert u.name == 'Test'
        assert u.email == 'test@example.com'
        assert u.check_password('secret')
        db.close()

    def test_create_duplicate_email(self, app):
        import pytest
        db = self._db(app)
        UserService.create(db, name='A', email='dup@example.com', password='x')
        with pytest.raises(ValueError, match='already exists'):
            UserService.create(db, name='B', email='dup@example.com', password='y')
        db.close()

    def test_authenticate_success(self, app):
        db = self._db(app)
        UserService.create(db, name='Auth', email='auth@example.com', password='pass')
        u = UserService.authenticate(db, 'auth@example.com', 'pass')
        assert u is not None
        assert u.name == 'Auth'
        db.close()

    def test_authenticate_wrong_password(self, app):
        db = self._db(app)
        UserService.create(db, name='Auth', email='auth2@example.com', password='pass')
        u = UserService.authenticate(db, 'auth2@example.com', 'wrong')
        assert u is None
        db.close()

    def test_authenticate_nonexistent(self, app):
        db = self._db(app)
        u = UserService.authenticate(db, 'nobody@example.com', 'pass')
        assert u is None
        db.close()

    def test_update_user(self, app):
        db = self._db(app)
        u = UserService.create(db, name='Old', email='old@example.com', password='x')
        updated = UserService.update(db, u.id, name='New', email='new@example.com')
        assert updated.name == 'New'
        assert updated.email == 'new@example.com'
        db.close()

    def test_update_email_already_in_use(self, app):
        import pytest
        db = self._db(app)
        UserService.create(db, name='A', email='a@example.com', password='x')
        b = UserService.create(db, name='B', email='b@example.com', password='x')
        with pytest.raises(ValueError, match='already in use'):
            UserService.update(db, b.id, email='a@example.com')
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = UserService.update(db, 99999, name='Ghost')
        assert result is None
        db.close()

    def test_update_password(self, app):
        db = self._db(app)
        u = UserService.create(db, name='Pwd', email='pwd@example.com', password='old')
        UserService.update(db, u.id, password='new')
        assert u.check_password('new')
        db.close()

    def test_get_by_id(self, app):
        db = self._db(app)
        u = UserService.create(db, name='ByID', email='byid@example.com', password='x')
        found = UserService.get_by_id(db, u.id)
        assert found is not None
        assert found.email == 'byid@example.com'
        db.close()

    def test_get_by_email(self, app):
        db = self._db(app)
        UserService.create(db, name='ByEmail', email='byemail@example.com', password='x')
        found = UserService.get_by_email(db, 'byemail@example.com')
        assert found is not None
        db.close()


class TestDeviceService:
    def _db(self, app):
        return SessionLocal()

    def test_create_device(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-svc-1', alias='Svc Device')
        assert d.id is not None
        assert d.device_id == 'esp32-svc-1'
        assert d.alias == 'Svc Device'
        assert d.enabled is True
        assert d.api_key is not None
        db.close()

    def test_get_by_device_id(self, app):
        db = self._db(app)
        DeviceService.create(db, 'esp32-find')
        d = DeviceService.get_by_device_id(db, 'esp32-find')
        assert d is not None
        db.close()

    def test_get_by_device_id_not_found(self, app):
        db = self._db(app)
        d = DeviceService.get_by_device_id(db, 'nonexistent')
        assert d is None
        db.close()

    def test_get_by_api_key(self, app):
        db = self._db(app)
        device = DeviceService.create(db, 'esp32-key')
        found = DeviceService.get_by_api_key(db, device.api_key)
        assert found is not None
        assert found.id == device.id
        db.close()

    def test_get_by_api_key_invalid(self, app):
        db = self._db(app)
        found = DeviceService.get_by_api_key(db, 'invalid-key')
        assert found is None
        db.close()

    def test_get_or_create_existing(self, app):
        db = self._db(app)
        DeviceService.create(db, 'esp32-goc')
        d = DeviceService.get_or_create(db, 'esp32-goc')
        assert d.device_id == 'esp32-goc'
        db.close()

    def test_get_or_create_new(self, app):
        db = self._db(app)
        d = DeviceService.get_or_create(db, 'esp32-new')
        assert d.device_id == 'esp32-new'
        db.close()

    def test_touch(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-touch')
        assert d.last_seen is None
        DeviceService.touch(db, 'esp32-touch')
        assert d.last_seen is not None
        db.close()

    def test_touch_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService.touch(db, 'nonexistent')
        assert result is None
        db.close()

    def test_regenerate_api_key(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-reg')
        old_key = d.api_key
        DeviceService.regenerate_api_key(db, d.id)
        assert d.api_key != old_key
        db.close()

    def test_regenerate_api_key_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService.regenerate_api_key(db, 99999)
        assert result is None
        db.close()

    def test_toggle_enabled(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-toggle')
        assert d.enabled is True
        DeviceService.toggle_enabled(db, d.id)
        assert d.enabled is False
        DeviceService.toggle_enabled(db, d.id)
        assert d.enabled is True
        db.close()

    def test_toggle_enabled_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService.toggle_enabled(db, 99999)
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-del')
        did = d.id
        assert DeviceService.delete(db, did) is True
        assert DeviceService.get_by_id(db, did) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert DeviceService.delete(db, 99999) is False
        db.close()

    def test_get_online_status_offline_no_last_seen(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-stat')
        assert DeviceService.get_online_status(d) == 'offline'
        db.close()

    def test_get_online_status_online(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-stat-on')
        d.last_seen = datetime.now(timezone.utc)
        assert DeviceService.get_online_status(d) == 'online'
        db.close()

    def test_get_online_status_expired(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-stat-off')
        d.last_seen = datetime.now(timezone.utc) - timedelta(seconds=180)
        assert DeviceService.get_online_status(d) == 'offline'
        db.close()

    def test_update(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-upd')
        DeviceService.update(db, d.id, alias='Updated', description='Desc')
        assert d.alias == 'Updated'
        assert d.description == 'Desc'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService.update(db, 99999, alias='Ghost')
        assert result is None
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        DeviceService.create(db, 'esp32-all-a')
        DeviceService.create(db, 'esp32-all-b')
        assert len(DeviceService.get_all(db)) >= 2
        db.close()

    def test_get_paginated(self, app):
        from sqlalchemy import insert
        from app.models import Device
        db = self._db(app)
        db.execute(insert(Device), [
            {'device_id': f'esp32-page-{i}', 'api_key': DeviceService.generate_api_key()}
            for i in range(5)
        ])
        db.commit()
        p = DeviceService.get_paginated(db, page=1, per_page=2)
        assert len(p.items) == 2
        assert p.total >= 5
        db.close()


class TestSessionService:
    def _db(self, app):
        return SessionLocal()

    def test_create_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-sess-svc')
        s = SessionService.create(db, device_id=d.id, name='Test Session')
        assert s.id is not None
        assert s.status == 'draft'
        db.close()

    def test_create_with_all_fields(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-sess-full')
        s = SessionService.create(db, device_id=d.id, name='Full', target_device='t1',
                                  description='desc')
        assert s.target_device == 't1'
        assert s.description == 'desc'
        db.close()

    def test_start_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-start')
        s = SessionService.create(db, d.id, 'Start')
        session, error = SessionService.start(db, s.id)
        assert error is None
        assert session.status == 'running'
        db.close()

    def test_start_nonexistent(self, app):
        db = self._db(app)
        session, error = SessionService.start(db, 99999)
        assert session is None
        assert error == 'Session not found'
        db.close()

    def test_start_already_running(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-already')
        s = SessionService.create(db, d.id, 'Running')
        SessionService.start(db, s.id)
        session, error = SessionService.start(db, s.id)
        assert session is None
        assert error == 'Session is already running'
        db.close()

    def test_stop_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-stop')
        s = SessionService.create(db, d.id, 'Stop')
        SessionService.start(db, s.id)
        session, error = SessionService.stop(db, s.id)
        assert error is None
        assert session.status == 'finished'
        db.close()

    def test_stop_nonexistent(self, app):
        db = self._db(app)
        session, error = SessionService.stop(db, 99999)
        assert session is None
        assert error == 'Session not found'
        db.close()

    def test_stop_not_running(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-stop2')
        s = SessionService.create(db, d.id, 'Draft')
        session, error = SessionService.stop(db, s.id)
        assert session is None
        assert error == 'Session is not running'
        db.close()

    def test_get_active_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-act')
        s = SessionService.create(db, d.id, 'Active')
        SessionService.start(db, s.id)
        active = SessionService.get_active_session(db, d.id)
        assert active is not None
        assert active.id == s.id
        db.close()

    def test_auto_stop_other_on_start(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-auto')
        a = SessionService.create(db, d.id, 'Session A')
        b = SessionService.create(db, d.id, 'Session B')
        SessionService.start(db, a.id)
        assert a.status == 'running'
        result, err = SessionService.start(db, b.id)
        assert result is None
        assert err == 'A session is already running for this device'
        assert a.status == 'running'
        db.close()

    def test_multiple_devices_can_run_concurrently(self, app):
        db = self._db(app)
        d1 = DeviceService.create(db, 'esp32-d1')
        d2 = DeviceService.create(db, 'esp32-d2')
        a = SessionService.create(db, d1.id, 'Session A')
        b = SessionService.create(db, d2.id, 'Session B')
        SessionService.start(db, a.id)
        assert a.status == 'running'
        SessionService.start(db, b.id)
        assert b.status == 'running'
        assert a.status == 'running'
        db.close()

    def test_get_for_device(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-gfd')
        SessionService.create(db, d.id, 'S1')
        SessionService.create(db, d.id, 'S2')
        sessions = SessionService.get_for_device(db, d.id)
        assert len(sessions) == 2
        db.close()

    def test_update(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-up')
        s = SessionService.create(db, d.id, 'Original')
        SessionService.update(db, s.id, name='Updated')
        assert s.name == 'Updated'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = SessionService.update(db, 99999, name='Ghost')
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-del-s')
        s = SessionService.create(db, d.id, 'To Delete')
        sid = s.id
        assert SessionService.delete(db, sid) is True
        assert SessionService.get_by_id(db, sid) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert SessionService.delete(db, 99999) is False
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-all-s')
        SessionService.create(db, d.id, 'A')
        SessionService.create(db, d.id, 'B')
        assert len(SessionService.get_all(db)) >= 2
        db.close()


class TestMeasurementService:
    def _db(self, app):
        return SessionLocal()

    def test_create_measurement(self, app):
        db = self._db(app)
        m = MeasurementService.create(db, 'esp32-meas-svc', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.id is not None
        assert m.load_voltage == 5.08
        assert m.current == 0.2
        assert m.power == 1.0
        db.close()

    def test_create_auto_registers_device(self, app):
        db = self._db(app)
        m = MeasurementService.create(db, 'esp32-auto-reg', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        device = DeviceService.get_by_device_id(db, 'esp32-auto-reg')
        assert device is not None
        assert m.device_id == device.id
        db.close()

    def test_create_with_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-sess-m')
        s = SessionService.create(db, d.id, 'Meas Session')
        SessionService.start(db, s.id)
        m = MeasurementService.create(db, 'esp32-sess-m', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.session_id == s.id
        db.close()

    def test_energy_accumulation_same_session(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-energy')
        s = SessionService.create(db, d.id, 'Energy')
        SessionService.start(db, s.id)
        m1 = MeasurementService.create(db, 'esp32-energy', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        m2 = MeasurementService.create(db, 'esp32-energy', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        assert m2.energy > m1.energy
        db.close()

    def test_energy_no_session_starts_at_zero(self, app):
        db = self._db(app)
        m = MeasurementService.create(db, 'esp32-no-sess', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.energy == 0.0
        db.close()

    def test_get_recent(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-recent', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        recent = MeasurementService.get_recent(db, limit=10)
        assert len(recent) >= 1
        db.close()

    def test_get_stats_empty(self, app):
        db = self._db(app)
        stats = MeasurementService.get_stats(db)
        assert stats['energy']['total'] == 0
        db.close()

    def test_get_stats_with_data(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-stats', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = MeasurementService.get_stats(db)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_chart_data_no_granularity(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-chart-svc', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService.get_chart_data(db, limit=10)
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_with_granularity_hour(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-gran', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService.get_chart_data(db, limit=10, granularity='h')
        assert len(data['labels']) >= 1
        db.close()

    def test_get_session_stats_empty(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-ss-empty')
        s = SessionService.create(db, d.id, 'Empty Session')
        stats = MeasurementService.get_session_stats(db, s.id)
        assert stats is not None
        assert stats['measurement_count'] == 0
        db.close()

    def test_get_session_stats_with_data(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-ss-data')
        s = SessionService.create(db, d.id, 'Data Session')
        SessionService.start(db, s.id)
        MeasurementService.create(db, 'esp32-ss-data', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = MeasurementService.get_session_stats(db, s.id)
        assert stats['measurement_count'] == 1
        assert stats['avg_power'] > 0
        db.close()

    def test_get_session_stats_nonexistent(self, app):
        db = self._db(app)
        stats = MeasurementService.get_session_stats(db, 99999)
        assert stats is None
        db.close()

    def test_get_paginated(self, app):
        db = self._db(app)
        for i in range(3):
            MeasurementService.create(db, f'esp32-pag-{i}', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        p = MeasurementService.get_paginated(db, page=1, per_page=2)
        assert len(p.items) == 2
        db.close()

    def test_get_all_filtered(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        rows = MeasurementService.get_all_filtered(db)
        assert len(rows) >= 1
        db.close()


class TestAlertService:
    def _db(self, app):
        return SessionLocal()

    def test_create_alert(self, app, sample_device_id):
        db = self._db(app)
        a = AlertService.create(db, device_id=sample_device_id, level='critical',
                                message='Test alert')
        assert a.id is not None
        assert a.level == 'critical'
        db.close()

    def test_get_paginated(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='A1')
        AlertService.create(db, device_id=sample_device_id, level='info', message='A2')
        p = AlertService.get_paginated(db, page=1, per_page=10)
        assert len(p.items) >= 2
        db.close()

    def test_get_paginated_filter_device(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='F1')
        p = AlertService.get_paginated(db, page=1, per_page=10, device_id=sample_device_id)
        assert len(p.items) == 1
        db.close()

    def test_get_paginated_filter_level(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='W')
        AlertService.create(db, device_id=sample_device_id, level='info', message='I')
        p = AlertService.get_paginated(db, page=1, per_page=10, level='info')
        assert len(p.items) == 1
        db.close()

    def test_get_paginated_filter_unresolved(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='Unres')
        p = AlertService.get_paginated(db, page=1, per_page=10, resolved=False)
        assert len(p.items) >= 1
        db.close()

    def test_resolve(self, app, sample_device_id):
        db = self._db(app)
        a = AlertService.create(db, device_id=sample_device_id, level='warning', message='Resolve me')
        assert a.resolved_at is None
        resolved = AlertService.resolve(db, a.id)
        assert resolved.resolved_at is not None
        db.close()

    def test_resolve_nonexistent(self, app):
        db = self._db(app)
        result = AlertService.resolve(db, 99999)
        assert result is None
        db.close()

    def test_resolve_all(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='A')
        AlertService.create(db, device_id=sample_device_id, level='info', message='B')
        AlertService.resolve_all(db)
        count = AlertService.get_unresolved_count(db)
        assert count == 0
        db.close()

    def test_get_unresolved_count(self, app, sample_device_id):
        db = self._db(app)
        AlertService.create(db, device_id=sample_device_id, level='warning', message='Urgent')
        assert AlertService.get_unresolved_count(db) >= 1
        db.close()

    def test_generate_alerts_high_power(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-alert-hp', high_power_threshold=1.0)
        AlertService.generate_alerts(db, d, bus_voltage=5.0, current=0.1, power=2.0)
        unresolved = AlertService.get_unresolved_count(db, device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_high_current(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-alert-hc', high_current_threshold=0.3)
        AlertService.generate_alerts(db, d, bus_voltage=5.0, current=0.5, power=0.5)
        unresolved = AlertService.get_unresolved_count(db, device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_low_voltage(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-alert-lv', low_voltage_threshold=4.0)
        AlertService.generate_alerts(db, d, bus_voltage=3.5, current=0.1, power=0.5)
        unresolved = AlertService.get_unresolved_count(db, device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_no_duplicates(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-alert-nd', high_power_threshold=1.0)
        AlertService.generate_alerts(db, d, bus_voltage=5.0, current=0.1, power=2.0)
        AlertService.generate_alerts(db, d, bus_voltage=5.0, current=0.1, power=2.0)
        unresolved = AlertService.get_unresolved_count(db, device_id=d.id)
        alerts = db.query(Alert).filter_by(device_id=d.id, resolved_at=None).all()
        high_power_count = sum(1 for a in alerts if 'High power' in a.message)
        assert high_power_count == 1
        db.close()


class TestProjectService:
    def _db(self, app):
        return SessionLocal()

    def test_create_project(self, app):
        db = self._db(app)
        p = ProjectService.create(db, name='Test Project', description='Desc')
        assert p.id is not None
        assert p.name == 'Test Project'
        db.close()

    def test_create_with_owner(self, app):
        db = self._db(app)
        user = db.query(User).first()
        p = ProjectService.create(db, name='Owned', owner_id=user.id)
        assert p.owner_id == user.id
        db.close()

    def test_get_by_id(self, app):
        db = self._db(app)
        p = ProjectService.create(db, name='Find Me')
        found = ProjectService.get_by_id(db, p.id)
        assert found is not None
        db.close()

    def test_get_by_id_nonexistent(self, app):
        db = self._db(app)
        p = ProjectService.get_by_id(db, 99999)
        assert p is None
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        ProjectService.create(db, name='A')
        ProjectService.create(db, name='B')
        assert len(ProjectService.get_all(db)) >= 2
        db.close()

    def test_get_paginated(self, app):
        from sqlalchemy import insert
        from app.models import Project
        db = self._db(app)
        db.execute(insert(Project), [{'name': f'Project {i}'} for i in range(5)])
        db.commit()
        p = ProjectService.get_paginated(db, page=1, per_page=2)
        assert len(p.items) == 2
        assert p.total >= 5
        db.close()

    def test_update(self, app):
        db = self._db(app)
        p = ProjectService.create(db, name='Original')
        ProjectService.update(db, p.id, name='Updated', description='New desc')
        assert p.name == 'Updated'
        assert p.description == 'New desc'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = ProjectService.update(db, 99999, name='Ghost')
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        p = ProjectService.create(db, name='To Delete')
        pid = p.id
        assert ProjectService.delete(db, pid) is True
        assert ProjectService.get_by_id(db, pid) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert ProjectService.delete(db, 99999) is False
        db.close()


class TestDashboardService:
    def _db(self, app):
        return SessionLocal()

    def test_get_summary_empty(self, app):
        db = self._db(app)
        summary = DashboardService.get_summary(db)
        assert summary['online_devices'] == 0
        assert summary['offline_devices'] == 0
        assert summary['total_projects'] == 0
        assert summary['active_sessions'] == 0
        assert summary['today_energy'] == 0
        assert summary['current_power'] == 0
        db.close()

    def test_get_summary_with_data(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-dash')
        d.last_seen = datetime.now(timezone.utc)
        s = SessionService.create(db, d.id, 'Dash Sess')
        SessionService.start(db, s.id)
        MeasurementService.create(db, 'esp32-dash', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        summary = DashboardService.get_summary(db)
        assert summary['online_devices'] >= 1
        assert summary['active_sessions'] >= 1
        assert summary['current_power'] > 0
        db.close()

    def test_get_statistics_empty(self, app):
        db = self._db(app)
        stats = DashboardService.get_statistics(db)
        assert stats['energy']['hourly'] == []
        assert stats['energy']['daily'] == []
        db.close()

    def test_get_statistics_with_data(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-dash-stats', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService.get_statistics(db)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_with_device_filter(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-filter-dev')
        MeasurementService.create(db, 'esp32-filter-dev', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService.get_statistics(db, device_id=d.id)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_with_session_filter(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-filter-sess')
        s = SessionService.create(db, d.id, 'Filter Sess')
        SessionService.start(db, s.id)
        MeasurementService.create(db, 'esp32-filter-sess', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService.get_statistics(db, session_id=s.id)
        assert stats['voltage']['avg'] > 0
        assert stats['session_started_at'] is not None
        db.close()

    def test_get_statistics_with_date_filter(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-filter-date', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        from datetime import datetime, timezone, timedelta
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc) + timedelta(hours=1)
        stats = DashboardService.get_statistics(db, start_date=start, end_date=end)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_outside_date_range(self, app):
        db = self._db(app)
        MeasurementService.create(db, 'esp32-filter-date2', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        from datetime import datetime, timezone, timedelta
        start = datetime.now(timezone.utc) + timedelta(hours=10)
        end = datetime.now(timezone.utc) + timedelta(hours=11)
        stats = DashboardService.get_statistics(db, start_date=start, end_date=end)
        assert stats['voltage']['avg'] == 0
        db.close()

    def test_get_energy_breakdown_with_device_filter(self, app):
        db = self._db(app)
        d = DeviceService.create(db, 'esp32-energy-filter')
        MeasurementService.create(db, 'esp32-energy-filter', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        energy = DashboardService._get_energy_breakdown(db, device_id=d.id)
        assert 'hourly' in energy
        db.close()

    def test_get_energy_breakdown_empty(self, app):
        db = self._db(app)
        energy = DashboardService._get_energy_breakdown(db)
        assert energy == {'hourly': [], 'daily': [], 'weekly': [], 'monthly': []}
        db.close()
