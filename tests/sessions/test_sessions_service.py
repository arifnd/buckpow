from datetime import datetime, timezone

from datetime import datetime, timezone, timedelta


from src.database import SessionLocal


from src.auth.models import User


from src.devices.models import Device


from src.sessions.models import Session


from src.measurements.models import Measurement


from src.projects.models import Project

from src.alerts.models import Alert
from src.auth.service import UserService
from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.alerts.service import AlertService
from src.projects.service import ProjectService
from src.dashboard.service import DashboardService


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





