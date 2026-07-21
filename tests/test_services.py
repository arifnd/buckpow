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
        u = UserService(db).create(name='Test', email='test@example.com', password='secret')
        assert u.id is not None
        assert u.name == 'Test'
        assert u.email == 'test@example.com'
        assert u.check_password('secret')
        db.close()

    def test_create_duplicate_email(self, app):
        import pytest
        db = self._db(app)
        UserService(db).create(name='A', email='dup@example.com', password='x')
        with pytest.raises(ValueError, match='already exists'):
            UserService(db).create(name='B', email='dup@example.com', password='y')
        db.close()

    def test_authenticate_success(self, app):
        db = self._db(app)
        UserService(db).create(name='Auth', email='auth@example.com', password='pass')
        u = UserService(db).authenticate('auth@example.com', 'pass')
        assert u is not None
        assert u.name == 'Auth'
        db.close()

    def test_authenticate_wrong_password(self, app):
        db = self._db(app)
        UserService(db).create(name='Auth', email='auth2@example.com', password='pass')
        u = UserService(db).authenticate('auth2@example.com', 'wrong')
        assert u is None
        db.close()

    def test_authenticate_nonexistent(self, app):
        db = self._db(app)
        u = UserService(db).authenticate('nobody@example.com', 'pass')
        assert u is None
        db.close()

    def test_update_user(self, app):
        db = self._db(app)
        u = UserService(db).create(name='Old', email='old@example.com', password='x')
        updated = UserService(db).update(u.id, name='New', email='new@example.com')
        assert updated.name == 'New'
        assert updated.email == 'new@example.com'
        db.close()

    def test_update_email_already_in_use(self, app):
        import pytest
        db = self._db(app)
        UserService(db).create(name='A', email='a@example.com', password='x')
        b = UserService(db).create(name='B', email='b@example.com', password='x')
        with pytest.raises(ValueError, match='already in use'):
            UserService(db).update(b.id, email='a@example.com')
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = UserService(db).update(99999, name='Ghost')
        assert result is None
        db.close()

    def test_update_password(self, app):
        db = self._db(app)
        u = UserService(db).create(name='Pwd', email='pwd@example.com', password='old')
        UserService(db).update(u.id, password='new')
        assert u.check_password('new')
        db.close()

    def test_get_by_id(self, app):
        db = self._db(app)
        u = UserService(db).create(name='ByID', email='byid@example.com', password='x')
        found = UserService(db).get_by_id(u.id)
        assert found is not None
        assert found.email == 'byid@example.com'
        db.close()

    def test_get_by_email(self, app):
        db = self._db(app)
        UserService(db).create(name='ByEmail', email='byemail@example.com', password='x')
        found = UserService(db).get_by_email('byemail@example.com')
        assert found is not None
        db.close()


