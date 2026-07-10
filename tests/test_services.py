from datetime import datetime, timezone, timedelta

from app import db
from app.models import Device, Session, Measurement, User, Project, Alert
from app.services.user_service import UserService
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.services.measurement_service import MeasurementService
from app.services.alert_service import AlertService
from app.services.project_service import ProjectService
from app.services.dashboard_service import DashboardService


class TestUserService:
    def test_create_user(self, app):
        with app.app_context():
            u = UserService.create(name='Test', email='test@example.com', password='secret')
            assert u.id is not None
            assert u.name == 'Test'
            assert u.email == 'test@example.com'
            assert u.check_password('secret')

    def test_create_duplicate_email(self, app):
        with app.app_context():
            UserService.create(name='A', email='dup@example.com', password='x')
            import pytest
            with pytest.raises(ValueError, match='already exists'):
                UserService.create(name='B', email='dup@example.com', password='y')

    def test_authenticate_success(self, app):
        with app.app_context():
            UserService.create(name='Auth', email='auth@example.com', password='pass')
            u = UserService.authenticate('auth@example.com', 'pass')
            assert u is not None
            assert u.name == 'Auth'

    def test_authenticate_wrong_password(self, app):
        with app.app_context():
            UserService.create(name='Auth', email='auth2@example.com', password='pass')
            u = UserService.authenticate('auth2@example.com', 'wrong')
            assert u is None

    def test_authenticate_nonexistent(self, app):
        with app.app_context():
            u = UserService.authenticate('nobody@example.com', 'pass')
            assert u is None

    def test_update_user(self, app):
        with app.app_context():
            u = UserService.create(name='Old', email='old@example.com', password='x')
            updated = UserService.update(u.id, name='New', email='new@example.com')
            assert updated.name == 'New'
            assert updated.email == 'new@example.com'

    def test_update_email_already_in_use(self, app):
        with app.app_context():
            UserService.create(name='A', email='a@example.com', password='x')
            b = UserService.create(name='B', email='b@example.com', password='x')
            import pytest
            with pytest.raises(ValueError, match='already in use'):
                UserService.update(b.id, email='a@example.com')

    def test_update_nonexistent(self, app):
        with app.app_context():
            result = UserService.update(99999, name='Ghost')
            assert result is None

    def test_update_password(self, app):
        with app.app_context():
            u = UserService.create(name='Pwd', email='pwd@example.com', password='old')
            UserService.update(u.id, password='new')
            assert u.check_password('new')

    def test_get_by_id(self, app):
        with app.app_context():
            u = UserService.create(name='ByID', email='byid@example.com', password='x')
            found = UserService.get_by_id(u.id)
            assert found is not None
            assert found.email == 'byid@example.com'

    def test_get_by_email(self, app):
        with app.app_context():
            UserService.create(name='ByEmail', email='byemail@example.com', password='x')
            found = UserService.get_by_email('byemail@example.com')
            assert found is not None


