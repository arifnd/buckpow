from datetime import datetime, timezone, timedelta

from datetime import datetime, timezone, timedelta

from src.database import SessionLocal
from src.models import Device, Session, Measurement, User, Project, Alert
from src.auth.service import UserService
from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.alerts.service import AlertService
from src.projects.service import ProjectService
from src.dashboard.service import DashboardService


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