class TestDeviceService:
    def _db(self, app):
        return SessionLocal()

    def test_create_device(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-svc-1', alias='Svc Device')
        assert d.id is not None
        assert d.device_id == 'esp32-svc-1'
        assert d.alias == 'Svc Device'
        assert d.enabled is True
        assert d.api_key is not None
        db.close()

    def test_get_by_device_id(self, app):
        db = self._db(app)
        DeviceService(db).create('esp32-find')
        d = DeviceService(db).get_by_device_id('esp32-find')
        assert d is not None
        db.close()

    def test_get_by_device_id_not_found(self, app):
        db = self._db(app)
        d = DeviceService(db).get_by_device_id('nonexistent')
        assert d is None
        db.close()

    def test_get_by_api_key(self, app):
        db = self._db(app)
        device = DeviceService(db).create('esp32-key')
        found = DeviceService(db).get_by_api_key(device.api_key)
        assert found is not None
        assert found.id == device.id
        db.close()

    def test_get_by_api_key_invalid(self, app):
        db = self._db(app)
        found = DeviceService(db).get_by_api_key('invalid-key')
        assert found is None
        db.close()

    def test_get_or_create_existing(self, app):
        db = self._db(app)
        DeviceService(db).create('esp32-goc')
        d = DeviceService(db).get_or_create('esp32-goc')
        assert d.device_id == 'esp32-goc'
        db.close()

    def test_get_or_create_new(self, app):
        db = self._db(app)
        d = DeviceService(db).get_or_create('esp32-new')
        assert d.device_id == 'esp32-new'
        db.close()

    def test_touch(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-touch')
        assert d.last_seen is None
        DeviceService(db).touch('esp32-touch')
        assert d.last_seen is not None
        db.close()

    def test_touch_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService(db).touch('nonexistent')
        assert result is None
        db.close()

    def test_regenerate_api_key(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-reg')
        old_key = d.api_key
        DeviceService(db).regenerate_api_key(d.id)
        assert d.api_key != old_key
        db.close()

    def test_regenerate_api_key_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService(db).regenerate_api_key(99999)
        assert result is None
        db.close()

    def test_toggle_enabled(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-toggle')
        assert d.enabled is True
        DeviceService(db).toggle_enabled(d.id)
        assert d.enabled is False
        DeviceService(db).toggle_enabled(d.id)
        assert d.enabled is True
        db.close()

    def test_toggle_enabled_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService(db).toggle_enabled(99999)
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-del')
        did = d.id
        assert DeviceService(db).delete(did) is True
        assert DeviceService(db).get_by_id(did) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert DeviceService(db).delete(99999) is False
        db.close()

    def test_get_online_status_offline_no_last_seen(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stat')
        assert DeviceService.get_online_status(d) == 'offline'
        db.close()

    def test_get_online_status_online(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stat-on')
        d.last_seen = datetime.now(timezone.utc)
        assert DeviceService.get_online_status(d) == 'online'
        db.close()

    def test_get_online_status_expired(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stat-off')
        d.last_seen = datetime.now(timezone.utc) - timedelta(seconds=180)
        assert DeviceService.get_online_status(d) == 'offline'
        db.close()

    def test_get_online_status_naive_datetime(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stat-naive')
        d.last_seen = datetime.now()
        d.last_seen = d.last_seen.replace(tzinfo=None)
        db.commit()
        status = DeviceService.get_online_status(d)
        assert status in ('online', 'offline')
        db.close()

    def test_masked_api_key_short(self, app):
        from app.models import Device
        d = Device(device_id='esp32-short', api_key='abcd1234')
        assert d._masked_api_key() == 'abcd****'

    def test_update(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-upd')
        DeviceService(db).update(d.id, alias='Updated', description='Desc')
        assert d.alias == 'Updated'
        assert d.description == 'Desc'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = DeviceService(db).update(99999, alias='Ghost')
        assert result is None
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        DeviceService(db).create('esp32-all-a')
        DeviceService(db).create('esp32-all-b')
        assert len(DeviceService(db).get_all()) >= 2
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
        p = DeviceService(db).get_paginated(page=1, per_page=2)
        assert len(p.items) == 2
        assert p.total >= 5
        db.close()


class TestSessionService:
    def _db(self, app):
        return SessionLocal()

    def test_create_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-sess-svc')
        s = SessionService(db).create(device_id=d.id, name='Test Session')
        assert s.id is not None
        assert s.status == 'draft'
        db.close()

    def test_create_with_all_fields(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-sess-full')
        s = SessionService(db).create(device_id=d.id, name='Full', target_device='t1',
                                  description='desc')
        assert s.target_device == 't1'
        assert s.description == 'desc'
        db.close()

    def test_start_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-start')
        s = SessionService(db).create(d.id, 'Start')
        session, error = SessionService(db).start(s.id)
        assert error is None
        assert session.status == 'running'
        db.close()

    def test_start_nonexistent(self, app):
        db = self._db(app)
        session, error = SessionService(db).start(99999)
        assert session is None
        assert error == 'Session not found'
        db.close()

    def test_start_already_running(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-already')
        s = SessionService(db).create(d.id, 'Running')
        SessionService(db).start(s.id)
        session, error = SessionService(db).start(s.id)
        assert session is None
        assert error == 'Session is already running'
        db.close()

    def test_stop_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stop')
        s = SessionService(db).create(d.id, 'Stop')
        SessionService(db).start(s.id)
        session, error = SessionService(db).stop(s.id)
        assert error is None
        assert session.status == 'finished'
        db.close()

    def test_stop_nonexistent(self, app):
        db = self._db(app)
        session, error = SessionService(db).stop(99999)
        assert session is None
        assert error == 'Session not found'
        db.close()

    def test_stop_not_running(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stop2')
        s = SessionService(db).create(d.id, 'Draft')
        session, error = SessionService(db).stop(s.id)
        assert session is None
        assert error == 'Session is not running'
        db.close()

    def test_get_active_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-act')
        s = SessionService(db).create(d.id, 'Active')
        SessionService(db).start(s.id)
        active = SessionService(db).get_active_session(d.id)
        assert active is not None
        assert active.id == s.id
        db.close()

    def test_auto_stop_other_on_start(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-auto')
        a = SessionService(db).create(d.id, 'Session A')
        b = SessionService(db).create(d.id, 'Session B')
        SessionService(db).start(a.id)
        assert a.status == 'running'
        result, err = SessionService(db).start(b.id)
        assert result is None
        assert err == 'A session is already running for this device'
        assert a.status == 'running'
        db.close()

    def test_multiple_devices_can_run_concurrently(self, app):
        db = self._db(app)
        d1 = DeviceService(db).create('esp32-d1')
        d2 = DeviceService(db).create('esp32-d2')
        a = SessionService(db).create(d1.id, 'Session A')
        b = SessionService(db).create(d2.id, 'Session B')
        SessionService(db).start(a.id)
        assert a.status == 'running'
        SessionService(db).start(b.id)
        assert b.status == 'running'
        assert a.status == 'running'
        db.close()

    def test_get_for_device(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-gfd')
        SessionService(db).create(d.id, 'S1')
        SessionService(db).create(d.id, 'S2')
        sessions = SessionService(db).get_for_device(d.id)
        assert len(sessions) == 2
        db.close()

    def test_update(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-up')
        s = SessionService(db).create(d.id, 'Original')
        SessionService(db).update(s.id, name='Updated')
        assert s.name == 'Updated'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = SessionService(db).update(99999, name='Ghost')
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-del-s')
        s = SessionService(db).create(d.id, 'To Delete')
        sid = s.id
        assert SessionService(db).delete(sid) is True
        assert SessionService(db).get_by_id(sid) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert SessionService(db).delete(99999) is False
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-all-s')
        SessionService(db).create(d.id, 'A')
        SessionService(db).create(d.id, 'B')
        assert len(SessionService(db).get_all()) >= 2
        db.close()

    def test_get_stats_for_sessions_with_measurements(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-sts')
        s = SessionService(db).create(d.id, 'Stats Session')
        SessionService(db).start(s.id)
        MeasurementService(db).create('esp32-sts', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        MeasurementService(db).create('esp32-sts', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = SessionService.get_stats_for_sessions(db, [s.id])
        assert s.id in stats
        assert stats[s.id]['avg_power'] is not None
        db.close()

    def test_get_stats_for_sessions_empty_ids(self, app):
        db = self._db(app)
        stats = SessionService.get_stats_for_sessions(db, [])
        assert stats == {}


class TestMeasurementService:
    def _db(self, app):
        return SessionLocal()

    def test_create_measurement(self, app):
        db = self._db(app)
        m = MeasurementService(db).create('esp32-meas-svc', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.id is not None
        assert m.load_voltage == 5.08
        assert m.current == 0.2
        assert m.power == 1.0
        db.close()

    def test_create_auto_registers_device(self, app):
        db = self._db(app)
        m = MeasurementService(db).create('esp32-auto-reg', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        device = DeviceService(db).get_by_device_id('esp32-auto-reg')
        assert device is not None
        assert m.device_id == device.id
        db.close()

    def test_create_with_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-sess-m')
        s = SessionService(db).create(d.id, 'Meas Session')
        SessionService(db).start(s.id)
        m = MeasurementService(db).create('esp32-sess-m', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.session_id == s.id
        db.close()

    def test_energy_accumulation_same_session(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-energy')
        s = SessionService(db).create(d.id, 'Energy')
        SessionService(db).start(s.id)
        m1 = MeasurementService(db).create('esp32-energy', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        m2 = MeasurementService(db).create('esp32-energy', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        assert m2.energy > m1.energy
        db.close()

    def test_energy_no_session_starts_at_zero(self, app):
        db = self._db(app)
        m = MeasurementService(db).create('esp32-no-sess', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        assert m.energy == 0.0
        db.close()

    def test_get_recent(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-recent', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        recent = MeasurementService(db).get_recent(limit=10)
        assert len(recent) >= 1
        db.close()

    def test_get_stats_empty(self, app):
        db = self._db(app)
        stats = MeasurementService(db).get_stats()
        assert stats['energy']['total'] == 0
        db.close()

    def test_get_stats_with_data(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-stats', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = MeasurementService(db).get_stats()
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_chart_data_no_granularity(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-chart-svc', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10)
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_with_granularity_hour(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-gran', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, granularity='h')
        assert len(data['labels']) >= 1
        db.close()

    def test_get_session_stats_empty(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-ss-empty')
        s = SessionService(db).create(d.id, 'Empty Session')
        stats = MeasurementService.get_session_stats(db, s.id)
        assert stats is not None
        assert stats['measurement_count'] == 0
        db.close()

    def test_get_session_stats_with_data(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-ss-data')
        s = SessionService(db).create(d.id, 'Data Session')
        SessionService(db).start(s.id)
        MeasurementService(db).create('esp32-ss-data', bus_voltage=5.0,
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
            MeasurementService(db).create(f'esp32-pag-{i}', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
        p = MeasurementService(db).get_paginated(page=1, per_page=2)
        assert len(p.items) == 2
        db.close()

    def test_get_all_filtered(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        rows = MeasurementService(db).get_all_filtered()
        assert len(rows) >= 1
        db.close()

    def test_get_recent_with_device_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-rec-filt')
        MeasurementService(db).create('esp32-rec-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        recent = MeasurementService(db).get_recent(limit=10, device_id=d.id)
        assert len(recent) >= 1
        db.close()

    def test_get_chart_data_granularity_second(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-g-s', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, granularity='s')
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_granularity_minute(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-g-m', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, granularity='m')
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_granularity_day(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-g-d', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, granularity='d')
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_device_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-cd-filt')
        MeasurementService(db).create('esp32-cd-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, device_id=d.id)
        assert len(data['labels']) >= 1
        db.close()

    def test_get_chart_data_session_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-cs-filt')
        s = SessionService(db).create(d.id, 'Chart Session')
        SessionService(db).start(s.id)
        MeasurementService(db).create('esp32-cs-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        data = MeasurementService(db).get_chart_data(limit=10, session_id=s.id)
        assert len(data['labels']) >= 1
        db.close()

    def test_get_stats_device_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-stats-filt')
        MeasurementService(db).create('esp32-stats-filt', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = MeasurementService(db).get_stats(device_id=d.id)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_energy_no_session_existing_device(self, app):
        db = self._db(app)
        DeviceService(db).create('esp32-ens-exist')
        m1 = MeasurementService(db).create('esp32-ens-exist', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        m2 = MeasurementService(db).create('esp32-ens-exist', bus_voltage=5.0,
                                       shunt_voltage=80.0, current=200, power=1000)
        assert m2.energy > m1.energy
        db.close()

    def test_pzem_create_no_shunt(self, app):
        db = self._db(app)
        m = MeasurementService(db).create('pzem-svc', bus_voltage=230.5,
                                      shunt_voltage=0.0, current=4500, power=1035000)
        assert m.bus_voltage == 230.5
        assert m.shunt_voltage == 0.0
        assert m.load_voltage == 230.5
        assert m.current == 4.5
        assert m.power == 1035.0
        db.close()

    def test_pzem_create_default_shunt(self, app):
        db = self._db(app)
        m = MeasurementService(db).create('pzem-default', bus_voltage=220.0,
                                      current=10000, power=2200000)
        assert m.shunt_voltage == 0.0
        assert m.load_voltage == 220.0
        db.close()

    def test_pzem_energy_accumulation(self, app):
        db = self._db(app)
        DeviceService(db).create('pzem-energy')
        m1 = MeasurementService(db).create('pzem-energy', bus_voltage=230.0,
                                       current=5000, power=1150000)
        m2 = MeasurementService(db).create('pzem-energy', bus_voltage=230.0,
                                       current=5000, power=1150000)
        assert m2.energy > m1.energy
        db.close()

    def test_pzem_chart_data(self, app):
        db = self._db(app)
        MeasurementService(db).create('pzem-chart', bus_voltage=230.0,
                                  current=5000, power=1150000)
        data = MeasurementService(db).get_chart_data(limit=10)
        assert len(data['labels']) >= 1
        assert data['voltage'][0] == 230.0
        db.close()

    def test_pzem_stats(self, app):
        db = self._db(app)
        MeasurementService(db).create('pzem-stats', bus_voltage=230.0,
                                  current=5000, power=1150000)
        stats = MeasurementService(db).get_stats()
        assert stats['voltage']['avg'] == 230.0
        db.close()


class TestAlertService:
    def _db(self, app):
        return SessionLocal()

    def test_create_alert(self, app, sample_device_id):
        db = self._db(app)
        a = AlertService(db).create(device_id=sample_device_id, level='critical',
                                message='Test alert')
        assert a.id is not None
        assert a.level == 'critical'
        db.close()

    def test_get_paginated(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='A1')
        AlertService(db).create(device_id=sample_device_id, level='info', message='A2')
        p = AlertService(db).get_paginated(page=1, per_page=10)
        assert len(p.items) >= 2
        db.close()

    def test_get_paginated_filter_device(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='F1')
        p = AlertService(db).get_paginated(page=1, per_page=10, device_id=sample_device_id)
        assert len(p.items) == 1
        db.close()

    def test_get_paginated_filter_level(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='W')
        AlertService(db).create(device_id=sample_device_id, level='info', message='I')
        p = AlertService(db).get_paginated(page=1, per_page=10, level='info')
        assert len(p.items) == 1
        db.close()

    def test_get_paginated_filter_unresolved(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='Unres')
        p = AlertService(db).get_paginated(page=1, per_page=10, resolved=False)
        assert len(p.items) >= 1
        db.close()

    def test_resolve(self, app, sample_device_id):
        db = self._db(app)
        a = AlertService(db).create(device_id=sample_device_id, level='warning', message='Resolve me')
        assert a.resolved_at is None
        resolved = AlertService(db).resolve(a.id)
        assert resolved.resolved_at is not None
        db.close()

    def test_resolve_nonexistent(self, app):
        db = self._db(app)
        result = AlertService(db).resolve(99999)
        assert result is None
        db.close()

    def test_resolve_all(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='A')
        AlertService(db).create(device_id=sample_device_id, level='info', message='B')
        AlertService(db).resolve_all()
        count = AlertService(db).get_unresolved_count()
        assert count == 0
        db.close()

    def test_get_unresolved_count(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='Urgent')
        assert AlertService(db).get_unresolved_count() >= 1
        db.close()

    def test_generate_alerts_high_power(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-alert-hp', high_power_threshold=1.0)
        AlertService(db).generate_alerts( d, bus_voltage=5.0, current=0.1, power=2.0)
        unresolved = AlertService(db).get_unresolved_count(device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_high_current(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-alert-hc', high_current_threshold=0.3)
        AlertService(db).generate_alerts( d, bus_voltage=5.0, current=0.5, power=0.5)
        unresolved = AlertService(db).get_unresolved_count(device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_low_voltage(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-alert-lv', low_voltage_threshold=4.0)
        AlertService(db).generate_alerts( d, bus_voltage=3.5, current=0.1, power=0.5)
        unresolved = AlertService(db).get_unresolved_count(device_id=d.id)
        assert unresolved >= 1
        db.close()

    def test_generate_alerts_no_duplicates(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-alert-nd', high_power_threshold=1.0)
        AlertService(db).generate_alerts( d, bus_voltage=5.0, current=0.1, power=2.0)
        AlertService(db).generate_alerts( d, bus_voltage=5.0, current=0.1, power=2.0)
        unresolved = AlertService(db).get_unresolved_count(device_id=d.id)
        alerts = db.query(Alert).filter_by(device_id=d.id, resolved_at=None).all()
        high_power_count = sum(1 for a in alerts if 'High power' in a.message)
        assert high_power_count == 1
        db.close()

    def test_resolve_all_with_device_filter(self, app, sample_device_id):
        db = self._db(app)
        AlertService(db).create(device_id=sample_device_id, level='warning', message='Filtered')
        AlertService(db).resolve_all(device_id=sample_device_id)
        count = AlertService(db).get_unresolved_count(device_id=sample_device_id)
        assert count == 0
        db.close()

    def test_get_paginated_resolved_true(self, app, sample_device_id):
        db = self._db(app)
        a = AlertService(db).create(device_id=sample_device_id, level='info', message='Resolved alert')
        AlertService(db).resolve(a.id)
        p = AlertService(db).get_paginated(page=1, per_page=10, resolved=True)
        assert len(p.items) >= 1
        db.close()

    def test_owner_settings_with_exception(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-own-err')
        d.project_id = 99999
        db.commit()
        result = AlertService._owner_settings(db, d)
        assert result == {}
        db.close()


class TestProjectService:
    def _db(self, app):
        return SessionLocal()

    def test_create_project(self, app):
        db = self._db(app)
        p = ProjectService(db).create(name='Test Project', description='Desc')
        assert p.id is not None
        assert p.name == 'Test Project'
        db.close()

    def test_create_with_owner(self, app):
        db = self._db(app)
        user = db.query(User).first()
        p = ProjectService(db).create(name='Owned', owner_id=user.id)
        assert p.owner_id == user.id
        db.close()

    def test_get_by_id(self, app):
        db = self._db(app)
        p = ProjectService(db).create(name='Find Me')
        found = ProjectService(db).get_by_id(p.id)
        assert found is not None
        db.close()

    def test_get_by_id_nonexistent(self, app):
        db = self._db(app)
        p = ProjectService(db).get_by_id(99999)
        assert p is None
        db.close()

    def test_get_all(self, app):
        db = self._db(app)
        ProjectService(db).create(name='A')
        ProjectService(db).create(name='B')
        assert len(ProjectService(db).get_all()) >= 2
        db.close()

    def test_get_paginated(self, app):
        from sqlalchemy import insert
        from app.models import Project
        db = self._db(app)
        db.execute(insert(Project), [{'name': f'Project {i}'} for i in range(5)])
        db.commit()
        p = ProjectService(db).get_paginated(page=1, per_page=2)
        assert len(p.items) == 2
        assert p.total >= 5
        db.close()

    def test_update(self, app):
        db = self._db(app)
        p = ProjectService(db).create(name='Original')
        ProjectService(db).update(p.id, name='Updated', description='New desc')
        assert p.name == 'Updated'
        assert p.description == 'New desc'
        db.close()

    def test_update_nonexistent(self, app):
        db = self._db(app)
        result = ProjectService(db).update(99999, name='Ghost')
        assert result is None
        db.close()

    def test_delete(self, app):
        db = self._db(app)
        p = ProjectService(db).create(name='To Delete')
        pid = p.id
        assert ProjectService(db).delete(pid) is True
        assert ProjectService(db).get_by_id(pid) is None
        db.close()

    def test_delete_nonexistent(self, app):
        db = self._db(app)
        assert ProjectService(db).delete(99999) is False
        db.close()


class TestDashboardService:
    def _db(self, app):
        return SessionLocal()

    def test_get_summary_empty(self, app):
        db = self._db(app)
        summary = DashboardService(db).get_summary()
        assert summary['online_devices'] == 0
        assert summary['offline_devices'] == 0
        assert summary['total_projects'] == 0
        assert summary['active_sessions'] == 0
        assert summary['today_energy'] == 0
        assert summary['current_power'] == 0
        db.close()

    def test_get_summary_with_data(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-dash')
        d.last_seen = datetime.now(timezone.utc)
        s = SessionService(db).create(d.id, 'Dash Sess')
        SessionService(db).start(s.id)
        MeasurementService(db).create('esp32-dash', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        summary = DashboardService(db).get_summary()
        assert summary['online_devices'] >= 1
        assert summary['active_sessions'] >= 1
        assert summary['current_power'] > 0
        db.close()

    def test_get_statistics_empty(self, app):
        db = self._db(app)
        stats = DashboardService(db).get_statistics()
        assert stats['energy']['hourly'] == []
        assert stats['energy']['daily'] == []
        db.close()

    def test_get_statistics_with_data(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-dash-stats', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService(db).get_statistics()
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_with_device_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-filter-dev')
        MeasurementService(db).create('esp32-filter-dev', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService(db).get_statistics(device_id=d.id)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_with_session_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-filter-sess')
        s = SessionService(db).create(d.id, 'Filter Sess')
        SessionService(db).start(s.id)
        MeasurementService(db).create('esp32-filter-sess', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        stats = DashboardService(db).get_statistics(session_id=s.id)
        assert stats['voltage']['avg'] > 0
        assert stats['session_started_at'] is not None
        db.close()

    def test_get_statistics_with_date_filter(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-filter-date', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        from datetime import datetime, timezone, timedelta
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc) + timedelta(hours=1)
        stats = DashboardService(db).get_statistics(start_date=start, end_date=end)
        assert stats['voltage']['avg'] > 0
        db.close()

    def test_get_statistics_outside_date_range(self, app):
        db = self._db(app)
        MeasurementService(db).create('esp32-filter-date2', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        from datetime import datetime, timezone, timedelta
        start = datetime.now(timezone.utc) + timedelta(hours=10)
        end = datetime.now(timezone.utc) + timedelta(hours=11)
        stats = DashboardService(db).get_statistics(start_date=start, end_date=end)
        assert stats['voltage']['avg'] == 0
        db.close()

    def test_get_energy_breakdown_with_device_filter(self, app):
        db = self._db(app)
        d = DeviceService(db).create('esp32-energy-filter')
        MeasurementService(db).create('esp32-energy-filter', bus_voltage=5.0,
                                  shunt_voltage=80.0, current=200, power=1000)
        energy = DashboardService(db)._get_energy_breakdown(device_id=d.id)
        assert 'hourly' in energy
        db.close()

    def test_get_energy_breakdown_empty(self, app):
        db = self._db(app)
        energy = DashboardService(db)._get_energy_breakdown()
        assert energy == {'hourly': [], 'daily': [], 'weekly': [], 'monthly': []}
        db.close()

    def test_get_energy_breakdown_session_boundary(self, app):
        db = self._db(app)
        d1 = DeviceService(db).create('esp32-boundary1')
        d2 = DeviceService(db).create('esp32-boundary2')
        sess1 = SessionService(db).create(d1.id, 'Boundary S1')
        sess2 = SessionService(db).create(d2.id, 'Boundary S2')
        from app.models import Measurement as M
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        m1 = M(device_id=d1.id, session_id=sess1.id, bus_voltage=5.0,
                shunt_voltage=0.0, load_voltage=5.0, current=0.1, power=0.5, energy=1.0,
                created_at=now - timedelta(minutes=5))
        m2 = M(device_id=d2.id, session_id=sess2.id, bus_voltage=5.0,
                shunt_voltage=0.0, load_voltage=5.0, current=0.1, power=0.5, energy=2.0,
                created_at=now)
        db.add_all([m1, m2])
        db.commit()
        energy = DashboardService(db)._get_energy_breakdown()
        assert isinstance(energy['hourly'], list)
        assert isinstance(energy['daily'], list)
        db.close()