class TestDeviceService:
    def test_create_device(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-svc-1', alias='Svc Device')
            assert d.id is not None
            assert d.device_id == 'esp32-svc-1'
            assert d.alias == 'Svc Device'
            assert d.enabled is True
            assert d.api_key is not None

    def test_get_by_device_id(self, app):
        with app.app_context():
            DeviceService.create('esp32-find')
            d = DeviceService.get_by_device_id('esp32-find')
            assert d is not None

    def test_get_by_device_id_not_found(self, app):
        with app.app_context():
            d = DeviceService.get_by_device_id('nonexistent')
            assert d is None

    def test_get_by_api_key(self, app):
        with app.app_context():
            device = DeviceService.create('esp32-key')
            found = DeviceService.get_by_api_key(device.api_key)
            assert found is not None
            assert found.id == device.id

    def test_get_by_api_key_invalid(self, app):
        with app.app_context():
            found = DeviceService.get_by_api_key('invalid-key')
            assert found is None

    def test_get_or_create_existing(self, app):
        with app.app_context():
            DeviceService.create('esp32-goc')
            d = DeviceService.get_or_create('esp32-goc')
            assert d.device_id == 'esp32-goc'

    def test_get_or_create_new(self, app):
        with app.app_context():
            d = DeviceService.get_or_create('esp32-new')
            assert d.device_id == 'esp32-new'

    def test_touch(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-touch')
            assert d.last_seen is None
            DeviceService.touch('esp32-touch')
            assert d.last_seen is not None

    def test_touch_nonexistent(self, app):
        with app.app_context():
            result = DeviceService.touch('nonexistent')
            assert result is None

    def test_regenerate_api_key(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-reg')
            old_key = d.api_key
            DeviceService.regenerate_api_key(d.id)
            assert d.api_key != old_key

    def test_regenerate_api_key_nonexistent(self, app):
        with app.app_context():
            result = DeviceService.regenerate_api_key(99999)
            assert result is None

    def test_toggle_enabled(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-toggle')
            assert d.enabled is True
            DeviceService.toggle_enabled(d.id)
            assert d.enabled is False
            DeviceService.toggle_enabled(d.id)
            assert d.enabled is True

    def test_toggle_enabled_nonexistent(self, app):
        with app.app_context():
            result = DeviceService.toggle_enabled(99999)
            assert result is None

    def test_delete(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-del')
            did = d.id
            assert DeviceService.delete(did) is True
            assert DeviceService.get_by_id(did) is None

    def test_delete_nonexistent(self, app):
        with app.app_context():
            assert DeviceService.delete(99999) is False

    def test_get_online_status_offline_no_last_seen(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-stat')
            assert DeviceService.get_online_status(d) == 'offline'

    def test_get_online_status_online(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-stat-on')
            d.last_seen = datetime.now(timezone.utc)
            assert DeviceService.get_online_status(d) == 'online'

    def test_get_online_status_expired(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-stat-off')
            d.last_seen = datetime.now(timezone.utc) - timedelta(seconds=180)
            assert DeviceService.get_online_status(d) == 'offline'

    def test_update(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-upd')
            DeviceService.update(d.id, alias='Updated', description='Desc')
            assert d.alias == 'Updated'
            assert d.description == 'Desc'

    def test_update_nonexistent(self, app):
        with app.app_context():
            result = DeviceService.update(99999, alias='Ghost')
            assert result is None

    def test_get_all(self, app):
        with app.app_context():
            DeviceService.create('esp32-all-a')
            DeviceService.create('esp32-all-b')
            assert len(DeviceService.get_all()) >= 2

    def test_get_paginated(self, app):
        with app.app_context():
            for i in range(5):
                DeviceService.create(f'esp32-page-{i}')
            p = DeviceService.get_paginated(page=1, per_page=2)
            assert len(p.items) == 2
            assert p.total >= 5


class TestSessionService:
    def test_create_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-sess-svc')
            s = SessionService.create(device_id=d.id, name='Test Session')
            assert s.id is not None
            assert s.status == 'draft'

    def test_create_with_all_fields(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-sess-full')
            s = SessionService.create(device_id=d.id, name='Full', target_device='t1',
                                      description='desc')
            assert s.target_device == 't1'
            assert s.description == 'desc'

    def test_start_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-start')
            s = SessionService.create(d.id, 'Start')
            session, error = SessionService.start(s.id)
            assert error is None
            assert session.status == 'running'

    def test_start_nonexistent(self, app):
        with app.app_context():
            session, error = SessionService.start(99999)
            assert session is None
            assert error == 'Session not found'

    def test_start_already_running(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-already')
            s = SessionService.create(d.id, 'Running')
            SessionService.start(s.id)
            session, error = SessionService.start(s.id)
            assert session is None
            assert error == 'Session is already running'

    def test_stop_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-stop')
            s = SessionService.create(d.id, 'Stop')
            SessionService.start(s.id)
            session, error = SessionService.stop(s.id)
            assert error is None
            assert session.status == 'finished'

    def test_stop_nonexistent(self, app):
        with app.app_context():
            session, error = SessionService.stop(99999)
            assert session is None
            assert error == 'Session not found'

    def test_stop_not_running(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-stop2')
            s = SessionService.create(d.id, 'Draft')
            session, error = SessionService.stop(s.id)
            assert session is None
            assert error == 'Session is not running'

    def test_get_active_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-act')
            s = SessionService.create(d.id, 'Active')
            SessionService.start(s.id)
            active = SessionService.get_active_session(d.id)
            assert active is not None
            assert active.id == s.id

    def test_get_any_active_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-any')
            s = SessionService.create(d.id, 'Any')
            SessionService.start(s.id)
            active = SessionService.get_any_active_session()
            assert active is not None

    def test_auto_stop_other_on_start(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-auto')
            a = SessionService.create(d.id, 'Session A')
            b = SessionService.create(d.id, 'Session B')
            SessionService.start(a.id)
            assert a.status == 'running'
            result, err = SessionService.start(b.id)
            assert result is None
            assert err == 'A session is already running for this device'
            assert a.status == 'running'

    def test_global_auto_finish_different_device(self, app):
        with app.app_context():
            d1 = DeviceService.create('esp32-d1')
            d2 = DeviceService.create('esp32-d2')
            a = SessionService.create(d1.id, 'Session A')
            b = SessionService.create(d2.id, 'Session B')
            SessionService.start(a.id)
            assert a.status == 'running'
            SessionService.start(b.id)
            assert b.status == 'running'
            assert a.status == 'finished'

    def test_get_for_device(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-gfd')
            SessionService.create(d.id, 'S1')
            SessionService.create(d.id, 'S2')
            sessions = SessionService.get_for_device(d.id)
            assert len(sessions) == 2

    def test_update(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-up')
            s = SessionService.create(d.id, 'Original')
            SessionService.update(s.id, name='Updated')
            assert s.name == 'Updated'

    def test_update_nonexistent(self, app):
        with app.app_context():
            result = SessionService.update(99999, name='Ghost')
            assert result is None

    def test_delete(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-del-s')
            s = SessionService.create(d.id, 'To Delete')
            sid = s.id
            assert SessionService.delete(sid) is True
            assert SessionService.get_by_id(sid) is None

    def test_delete_nonexistent(self, app):
        with app.app_context():
            assert SessionService.delete(99999) is False

    def test_get_all(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-all-s')
            SessionService.create(d.id, 'A')
            SessionService.create(d.id, 'B')
            assert len(SessionService.get_all()) >= 2


class TestMeasurementService:
    def test_create_measurement(self, app):
        with app.app_context():
            m = MeasurementService.create('esp32-meas-svc', bus_voltage=5.0,
                                          shunt_voltage=80.0, current=200, power=1000)
            assert m.id is not None
            assert m.load_voltage == 5.08
            assert m.current == 0.2
            assert m.power == 1.0

    def test_create_auto_registers_device(self, app):
        with app.app_context():
            m = MeasurementService.create('esp32-auto-reg', bus_voltage=5.0,
                                          shunt_voltage=80.0, current=200, power=1000)
            device = DeviceService.get_by_device_id('esp32-auto-reg')
            assert device is not None
            assert m.device_id == device.id

    def test_create_with_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-sess-m')
            s = SessionService.create(d.id, 'Meas Session')
            SessionService.start(s.id)
            m = MeasurementService.create('esp32-sess-m', bus_voltage=5.0,
                                          shunt_voltage=80.0, current=200, power=1000)
            assert m.session_id == s.id

    def test_energy_accumulation_same_session(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-energy')
            s = SessionService.create(d.id, 'Energy')
            SessionService.start(s.id)
            m1 = MeasurementService.create('esp32-energy', bus_voltage=5.0,
                                           shunt_voltage=80.0, current=200, power=1000)
            m2 = MeasurementService.create('esp32-energy', bus_voltage=5.0,
                                           shunt_voltage=80.0, current=200, power=1000)
            assert m2.energy > m1.energy

    def test_energy_no_session_starts_at_zero(self, app):
        with app.app_context():
            m = MeasurementService.create('esp32-no-sess', bus_voltage=5.0,
                                          shunt_voltage=80.0, current=200, power=1000)
            assert m.energy == 0.0

    def test_get_recent(self, app):
        with app.app_context():
            MeasurementService.create('esp32-recent', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            recent = MeasurementService.get_recent(limit=10)
            assert len(recent) >= 1

    def test_get_stats_empty(self, app):
        with app.app_context():
            stats = MeasurementService.get_stats()
            assert stats['energy']['total'] == 0

    def test_get_stats_with_data(self, app):
        with app.app_context():
            MeasurementService.create('esp32-stats', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            stats = MeasurementService.get_stats()
            assert stats['voltage']['avg'] > 0

    def test_get_chart_data_no_granularity(self, app):
        with app.app_context():
            MeasurementService.create('esp32-chart-svc', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            data = MeasurementService.get_chart_data(limit=10)
            assert len(data['labels']) >= 1

    def test_get_chart_data_with_granularity_hour(self, app):
        with app.app_context():
            MeasurementService.create('esp32-gran', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            data = MeasurementService.get_chart_data(limit=10, granularity='h')
            assert len(data['labels']) >= 1

    def test_get_session_stats_empty(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-ss-empty')
            s = SessionService.create(d.id, 'Empty Session')
            stats = MeasurementService.get_session_stats(s.id)
            assert stats is not None
            assert stats['measurement_count'] == 0

    def test_get_session_stats_with_data(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-ss-data')
            s = SessionService.create(d.id, 'Data Session')
            SessionService.start(s.id)
            MeasurementService.create('esp32-ss-data', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            db.session.flush()
            stats = MeasurementService.get_session_stats(s.id)
            assert stats['measurement_count'] == 1
            assert stats['avg_power'] > 0

    def test_get_session_stats_nonexistent(self, app):
        with app.app_context():
            stats = MeasurementService.get_session_stats(99999)
            assert stats is None

    def test_get_paginated(self, app):
        with app.app_context():
            for i in range(3):
                MeasurementService.create(f'esp32-pag-{i}', bus_voltage=5.0,
                                          shunt_voltage=80.0, current=200, power=1000)
            p = MeasurementService.get_paginated(page=1, per_page=2)
            assert len(p.items) == 2

    def test_get_all_filtered(self, app):
        with app.app_context():
            MeasurementService.create('esp32-filt', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            rows = MeasurementService.get_all_filtered()
            assert len(rows) >= 1


class TestAlertService:
    def test_create_alert(self, app, sample_device_id):
        with app.app_context():
            a = AlertService.create(device_id=sample_device_id, level='critical',
                                    message='Test alert')
            assert a.id is not None
            assert a.level == 'critical'

    def test_get_paginated(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='A1')
            AlertService.create(device_id=sample_device_id, level='info', message='A2')
            p = AlertService.get_paginated(page=1, per_page=10)
            assert len(p.items) >= 2

    def test_get_paginated_filter_device(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='F1')
            p = AlertService.get_paginated(page=1, per_page=10, device_id=sample_device_id)
            assert len(p.items) == 1

    def test_get_paginated_filter_level(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='W')
            AlertService.create(device_id=sample_device_id, level='info', message='I')
            p = AlertService.get_paginated(page=1, per_page=10, level='info')
            assert len(p.items) == 1

    def test_get_paginated_filter_unresolved(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='Unres')
            p = AlertService.get_paginated(page=1, per_page=10, resolved=False)
            assert len(p.items) >= 1

    def test_resolve(self, app, sample_device_id):
        with app.app_context():
            a = AlertService.create(device_id=sample_device_id, level='warning', message='Resolve me')
            assert a.resolved_at is None
            resolved = AlertService.resolve(a.id)
            assert resolved.resolved_at is not None

    def test_resolve_nonexistent(self, app):
        with app.app_context():
            result = AlertService.resolve(99999)
            assert result is None

    def test_resolve_all(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='A')
            AlertService.create(device_id=sample_device_id, level='info', message='B')
            AlertService.resolve_all()
            count = AlertService.get_unresolved_count()
            assert count == 0

    def test_get_unresolved_count(self, app, sample_device_id):
        with app.app_context():
            AlertService.create(device_id=sample_device_id, level='warning', message='Urgent')
            assert AlertService.get_unresolved_count() >= 1

    def test_generate_alerts_high_power(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-alert-hp', high_power_threshold=1.0)
            AlertService.generate_alerts(d, bus_voltage=5.0, current=0.1, power=2.0)
            unresolved = AlertService.get_unresolved_count(device_id=d.id)
            assert unresolved >= 1

    def test_generate_alerts_high_current(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-alert-hc', high_current_threshold=0.3)
            AlertService.generate_alerts(d, bus_voltage=5.0, current=0.5, power=0.5)
            unresolved = AlertService.get_unresolved_count(device_id=d.id)
            assert unresolved >= 1

    def test_generate_alerts_low_voltage(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-alert-lv', low_voltage_threshold=4.0)
            AlertService.generate_alerts(d, bus_voltage=3.5, current=0.1, power=0.5)
            unresolved = AlertService.get_unresolved_count(device_id=d.id)
            assert unresolved >= 1

    def test_generate_alerts_no_duplicates(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-alert-nd', high_power_threshold=1.0)
            AlertService.generate_alerts(d, bus_voltage=5.0, current=0.1, power=2.0)
            AlertService.generate_alerts(d, bus_voltage=5.0, current=0.1, power=2.0)
            unresolved = AlertService.get_unresolved_count(device_id=d.id)
            alerts = Alert.query.filter_by(device_id=d.id, resolved_at=None).all()
            high_power_count = sum(1 for a in alerts if 'High power' in a.message)
            assert high_power_count == 1


class TestProjectService:
    def test_create_project(self, app):
        with app.app_context():
            p = ProjectService.create(name='Test Project', description='Desc')
            assert p.id is not None
            assert p.name == 'Test Project'

    def test_create_with_owner(self, app):
        with app.app_context():
            user = User.query.first()
            p = ProjectService.create(name='Owned', owner_id=user.id)
            assert p.owner_id == user.id

    def test_get_by_id(self, app):
        with app.app_context():
            p = ProjectService.create(name='Find Me')
            found = ProjectService.get_by_id(p.id)
            assert found is not None

    def test_get_by_id_nonexistent(self, app):
        with app.app_context():
            p = ProjectService.get_by_id(99999)
            assert p is None

    def test_get_all(self, app):
        with app.app_context():
            ProjectService.create(name='A')
            ProjectService.create(name='B')
            assert len(ProjectService.get_all()) >= 2

    def test_get_paginated(self, app):
        with app.app_context():
            for i in range(5):
                ProjectService.create(name=f'Project {i}')
            p = ProjectService.get_paginated(page=1, per_page=2)
            assert len(p.items) == 2
            assert p.total >= 5

    def test_update(self, app):
        with app.app_context():
            p = ProjectService.create(name='Original')
            ProjectService.update(p.id, name='Updated', description='New desc')
            assert p.name == 'Updated'
            assert p.description == 'New desc'

    def test_update_nonexistent(self, app):
        with app.app_context():
            result = ProjectService.update(99999, name='Ghost')
            assert result is None

    def test_delete(self, app):
        with app.app_context():
            p = ProjectService.create(name='To Delete')
            pid = p.id
            assert ProjectService.delete(pid) is True
            assert ProjectService.get_by_id(pid) is None

    def test_delete_nonexistent(self, app):
        with app.app_context():
            assert ProjectService.delete(99999) is False


class TestDashboardService:
    def test_get_summary_empty(self, app):
        with app.app_context():
            summary = DashboardService.get_summary()
            assert summary['online_devices'] == 0
            assert summary['offline_devices'] == 0
            assert summary['total_projects'] == 0
            assert summary['active_sessions'] == 0
            assert summary['today_energy'] == 0
            assert summary['current_power'] == 0

    def test_get_summary_with_data(self, app):
        with app.app_context():
            d = DeviceService.create('esp32-dash')
            d.last_seen = datetime.now(timezone.utc)
            s = SessionService.create(d.id, 'Dash Sess')
            SessionService.start(s.id)
            MeasurementService.create('esp32-dash', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            summary = DashboardService.get_summary()
            assert summary['online_devices'] >= 1
            assert summary['active_sessions'] >= 1
            assert summary['current_power'] > 0

    def test_get_statistics_empty(self, app):
        with app.app_context():
            stats = DashboardService.get_statistics()
            assert stats['energy']['hourly'] == []
            assert stats['energy']['daily'] == []

    def test_get_statistics_with_data(self, app):
        with app.app_context():
            MeasurementService.create('esp32-dash-stats', bus_voltage=5.0,
                                      shunt_voltage=80.0, current=200, power=1000)
            stats = DashboardService.get_statistics()
            assert stats['voltage']['avg'] > 0
